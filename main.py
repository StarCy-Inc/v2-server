"""
StarCy Backend Server - Real-Time Dynamic Island Updates
Monitors Google Calendar and Gmail changes in real-time
Sends push notifications to update Dynamic Island even when app is terminated

SECURITY: All endpoints require authentication via JWT tokens
"""

import os
import sys
import time
import jwt
import httpx
import asyncio
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any, List
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends, Request, Header
from pydantic import BaseModel
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import hashlib
import json

# Load environment variables first
load_dotenv()

# Import authentication middleware
from auth_middleware import (
    get_current_user,
    rate_limited_user,
    create_access_token,
    User,
    validate_device_token
)

# Import webhook handler
try:
    from webhook_handler import handle_calendar_webhook, setup_google_calendar_webhook
    WEBHOOKS_AVAILABLE = True
    print("✅ Webhook handler imported successfully")
except ImportError as e:
    print(f"⚠️ Webhook handler import failed: {e}")
    WEBHOOKS_AVAILABLE = False

# Import google_service after environment is loaded
try:
    from google_service import google_service
    GOOGLE_AVAILABLE = True
    print("✅ Google service imported successfully")
except ImportError as e:
    print(f"⚠️ Google service import failed: {e}")
    GOOGLE_AVAILABLE = False
    google_service = None

app = FastAPI(title="StarCy Backend - Real-Time Updates", version="5.0.0")

# Validate critical environment variables on startup
REQUIRED_ENV_VARS = ["APNS_KEY_ID", "APNS_TEAM_ID", "APNS_BUNDLE_ID", "JWT_SECRET"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    print(f"❌ CRITICAL: Missing environment variables: {', '.join(missing_vars)}")
    print("⚠️ Server will start but authentication and push notifications will fail")

# APNs Configuration
APNS_KEY_ID = os.getenv("APNS_KEY_ID")
APNS_TEAM_ID = os.getenv("APNS_TEAM_ID")
APNS_BUNDLE_ID = os.getenv("APNS_BUNDLE_ID")
APNS_KEY_PATH = os.getenv("APNS_KEY_PATH")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# APNs endpoints
APNS_URL = "https://api.sandbox.push.apple.com" if ENVIRONMENT == "development" else "https://api.push.apple.com"

# Store active device tokens with user credentials
active_devices: Dict[str, Dict[str, Any]] = {}

# Scheduler for periodic updates
scheduler = BackgroundScheduler()

# Real-time monitoring cache with change detection
monitoring_cache = {
    "users": {},  # user_id -> {calendar_hash, email_hash, last_data}
    "last_global_check": None
}

# Google data cache for fallback
google_data_cache: Dict[str, Any] = {
    "next_event": None,
    "unread_count": 0,
    "recent_emails": [],
    "last_refresh": None
}


DEVICE_STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "device_state.json")


def save_devices_to_disk():
    """Persist active_devices to disk so state survives server restarts"""
    try:
        serializable = {}
        for token, info in active_devices.items():
            entry = {}
            for k, v in info.items():
                if isinstance(v, datetime):
                    entry[k] = v.isoformat()
                else:
                    entry[k] = v
            serializable[token] = entry
        with open(DEVICE_STATE_FILE, "w") as f:
            json.dump(serializable, f, default=str)
        print(f"💾 Saved {len(serializable)} devices to disk")
    except Exception as e:
        print(f"❌ Error saving devices to disk: {e}")


def load_devices_from_disk():
    """Restore active_devices from disk on startup"""
    global active_devices
    try:
        if os.path.exists(DEVICE_STATE_FILE):
            with open(DEVICE_STATE_FILE, "r") as f:
                loaded = json.load(f)
            active_devices.update(loaded)
            print(f"💾 Loaded {len(loaded)} devices from disk")
        else:
            print("💾 No saved device state found — starting fresh")
    except Exception as e:
        print(f"❌ Error loading devices from disk: {e}")


class DeviceRegistration(BaseModel):
    device_token: str
    activity_id: str
    user_id: Optional[str] = None
    live_activity_push_token: Optional[str] = None  # Live Activity push token (different from device token)
    google_credentials: Optional[Dict[str, Any]] = None  # Store user's Google credentials
    zoho_credentials: Optional[Dict[str, Any]] = None    # Store user's Zoho credentials


class LiveActivityUpdate(BaseModel):
    device_token: str
    activity_id: str
    content_state: Dict[str, Any]


class SyncStateRequest(BaseModel):
    device_token: str
    calendar_events: Optional[List[Dict[str, Any]]] = None
    email_data: Optional[Dict[str, Any]] = None
    weather_data: Optional[Dict[str, Any]] = None  # {temp, condition, icon, sunrise, sunset, location}
    timezone: Optional[str] = None  # e.g. "Asia/Kolkata"
    current_island_type: Optional[str] = None
    is_subscribed: Optional[bool] = None


def generate_data_hash(data: Any) -> str:
    """Generate hash of data to detect changes"""
    return hashlib.md5(json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()


async def monitor_user_changes(user_id: str, credentials: Dict[str, Any]) -> bool:
    """Monitor a specific user's calendar and email for changes"""
    if not GOOGLE_AVAILABLE or not google_service:
        print(f"⚠️ Google service not available for user {user_id}")
        return False
        
    try:
        print(f"🔍 Monitoring changes for user {user_id}")
        
        # Get current data
        current_calendar = google_service.get_today_events_for_user(credentials)
        current_emails = google_service.get_recent_emails_for_user(credentials, max_results=5)
        
        # Generate hashes
        calendar_hash = generate_data_hash(current_calendar)
        email_hash = generate_data_hash(current_emails)
        
        # Check if this is first time monitoring this user
        if user_id not in monitoring_cache["users"]:
            monitoring_cache["users"][user_id] = {
                "calendar_hash": calendar_hash,
                "email_hash": email_hash,
                "last_calendar_data": current_calendar,
                "last_email_data": current_emails,
                "last_check": datetime.now()
            }
            print(f"✅ Initial monitoring setup for user {user_id}")
            return False  # No changes on first setup
        
        user_cache = monitoring_cache["users"][user_id]
        changes_detected = False
        
        # Check for calendar changes
        if calendar_hash != user_cache["calendar_hash"]:
            print(f"📅 Calendar changes detected for user {user_id}")
            user_cache["calendar_hash"] = calendar_hash
            user_cache["last_calendar_data"] = current_calendar
            changes_detected = True
            
            # Log specific changes
            old_events = [e.get("title", "Unknown") for e in user_cache.get("last_calendar_data", [])]
            new_events = [e.get("title", "Unknown") for e in current_calendar]
            print(f"📅 Old events: {old_events}")
            print(f"📅 New events: {new_events}")
        
        # Check for email changes
        if email_hash != user_cache["email_hash"]:
            print(f"📧 Email changes detected for user {user_id}")
            user_cache["email_hash"] = email_hash
            user_cache["last_email_data"] = current_emails
            changes_detected = True
            
            # Log specific changes
            if current_emails:
                latest_email = current_emails[0]
                print(f"📧 New email from: {latest_email.get('sender', 'Unknown')}")
                print(f"📧 Subject: {latest_email.get('subject', 'No subject')}")
        
        user_cache["last_check"] = datetime.now()
        return changes_detected
        
    except Exception as e:
        print(f"❌ Error monitoring user {user_id}: {e}")
        return False


async def update_user_dynamic_island(user_id: str):
    """Update Dynamic Island for a specific user with latest data"""
    try:
        # Find devices for this user
        user_devices = [
            (token, info) for token, info in active_devices.items() 
            if info.get("user_id") == user_id
        ]
        
        if not user_devices:
            print(f"⚠️ No devices found for user {user_id}")
            return
        
        # Get latest data from cache
        user_cache = monitoring_cache["users"].get(user_id)
        if not user_cache:
            print(f"⚠️ No cache data for user {user_id}")
            return
        
        # Create updated content state
        content_state = create_content_state_from_cache(user_cache)
        
        # Update all devices for this user
        # Use live_activity_push_token if registered — required for APNs Live Activity updates
        for device_token, device_info in user_devices:
            push_token = device_info.get("live_activity_push_token", device_token)
            success = await send_live_activity_update(
                device_token=push_token,
                activity_id=device_info["activity_id"],
                content_state=content_state
            )
            
            if success:
                device_info["last_update"] = datetime.now()
                print(f"✅ Updated Dynamic Island for user {user_id} device {device_token[:8]}...")
            else:
                print(f"❌ Failed to update Dynamic Island for user {user_id} device {device_token[:8]}...")
                
    except Exception as e:
        print(f"❌ Error updating Dynamic Island for user {user_id}: {e}")


def create_content_state_from_cache(user_cache: Dict[str, Any]) -> Dict[str, Any]:
    """Create Live Activity content state from cached user data"""
    calendar_data = user_cache.get("last_calendar_data", [])
    email_data = user_cache.get("last_email_data", [])
    
    content_state = {
        "callStatus": "Ready",
        "duration": 0,
        "transcript": "",
        "isSpeaking": False,
        "companionMode": "idle",
        "currentDate": datetime.now().strftime("%a, %b %d"),
        "isGoogleConnected": True,
        "isZohoConnected": False
    }
    
    # Add next calendar event
    if calendar_data:
        next_event = calendar_data[0]  # Assuming sorted by time
        content_state.update({
            "nextEventTitle": next_event.get("title", "Event"),
            "nextEventTime": next_event.get("time", "TBD")
        })
    
    # Add email info
    if email_data:
        unread_count = len(email_data)
        top_email = email_data[0]
        content_state.update({
            "unreadEmailCount": unread_count if unread_count > 0 else None,
            "topEmailSenders": top_email.get("sender", "Unknown"),
            "topEmailSubject": top_email.get("subject", "No subject"),
            "topEmailTime": top_email.get("time", "Unknown")
        })
    
    return content_state


async def real_time_monitoring_job():
    """Main job that monitors all users for changes every 2 minutes"""
    print("🔍 Starting real-time monitoring cycle...")
    
    for user_id, user_cache in monitoring_cache["users"].items():
        try:
            # Find user credentials from active devices
            user_credentials = None
            for device_info in active_devices.values():
                if device_info.get("user_id") == user_id:
                    user_credentials = device_info.get("google_credentials")
                    break
            
            if not user_credentials:
                print(f"⚠️ No credentials found for user {user_id}")
                continue
            
            # Monitor for changes
            changes_detected = await monitor_user_changes(user_id, user_credentials)
            
            # If changes detected, update Dynamic Island immediately
            if changes_detected:
                print(f"🚨 Changes detected for user {user_id} - updating Dynamic Island")
                await update_user_dynamic_island(user_id)
            else:
                print(f"✅ No changes for user {user_id}")
                
        except Exception as e:
            print(f"❌ Error in monitoring cycle for user {user_id}: {e}")
    
    monitoring_cache["last_global_check"] = datetime.now()
    print("✅ Real-time monitoring cycle completed")


class CalendarEventRequest(BaseModel):
    device_token: str
    title: str
    datetime: str
    duration_minutes: int = 60
    location: Optional[str] = None
    description: Optional[str] = None


class CalendarEventResponse(BaseModel):
    success: bool
    message: str
    event_id: Optional[str] = None


def generate_apns_token() -> str:
    """Generate JWT token for APNs authentication"""
    # Support base64-encoded key for cloud deployment
    if os.getenv("APNS_KEY_BASE64"):
        import base64
        private_key = base64.b64decode(os.getenv("APNS_KEY_BASE64")).decode()
    else:
        with open(APNS_KEY_PATH, 'r') as f:
            private_key = f.read()
    
    headers = {
        "alg": "ES256",
        "kid": APNS_KEY_ID
    }
    
    payload = {
        "iss": APNS_TEAM_ID,
        "iat": int(time.time())
    }
    
    token = jwt.encode(payload, private_key, algorithm="ES256", headers=headers)
    return token


async def send_live_activity_update(
    device_token: str,
    activity_id: str,
    content_state: Dict[str, Any],
    event: str = "update"
) -> bool:
    """Send push notification to update Live Activity"""
    try:
        token = generate_apns_token()
        
        headers = {
            "authorization": f"bearer {token}",
            "apns-push-type": "liveactivity",
            "apns-topic": f"{APNS_BUNDLE_ID}.push-type.liveactivity",
            "apns-priority": "10"
        }
        
        payload = {
            "aps": {
                "timestamp": int(time.time()),
                "event": event,
                "content-state": content_state
            }
        }
        
        url = f"{APNS_URL}/3/device/{device_token}"

        async with httpx.AsyncClient(http2=True) as client:
            response = await client.post(url, json=payload, headers=headers, timeout=10.0)

            if response.status_code == 200:
                print(f"✅ Live Activity updated for device {device_token[:8]}...")
                return True
            elif response.status_code == 410:
                # Token is no longer valid — remove stale device
                print(f"⚠️ APNs 410: Token expired for {device_token[:8]}... — removing device")
                stale_keys = [k for k, v in active_devices.items()
                              if v.get("live_activity_push_token") == device_token or k == device_token]
                for k in stale_keys:
                    active_devices.pop(k, None)
                save_devices_to_disk()
                return False
            else:
                print(f"❌ Failed to update Live Activity: {response.status_code} - {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Error sending push notification: {e}")
        return False


def refresh_google_data():
    """Refresh Google Calendar and Gmail data"""
    if not GOOGLE_AVAILABLE or not google_service:
        print("⚠️ Google service not available - skipping data refresh")
        return
        
    try:
        print("🔄 Refreshing Google data...")
        
        # Get next calendar event
        next_event = google_service.get_next_calendar_event()
        if next_event:
            google_data_cache["next_event"] = next_event
            print(f"📅 Next event: {next_event['title']} at {next_event['time']}")
        
        # Get unread email count
        unread_count = google_service.get_unread_email_count()
        google_data_cache["unread_count"] = unread_count
        print(f"📧 Unread emails: {unread_count}")
        
        # Get recent emails
        recent_emails = google_service.get_recent_emails(max_results=3)
        google_data_cache["recent_emails"] = recent_emails
        if recent_emails:
            print(f"📬 Recent email from: {recent_emails[0]['sender']}")
        
        google_data_cache["last_refresh"] = datetime.now()
        print("✅ Google data refreshed")
        
    except Exception as e:
        print(f"❌ Error refreshing Google data: {e}")


def periodic_google_refresh_job():
    """Job that runs every 5 minutes to refresh Google data and update Live Activities"""
    refresh_google_data()
    
    # Update all active Live Activities with fresh data
    for device_token, device_info in active_devices.items():
        try:
            # Create content state with fresh Google data
            content_state = create_dashboard_content_state()

            # Use live_activity_push_token if available — required for APNs Live Activity updates
            push_token = device_info.get("live_activity_push_token", device_token)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            success = loop.run_until_complete(
                send_live_activity_update(
                    device_token=push_token,
                    activity_id=device_info["activity_id"],
                    content_state=content_state
                )
            )
            loop.close()
            
            if success:
                device_info["last_update"] = datetime.now()
                print(f"✅ Updated Live Activity for device {device_token[:8]}...")
            else:
                print(f"❌ Failed to update Live Activity for device {device_token[:8]}...")
                
        except Exception as e:
            print(f"❌ Error updating device {device_token[:8]}...: {e}")


def create_dashboard_content_state() -> Dict[str, Any]:
    """Create content state with current Google data"""
    next_event = google_data_cache.get("next_event")
    unread_count = google_data_cache.get("unread_count", 0)
    recent_emails = google_data_cache.get("recent_emails", [])
    
    content_state = {
        "callStatus": "Ready",
        "duration": 0,
        "transcript": "",
        "isSpeaking": False,
        "companionMode": "idle",
        "currentDate": datetime.now().strftime("%a, %b %d"),
        "unreadEmailCount": unread_count if unread_count > 0 else None,
        "isGoogleConnected": True,
        "isZohoConnected": False
    }
    
    # Add next event if available
    if next_event:
        content_state.update({
            "nextEventTitle": next_event["title"],
            "nextEventTime": next_event["time"]
        })
    
    # Add top email info if available
    if recent_emails:
        top_email = recent_emails[0]
        content_state.update({
            "topEmailSenders": top_email["sender"],
            "topEmailSubject": top_email["subject"],
            "topEmailTime": top_email["time"]
        })
    
    return content_state


def calculate_island_score(island_type: str, context: Dict[str, Any], device_info: Dict[str, Any]) -> tuple[float, str]:
    """
    Calculate score for an island type - matches iOS IslandIntelligenceEngine scoring
    Returns (score, reason)
    """
    import random
    
    # Base priorities (from iOS)
    base_priorities = {
        "reminder_due": 100,
        "breaking_news": 95,
        "meeting_prep": 90,
        "focus_mode": 85,
        "sunrise": 75,
        "meeting_marathon": 70,
        "dashboard": 50
    }
    
    score = float(base_priorities.get(island_type, 50))
    reason = "Base priority"
    
    current_hour = context["current_hour"]
    meetings_today = context["meetings_today"]
    next_meeting_minutes = context["next_meeting_minutes"]
    unread_count = context["unread_count"]
    is_high_email = unread_count > 20
    
    # Time periods
    is_morning = 7 <= current_hour < 10
    is_work_hours = 10 <= current_hour < 17
    is_evening = 17 <= current_hour < 21
    is_night = current_hour >= 21 or current_hour < 7
    
    # Apply island-specific scoring logic (matches iOS exactly)
    if island_type == "dashboard":
        # Boost dashboard when there's relevant data
        if meetings_today > 0:
            score += 5
            reason = "Has meetings today"
        if is_high_email:
            score += 3
            reason = "High email volume"
        
        # At night, reduce dashboard priority to allow rotation
        if is_night:
            if meetings_today > 0 or unread_count > 0:
                score = 48  # Competitive with news (52) and sun arc (45)
                reason = "Night - has useful content"
            else:
                score = 45  # Equal to sun arc when no content
                reason = "Night - minimal content"
        
        # Work hours boost
        if is_work_hours:
            score += 5
            reason = "Work hours - dashboard relevant"
    
    elif island_type == "sunrise":
        # Show sun arc at night OR sunrise in the morning
        if is_night:
            score = 47  # Competitive with dashboard (48) and news (52)
            reason = "Night mode - sun arc"
        elif is_morning:
            score += 40
            reason = "Morning - sunrise"
        else:
            score -= 100  # Don't show during day
    
    elif island_type == "focus_mode":
        # Only if it's late evening/night
        if not is_night:
            score -= 100
        else:
            reason = "Night - focus mode"
    
    elif island_type == "meeting_prep":
        # Only if meeting is soon (within 15 minutes)
        if next_meeting_minutes is None or next_meeting_minutes > 15 or next_meeting_minutes <= 0:
            score -= 100
        else:
            reason = f"Meeting in {next_meeting_minutes} min"
    
    elif island_type == "meeting_marathon":
        # Show when user has 3+ meetings today with future meetings remaining
        if meetings_today >= 3 and next_meeting_minutes is not None:
            if is_work_hours or is_evening:
                score += 20
                reason = f"Busy day - {meetings_today} meetings"
            elif is_night:
                score = 50  # Competitive with dashboard and news
                reason = "Night - meeting overview"
            else:
                score += 15
                reason = "Meeting marathon day"
        else:
            score -= 100
    
    elif island_type == "breaking_news":
        # Show news more often - during work hours, evening, and night
        if is_work_hours:
            score = 58  # Competitive with dashboard
            reason = "Work hours - breaking news"
        elif is_evening:
            score = 55
            reason = "Evening - news rotation"
        elif is_night:
            score = 52  # Higher than sun arc, competitive with dashboard
            reason = "Night - news rotation"
        elif is_morning:
            score = 60
            reason = "Morning - news briefing"
        else:
            score = 45
            reason = "News available"
    
    # Penalize recently shown islands (avoid repetition)
    last_shown = device_info.get("last_island_type")
    last_shown_time = device_info.get("last_island_shown_time")
    if last_shown == island_type and last_shown_time:
        try:
            last_time = datetime.fromisoformat(last_shown_time)
            seconds_since = (datetime.now() - last_time).total_seconds()
            if seconds_since < 90:  # 1.5 minutes
                score -= 50
                reason = "Recently shown"
        except:
            pass
    
    # Add random variation for variety (matches iOS)
    random_variation = random.uniform(-5, 5)
    score += random_variation
    
    return (max(0, score), reason)


def rotate_content_for_device(device_token: str, device_info: Dict[str, Any]):
    """
    Intelligent Dynamic Island rotation - FULL scoring system matching iOS IslandIntelligenceEngine
    Uses scoring algorithm to select best island based on context
    """
    # Use device timezone if synced, otherwise fall back to server time
    tz_name = device_info.get("timezone")
    try:
        tz = ZoneInfo(tz_name) if tz_name else None
    except Exception:
        tz = None
    now = datetime.now(tz) if tz else datetime.now()
    current_hour = now.hour
    
    # Get user data
    calendar_events = device_info.get("calendar_events", [])
    email_data = device_info.get("email_data", {})
    
    # Fallback to Google data if iOS data not available
    if not calendar_events and google_data_cache.get("next_event"):
        event = google_data_cache["next_event"]
        calendar_events = [{
            "title": event["title"],
            "time": event["time"],
            "start_date": event.get("start_date")
        }]
        print(f"📅 Using Google Calendar data: {event['title']}")
    
    if not email_data.get("unread_count") and google_data_cache.get("unread_count"):
        email_data = {
            "unread_count": google_data_cache["unread_count"],
            "recent_emails": google_data_cache.get("recent_emails", [])
        }
        print(f"📧 Using Google Gmail data: {google_data_cache['unread_count']} unread")
    
    # Calculate context
    unread_count = email_data.get("unread_count", 0)
    meetings_today = len(calendar_events)
    
    # Check if next meeting is soon
    next_meeting_minutes = None
    if calendar_events:
        next_event = calendar_events[0]
        if next_event.get("start_date"):
            try:
                if isinstance(next_event["start_date"], str):
                    start_dt = datetime.fromisoformat(next_event["start_date"].replace('Z', '+00:00'))
                else:
                    start_dt = next_event["start_date"]
                next_meeting_minutes = int((start_dt - now).total_seconds() / 60)
            except:
                pass
    
    # Build context object
    context = {
        "current_hour": current_hour,
        "meetings_today": meetings_today,
        "next_meeting_minutes": next_meeting_minutes,
        "unread_count": unread_count
    }
    
    # Score all island types
    island_types = ["dashboard", "meeting_prep", "meeting_marathon", "sunrise", "focus_mode", "breaking_news"]
    scores = []
    
    for island_type in island_types:
        score, reason = calculate_island_score(island_type, context, device_info)
        scores.append({
            "type": island_type,
            "score": score,
            "reason": reason
        })
    
    # Sort by score (highest first)
    scores.sort(key=lambda x: x["score"], reverse=True)
    
    # Log all scores for debugging
    print("🧠 Island scores:")
    for i, s in enumerate(scores[:5]):
        emoji = "🏆" if i == 0 else "  "
        print(f"{emoji} {i+1}. {s['type']}: {int(s['score'])} - {s['reason']}")
    
    # Select the best island
    best = scores[0]
    island_type = best["type"]
    
    print(f"🧠 ✅ Selected: {island_type} (score: {int(best['score'])})")
    
    # Update device info with last shown
    device_info["last_island_type"] = island_type
    device_info["last_island_shown_time"] = now.isoformat()
    device_info["last_update"] = now.isoformat()
    
    # Build content state based on selected island type
    content_state = {
        "callStatus": "Ready",
        "duration": 0,
        "transcript": f"Updated at {now.strftime('%H:%M')}",
        "isSpeaking": False,
        "companionMode": "idle",
        "isIdleMode": True,
        "isDarkMode": current_hour < 7 or current_hour >= 19,
        "currentDate": now.strftime("%a, %b %d"),
        "intelligentIslandType": island_type
    }

    # Inject real weather data from synced device state
    weather = device_info.get("weather_data")
    if weather:
        content_state.update({
            "weatherTemp": weather.get("temp"),
            "weatherCondition": weather.get("condition"),
            "weatherIcon": weather.get("icon"),
            "sunriseTime": weather.get("sunrise"),
            "sunsetTime": weather.get("sunset"),
            "locationName": weather.get("location"),
        })

    # Populate content based on island type
    if island_type == "meeting_prep":
        if calendar_events:
            next_event = calendar_events[0]
            content_state.update({
                "nextEventTitle": next_event.get("title"),
                "nextEventTime": next_event.get("time"),
                "suggestion": f"Meeting in {next_meeting_minutes} min",
                "suggestionIcon": "calendar.badge.clock"
            })
    
    elif island_type == "meeting_marathon":
        if calendar_events:
            next_event = calendar_events[0]
            content_state.update({
                "nextEventTitle": next_event.get("title"),
                "nextEventTime": next_event.get("time"),
                "suggestion": f"{meetings_today} meetings today",
                "suggestionIcon": "calendar.badge.exclamationmark"
            })
    
    elif island_type == "sunrise":
        content_state.update({
            "suggestion": "Good morning ☀️",
            "suggestionIcon": "sunrise.fill"
        })
        if calendar_events:
            next_event = calendar_events[0]
            content_state.update({
                "nextEventTitle": next_event.get("title"),
                "nextEventTime": next_event.get("time")
            })
    
    elif island_type == "focus_mode":
        content_state.update({
            "suggestion": "Focus time 🌙",
            "suggestionIcon": "moon.stars.fill"
        })
    
    elif island_type == "breaking_news":
        content_state.update({
            "suggestion": "Check latest updates",
            "suggestionIcon": "newspaper.fill"
        })
    
    else:  # dashboard
        content_state.update({
            "suggestion": "Your day at a glance",
            "suggestionIcon": "calendar"
        })
        
        if calendar_events:
            next_event = calendar_events[0]
            content_state.update({
                "nextEventTitle": next_event.get("title"),
                "nextEventTime": next_event.get("time")
            })
        
        if unread_count > 0:
            content_state["unreadEmailCount"] = unread_count
            
            recent_emails = email_data.get("recent_emails", [])
            if recent_emails:
                top_email = recent_emails[0]
                content_state.update({
                    "topEmailSenders": top_email.get("sender"),
                    "topEmailSubject": top_email.get("subject"),
                    "topEmailTime": top_email.get("time")
                })
    
    # Send update (called from a sync thread, so create a new event loop)
    push_token = device_info.get("live_activity_push_token", device_token)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(
            send_live_activity_update(
                push_token,
                device_info["activity_id"],
                content_state
            )
        )
    finally:
        loop.close()


def periodic_rotation_job():
    """Job that runs every 60 seconds to rotate content (also serves as keep-alive)"""
    print(f"🔄 Running periodic rotation at {datetime.now().strftime('%H:%M:%S')}")
    for device_token, device_info in list(active_devices.items()):
        rotate_content_for_device(device_token, device_info)


def periodic_google_refresh_job():
    """Job that runs every 5 minutes to refresh Google data"""
    refresh_google_data()


@app.on_event("startup")
async def startup_event():
    """Start the scheduler when server starts"""
    print("✅ Backend server starting...")
    print(f"🔐 JWT Secret configured: {'Yes' if os.getenv('JWT_SECRET') else 'No (INSECURE!)'}")
    print(f"🔔 APNs configured: {'Yes' if APNS_KEY_ID and APNS_TEAM_ID else 'No'}")

    # Restore device state from disk
    load_devices_from_disk()

    # Try to authenticate with Google
    if GOOGLE_AVAILABLE and google_service:
        print("🔐 Authenticating with Google...")
        if google_service.authenticate():
            print("✅ Google authentication successful")
            # Initial data fetch
            refresh_google_data()
            # Schedule Google data refresh every 5 minutes
            scheduler.add_job(periodic_google_refresh_job, 'interval', minutes=5)
            print("✅ Google data will refresh every 5 minutes")
        else:
            print("⚠️ Google authentication failed - will use data from iOS app only")
    else:
        print("⚠️ Google service not available - will use data from iOS app only")

    # Rotate content every 60 seconds (Apple rate-limits Live Activity pushes to ~1/min)
    scheduler.add_job(periodic_rotation_job, 'interval', seconds=60)

    # Real-time monitoring every 2 minutes (PRIMARY)
    # real_time_monitoring_job is async; wrap it so BackgroundScheduler (sync) can run it
    def real_time_monitoring_job_wrapper():
        asyncio.run(real_time_monitoring_job())
    scheduler.add_job(real_time_monitoring_job_wrapper, 'interval', minutes=2)

    # Persist device state every 5 minutes
    scheduler.add_job(save_devices_to_disk, 'interval', minutes=5)

    scheduler.start()
    print("✅ Scheduler started:")
    print("   - Real-time monitoring: Every 2 minutes")
    print("   - Content rotation: Every 60 seconds")
    print("   - Device state persistence: Every 5 minutes")
    print("")
    print("🚀 Server ready for connections")
    print(f"📡 Webhook endpoint: {os.getenv('WEBHOOK_URL', 'Not configured')}")


@app.on_event("shutdown")
async def shutdown_event():
    """Stop the scheduler when server shuts down"""
    save_devices_to_disk()
    scheduler.shutdown()
    print("🛑 Scheduler stopped, device state saved")


@app.get("/")
async def root():
    """Root endpoint with service info"""
    return {
        "service": "StarCy Backend - Real-Time Dynamic Island Updates",
        "version": "5.0.0",
        "status": "running",
        "active_devices": len(active_devices),
        "monitoring_users": len(monitoring_cache.get("users", {})),
        "environment": ENVIRONMENT,
        "features": [
            "Real-time calendar/email monitoring",
            "Push notifications to iOS",
            "24/7 Dynamic Island updates"
        ]
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "5.0.0",
        "active_devices": len(active_devices),
        "monitoring_users": len(monitoring_cache.get("users", {}))
    }


@app.post("/register")
async def register_device(
    registration: DeviceRegistration,
    user: User = Depends(rate_limited_user)
):
    """
    Register device for Live Activity updates with user credentials for real-time monitoring
    
    SECURITY: Requires JWT authentication
    RATE LIMIT: 10 requests per minute per user
    """
    try:
        device_token = registration.device_token
        activity_id = registration.activity_id
        user_id = user.user_id  # Use authenticated user ID
        
        # Validate device token format (basic check)
        if len(device_token) < 32:
            raise HTTPException(
                status_code=400,
                detail="Invalid device token format"
            )
        
        # Store device with user credentials for real-time monitoring
        active_devices[device_token] = {
            "activity_id": activity_id,
            "user_id": user_id,
            "live_activity_push_token": registration.live_activity_push_token,  # For APNs Live Activity updates
            "google_credentials": registration.google_credentials,
            "zoho_credentials": registration.zoho_credentials,
            "registered_at": datetime.now(),
            "last_update": None,
            "last_keepalive": None,
            "content_index": 0
        }
        
        save_devices_to_disk()

        print(f"✅ Device registered: {device_token[:8]}... for user {user_id}")
        print(f"🔍 Real-time monitoring: {'Enabled' if registration.google_credentials else 'Disabled'}")

        # Send immediate update with current data if credentials provided
        if registration.google_credentials and GOOGLE_AVAILABLE and google_service:
            try:
                # Get initial data using user's credentials
                calendar_events = google_service.get_today_events_for_user(registration.google_credentials)
                recent_emails = google_service.get_recent_emails_for_user(registration.google_credentials, max_results=3)
                
                # Create content state
                content_state = {
                    "callStatus": "Ready",
                    "duration": 0,
                    "transcript": "",
                    "isSpeaking": False,
                    "companionMode": "idle",
                    "currentDate": datetime.now().strftime("%a, %b %d"),
                    "isGoogleConnected": True,
                    "isZohoConnected": bool(registration.zoho_credentials)
                }
                
                # Add calendar data
                if calendar_events:
                    next_event = calendar_events[0]
                    content_state.update({
                        "nextEventTitle": next_event.get("title", "Event"),
                        "nextEventTime": next_event.get("time", "TBD")
                    })
                
                # Add email data
                if recent_emails:
                    unread_count = len(recent_emails)
                    top_email = recent_emails[0]
                    content_state.update({
                        "unreadEmailCount": unread_count if unread_count > 0 else None,
                        "topEmailSenders": top_email.get("sender", "Unknown"),
                        "topEmailSubject": top_email.get("subject", "No subject"),
                        "topEmailTime": top_email.get("time", "Unknown")
                    })
                
                # Send initial update
                await send_live_activity_update(device_token, activity_id, content_state)
                print(f"✅ Sent initial real-time data to device {device_token[:8]}...")
                
            except Exception as e:
                print(f"⚠️ Could not send initial data: {e}")
        
        return {
            "success": True,
            "message": f"Device registered with real-time monitoring for user {user_id}",
            "monitoring_enabled": bool(registration.google_credentials),
            "device_count": len(active_devices),
            "update_interval": "Real-time (2 minutes)"
        }
        
    except Exception as e:
        print(f"❌ Registration error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/unregister")
async def unregister_device(
    device_token: str,
    user: User = Depends(rate_limited_user)
):
    """
    Unregister a device
    
    SECURITY: Requires JWT authentication
    RATE LIMIT: 10 requests per minute per user
    """
    if device_token in active_devices:
        device_info = active_devices[device_token]
        
        # Verify device belongs to user
        if device_info["user_id"] != user.user_id:
            raise HTTPException(
                status_code=403,
                detail="You don't have permission to unregister this device"
            )
        
        del active_devices[device_token]
        save_devices_to_disk()
        print(f"📱 Device unregistered: {device_token[:8]}... by user {user.user_id}")
        return {"success": True, "message": "Device unregistered"}
    
    return {"success": False, "message": "Device not found"}


@app.post("/update")
async def update_live_activity(
    update: LiveActivityUpdate,
    user: User = Depends(rate_limited_user)
):
    """
    Manually trigger a Live Activity update
    
    SECURITY: Requires JWT authentication
    RATE LIMIT: 10 requests per minute per user
    """
    # Verify device belongs to user
    if update.device_token not in active_devices:
        raise HTTPException(status_code=404, detail="Device not registered")
    
    device_info = active_devices[update.device_token]
    if device_info["user_id"] != user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update this device"
        )
    
    success = await send_live_activity_update(
        update.device_token,
        update.activity_id,
        update.content_state
    )
    
    if success:
        return {"success": True, "message": "Live Activity updated"}
    else:
        raise HTTPException(status_code=500, detail="Failed to update Live Activity")


@app.post("/update_user_data")
async def update_user_data(
    device_token: str,
    calendar_events: Optional[List[Dict]] = None,
    email_data: Optional[Dict] = None,
    user: User = Depends(rate_limited_user)
):
    """
    Receive calendar and email data from iOS app
    
    SECURITY: Requires JWT authentication
    RATE LIMIT: 10 requests per minute per user
    """
    if device_token not in active_devices:
        raise HTTPException(status_code=404, detail="Device not registered")
    
    device_info = active_devices[device_token]
    
    # Verify device belongs to user
    if device_info["user_id"] != user.user_id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to update this device"
        )
    
    # Store calendar events
    if calendar_events:
        device_info["calendar_events"] = calendar_events
        print(f"📅 Received {len(calendar_events)} calendar events from device {device_token[:8]}...")
    
    # Store email data
    if email_data:
        device_info["email_data"] = email_data
        print(f"📧 Received email data from device {device_token[:8]}...")
    
    device_info["last_data_update"] = datetime.now().isoformat()
    
    return {"success": True, "message": "User data updated"}


@app.post("/sync_state")
async def sync_state(req: SyncStateRequest):
    """
    Receive full app state from iOS before backgrounding.
    No auth required — the iOS app calls this with its device token as identifier.
    This keeps the backend in sync so it can push accurate updates when the app is killed.
    """
    token = req.device_token
    if token not in active_devices:
        raise HTTPException(status_code=404, detail="Device not registered — call /register first")

    device_info = active_devices[token]

    if req.calendar_events is not None:
        device_info["calendar_events"] = req.calendar_events
    if req.email_data is not None:
        device_info["email_data"] = req.email_data
    if req.weather_data is not None:
        device_info["weather_data"] = req.weather_data
    if req.timezone is not None:
        device_info["timezone"] = req.timezone
    if req.current_island_type is not None:
        device_info["current_island_type"] = req.current_island_type
    if req.is_subscribed is not None:
        device_info["is_subscribed"] = req.is_subscribed

    device_info["last_sync"] = datetime.now().isoformat()
    save_devices_to_disk()

    print(f"🔄 Full state synced for device {token[:8]}... "
          f"(tz={req.timezone}, island={req.current_island_type}, "
          f"events={len(req.calendar_events) if req.calendar_events else 0}, "
          f"weather={'yes' if req.weather_data else 'no'})")

    return {"success": True, "message": "State synced"}


@app.get("/devices")
async def list_devices():
    """List all registered devices"""
    return {
        "count": len(active_devices),
        "devices": [
            {
                "device_token": token[:8] + "...",
                "activity_id": info["activity_id"],
                "registered_at": info["registered_at"],
                "last_update": info.get("last_update"),
                "last_data_update": info.get("last_data_update"),
                "has_calendar_data": "calendar_events" in info,
                "has_email_data": "email_data" in info
            }
            for token, info in active_devices.items()
        ]
    }


@app.post("/vapi/create_calendar_event")
async def create_calendar_event(request: CalendarEventRequest) -> CalendarEventResponse:
    """
    Handle calendar event creation request from Vapi
    
    Args:
        request: CalendarEventRequest containing:
            - device_token: User's device token to route request
            - title: Event title
            - datetime: ISO 8601 datetime string
            - duration_minutes: Event duration in minutes (default: 60)
            - location: Optional event location
            - description: Optional event description
    
    Returns:
        CalendarEventResponse with success status, message, and event_id if successful
    
    Validates:
        - Requirements 7.2: Request validation
        - Requirements 7.4: Response format
        - Requirements 9.1: Past date validation
        - Requirements 9.2: Duration bounds validation
    """
    # Validate device token exists
    if request.device_token not in active_devices:
        return CalendarEventResponse(
            success=False,
            message="Device not registered. Please ensure the app is connected."
        )
    
    # Validate datetime format (ISO 8601)
    try:
        event_datetime = datetime.fromisoformat(request.datetime.replace('Z', '+00:00'))
    except (ValueError, AttributeError) as e:
        return CalendarEventResponse(
            success=False,
            message=f"Invalid datetime format. Please use ISO 8601 format (e.g., '2024-12-10T14:00:00Z'). Error: {str(e)}"
        )
    
    # Validate datetime is not in the past (Requirement 9.1)
    now = datetime.now(event_datetime.tzinfo) if event_datetime.tzinfo else datetime.now()
    if event_datetime < now:
        # Allow events in the past with a warning, but within 5 minutes (user might be creating an event that just started)
        time_diff = (now - event_datetime).total_seconds() / 60
        if time_diff > 5:
            return CalendarEventResponse(
                success=False,
                message=f"Cannot create events in the past. The specified time was {int(time_diff)} minutes ago."
            )
    
    # Validate duration bounds: 5 minutes to 24 hours (Requirement 9.2)
    if request.duration_minutes < 5:
        return CalendarEventResponse(
            success=False,
            message="Event duration must be at least 5 minutes."
        )
    
    if request.duration_minutes > 1440:  # 24 hours = 1440 minutes
        return CalendarEventResponse(
            success=False,
            message="Event duration cannot exceed 24 hours (1440 minutes)."
        )
    
    # Validate required fields
    if not request.title or not request.title.strip():
        return CalendarEventResponse(
            success=False,
            message="Event title is required."
        )
    
    # TODO: Forward request to iOS app via notification/webhook
    # For now, return a placeholder response indicating the endpoint is working
    # This will be implemented in Task 7
    
    print(f"📅 Calendar event creation request received:")
    print(f"   Device: {request.device_token[:8]}...")
    print(f"   Title: {request.title}")
    print(f"   DateTime: {request.datetime}")
    print(f"   Duration: {request.duration_minutes} minutes")
    if request.location:
        print(f"   Location: {request.location}")
    if request.description:
        print(f"   Description: {request.description}")
    
    # Placeholder response - will be replaced with actual iOS integration in Task 7
    return CalendarEventResponse(
        success=True,
        message=f"Calendar event '{request.title}' validated and ready for creation.",
        event_id="pending_ios_integration"
    )


@app.post("/webhooks/google/calendar")
async def google_calendar_webhook(
    request: Request,
    x_goog_channel_id: str = Header(None),
    x_goog_resource_state: str = Header(None),
    x_goog_resource_id: str = Header(None)
):
    """
    Handle Google Calendar push notifications for instant updates
    
    This endpoint receives notifications when a user's calendar changes,
    allowing for real-time Dynamic Island updates without polling.
    
    Headers:
        x-goog-channel-id: Channel ID from Google
        x-goog-resource-state: Resource state (sync, exists, not_exists)
        x-goog-resource-id: Resource ID
    
    Returns:
        Success response
    """
    if not WEBHOOKS_AVAILABLE:
        raise HTTPException(
            status_code=501,
            detail="Webhooks not configured"
        )
    
    return await handle_calendar_webhook(
        request,
        x_goog_channel_id,
        x_goog_resource_state,
        x_goog_resource_id
    )


if __name__ == "__main__":
    import uvicorn
    # Use PORT from Railway/Render, or SERVER_PORT for local development
    port = int(os.getenv("PORT", os.getenv("SERVER_PORT", 8000)))
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    uvicorn.run(app, host=host, port=port)
