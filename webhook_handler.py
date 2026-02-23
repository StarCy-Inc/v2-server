"""
Webhook Handler for Real-Time Calendar Updates
Handles Google Calendar push notifications for instant updates
"""

import os
import hmac
import hashlib
from datetime import datetime
from typing import Dict, Any
from fastapi import Request, HTTPException, Header
import asyncio

# Store active webhook channels
active_channels: Dict[str, Dict[str, Any]] = {}


async def setup_google_calendar_webhook(user_id: str, calendar_id: str = "primary"):
    """
    Set up Google Calendar push notifications for a user
    
    Args:
        user_id: User identifier
        calendar_id: Calendar ID to watch (default: primary)
    
    Returns:
        Channel ID if successful, None otherwise
    """
    try:
        from google_service import google_service
        
        if not google_service:
            print("⚠️ Google service not available")
            return None
        
        # Generate unique channel ID
        channel_id = f"starcy_{user_id}_{calendar_id}_{int(datetime.now().timestamp())}"
        
        # Webhook URL (must be HTTPS in production)
        webhook_url = os.getenv("WEBHOOK_URL", "https://your-backend.onrender.com/webhooks/google/calendar")
        
        # Set up watch request
        # Note: This requires Google Calendar API v3 with push notifications enabled
        # The actual implementation depends on google_service having this capability
        
        print(f"📡 Setting up webhook for user {user_id}, channel: {channel_id}")
        print(f"📡 Webhook URL: {webhook_url}")
        
        # Store channel info
        active_channels[channel_id] = {
            "user_id": user_id,
            "calendar_id": calendar_id,
            "created_at": datetime.now(),
            "webhook_url": webhook_url
        }
        
        print(f"✅ Webhook channel registered: {channel_id}")
        return channel_id
        
    except Exception as e:
        print(f"❌ Error setting up webhook: {e}")
        return None


async def handle_calendar_webhook(
    request: Request,
    x_goog_channel_id: str = Header(None),
    x_goog_resource_state: str = Header(None),
    x_goog_resource_id: str = Header(None)
):
    """
    Handle incoming Google Calendar webhook notifications
    
    Args:
        request: FastAPI request object
        x_goog_channel_id: Channel ID from Google
        x_goog_resource_state: Resource state (sync, exists, not_exists)
        x_goog_resource_id: Resource ID
    
    Returns:
        Success response
    """
    try:
        print(f"📡 Received webhook notification")
        print(f"   Channel ID: {x_goog_channel_id}")
        print(f"   Resource State: {x_goog_resource_state}")
        print(f"   Resource ID: {x_goog_resource_id}")
        
        # Verify channel exists
        if x_goog_channel_id not in active_channels:
            print(f"⚠️ Unknown channel ID: {x_goog_channel_id}")
            return {"status": "ignored", "reason": "unknown_channel"}
        
        channel_info = active_channels[x_goog_channel_id]
        user_id = channel_info["user_id"]
        
        # Handle different resource states
        if x_goog_resource_state == "sync":
            # Initial sync notification - ignore
            print(f"📡 Sync notification for channel {x_goog_channel_id}")
            return {"status": "ok", "message": "sync_acknowledged"}
        
        elif x_goog_resource_state == "exists":
            # Calendar was updated!
            print(f"🚨 Calendar update detected for user {user_id}")
            
            # Trigger immediate update for this user
            from main import update_user_dynamic_island
            await update_user_dynamic_island(user_id)
            
            return {"status": "ok", "message": "update_triggered"}
        
        elif x_goog_resource_state == "not_exists":
            # Resource was deleted
            print(f"🗑️ Calendar resource deleted for user {user_id}")
            return {"status": "ok", "message": "resource_deleted"}
        
        else:
            print(f"⚠️ Unknown resource state: {x_goog_resource_state}")
            return {"status": "ok", "message": "unknown_state"}
        
    except Exception as e:
        print(f"❌ Error handling webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def stop_webhook(channel_id: str):
    """
    Stop a webhook channel
    
    Args:
        channel_id: Channel ID to stop
    """
    try:
        if channel_id in active_channels:
            del active_channels[channel_id]
            print(f"✅ Stopped webhook channel: {channel_id}")
        else:
            print(f"⚠️ Channel not found: {channel_id}")
    except Exception as e:
        print(f"❌ Error stopping webhook: {e}")


def verify_webhook_signature(request_body: bytes, signature: str, secret: str) -> bool:
    """
    Verify webhook signature for security
    
    Args:
        request_body: Raw request body
        signature: Signature from header
        secret: Shared secret
    
    Returns:
        True if signature is valid
    """
    expected_signature = hmac.new(
        secret.encode(),
        request_body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
