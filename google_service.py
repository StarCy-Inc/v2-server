"""
Google Calendar and Gmail Service
Fetches real calendar events and email data for Dynamic Island
"""

import os
import pickle
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Scopes for Google APIs
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/gmail.readonly'
]


class GoogleService:
    """Service to fetch Google Calendar and Gmail data"""
    
    def __init__(self):
        self.creds: Optional[Credentials] = None
        self.calendar_service = None
        self.gmail_service = None
        self.credentials_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "./credentials.json")
        self.token_path = os.getenv("GOOGLE_TOKEN_PATH", "./token.json")
        
    def authenticate(self) -> bool:
        """Authenticate with Google APIs"""
        try:
            # Check if we have saved credentials
            if os.path.exists(self.token_path):
                with open(self.token_path, 'rb') as token:
                    self.creds = pickle.load(token)
            
            # If credentials are invalid or don't exist, get new ones
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    print("🔄 Refreshing Google credentials...")
                    self.creds.refresh(Request())
                else:
                    # Check for base64-encoded credentials (for cloud deployment)
                    credentials_content = None
                    if os.getenv("GOOGLE_CREDENTIALS_BASE64"):
                        import base64
                        import json
                        import tempfile
                        print("🔐 Using base64-encoded Google credentials...")
                        credentials_content = base64.b64decode(os.getenv("GOOGLE_CREDENTIALS_BASE64")).decode()
                        # Create temporary file for credentials
                        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
                            f.write(credentials_content)
                            temp_creds_path = f.name
                        self.credentials_path = temp_creds_path
                    elif not os.path.exists(self.credentials_path):
                        print("⚠️ Google credentials.json not found - skipping Google integration")
                        return False
                    
                    print("🔐 Starting Google OAuth flow...")
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_path, SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)
                
                # Save credentials for next time
                with open(self.token_path, 'wb') as token:
                    pickle.dump(self.creds, token)
            
            # Build services
            self.calendar_service = build('calendar', 'v3', credentials=self.creds)
            self.gmail_service = build('gmail', 'v1', credentials=self.creds)
            
            print("✅ Google services authenticated successfully")
            return True
            
        except Exception as e:
            print(f"❌ Google authentication failed: {e}")
            return False
    
    def get_next_calendar_event(self) -> Optional[Dict[str, Any]]:
        """Get the next upcoming calendar event (excluding all-day events)"""
        if not self.calendar_service:
            return None
        
        try:
            now = datetime.utcnow().isoformat() + 'Z'
            
            # Get events from primary calendar (get more to filter all-day events)
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=now,
                maxResults=10,  # Get more events to filter all-day
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            if not events:
                return None
            
            # Find first non-all-day event
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                
                # Skip all-day events (they only have 'date', not 'dateTime')
                if 'T' not in start:
                    continue
                
                summary = event.get('summary', 'Untitled Event')
                
                # Parse datetime event
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                time_str = start_dt.strftime('%I:%M %p').lstrip('0')
                
                # Get attendees
                attendees = event.get('attendees', [])
                attendee_names = [a.get('displayName', a.get('email', '').split('@')[0]) 
                                for a in attendees if not a.get('self', False)]
                attendees_str = ', '.join(attendee_names[:3]) if attendee_names else None
                
                return {
                    'title': summary,
                    'time': time_str,
                    'start_date': start_dt,
                    'is_all_day': False,
                    'attendees': attendees_str
                }
            
            # No non-all-day events found
            return None
            
        except Exception as e:
            print(f"❌ Error fetching calendar events: {e}")
            return None
    
    def get_todays_events(self) -> List[Dict[str, Any]]:
        """Get all non-all-day events for today"""
        if not self.calendar_service:
            return []
        
        try:
            # Get start and end of today
            now = datetime.now()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            time_min = start_of_day.isoformat() + 'Z'
            time_max = end_of_day.isoformat() + 'Z'
            
            events_result = self.calendar_service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            result = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                
                # Skip all-day events
                if 'T' not in start:
                    continue
                
                summary = event.get('summary', 'Untitled Event')
                start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                time_str = start_dt.strftime('%I:%M %p').lstrip('0')
                
                attendees = event.get('attendees', [])
                attendee_names = [a.get('displayName', a.get('email', '').split('@')[0]) 
                                for a in attendees if not a.get('self', False)]
                attendees_str = ', '.join(attendee_names[:3]) if attendee_names else None
                
                result.append({
                    'title': summary,
                    'time': time_str,
                    'start_date': start_dt,
                    'is_all_day': False,
                    'attendees': attendees_str
                })
            
            return result
            
        except Exception as e:
            print(f"❌ Error fetching today's events: {e}")
            return []
    
    def get_unread_email_count(self) -> int:
        """Get count of unread emails"""
        if not self.gmail_service:
            return 0
        
        try:
            results = self.gmail_service.users().messages().list(
                userId='me',
                q='is:unread in:inbox',
                maxResults=100
            ).execute()
            
            messages = results.get('messages', [])
            return len(messages)
            
        except Exception as e:
            print(f"❌ Error fetching email count: {e}")
            return 0
    
    def get_recent_emails(self, max_results: int = 3) -> List[Dict[str, Any]]:
        """Get recent unread emails"""
        if not self.gmail_service:
            return []
        
        try:
            results = self.gmail_service.users().messages().list(
                userId='me',
                q='is:unread in:inbox',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            emails = []
            for msg in messages:
                msg_data = self.gmail_service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = msg_data.get('payload', {}).get('headers', [])
                
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Extract sender name
                if '<' in sender:
                    sender = sender.split('<')[0].strip().strip('"')
                
                # Parse date
                try:
                    from email.utils import parsedate_to_datetime
                    date_dt = parsedate_to_datetime(date_str)
                    time_str = date_dt.strftime('%I:%M %p').lstrip('0')
                except:
                    time_str = 'Recently'
                
                emails.append({
                    'sender': sender,
                    'subject': subject,
                    'time': time_str
                })
            
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return []


    def get_today_events_for_user(self, user_credentials: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get today's calendar events for a specific user"""
        try:
            # Create credentials from user's access token
            creds = Credentials(token=user_credentials.get("access_token"))
            
            # Build calendar service for this user
            calendar_service = build('calendar', 'v3', credentials=creds)
            
            # Get today's events
            now = datetime.utcnow()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            events_result = calendar_service.events().list(
                calendarId='primary',
                timeMin=start_of_day.isoformat() + 'Z',
                timeMax=end_of_day.isoformat() + 'Z',
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            
            formatted_events = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                
                # Parse start time
                if 'T' in start:  # DateTime format
                    start_dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                    time_str = start_dt.strftime("%I:%M %p")
                    is_all_day = False
                else:  # Date format (all-day event)
                    start_dt = datetime.fromisoformat(start)
                    time_str = "All Day"
                    is_all_day = True
                
                formatted_events.append({
                    "title": event.get('summary', 'No Title'),
                    "time": time_str,
                    "start_datetime": start_dt,
                    "is_all_day": is_all_day,
                    "attendees": self._get_attendee_names(event.get('attendees', []))
                })
            
            print(f"📅 Found {len(formatted_events)} events for user")
            return formatted_events
            
        except Exception as e:
            print(f"❌ Error fetching user calendar events: {e}")
            return []
    
    def get_recent_emails_for_user(self, user_credentials: Dict[str, Any], max_results: int = 5) -> List[Dict[str, Any]]:
        """Get recent emails for a specific user"""
        try:
            # Create credentials from user's access token
            creds = Credentials(token=user_credentials.get("access_token"))
            
            # Build Gmail service for this user
            gmail_service = build('gmail', 'v1', credentials=creds)
            
            # Get recent unread emails
            results = gmail_service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            
            formatted_emails = []
            for message in messages:
                msg = gmail_service.users().messages().get(
                    userId='me',
                    id=message['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()
                
                headers = msg['payload'].get('headers', [])
                
                # Extract email details
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Parse sender name (remove email address)
                if '<' in sender:
                    sender = sender.split('<')[0].strip().strip('"')
                
                # Parse date
                try:
                    from email.utils import parsedate_to_datetime
                    date_dt = parsedate_to_datetime(date_str)
                    time_str = date_dt.strftime("%I:%M %p")
                except:
                    time_str = "Unknown"
                
                formatted_emails.append({
                    "sender": sender,
                    "subject": subject,
                    "time": time_str,
                    "date": date_dt if 'date_dt' in locals() else None
                })
            
            print(f"📧 Found {len(formatted_emails)} unread emails for user")
            return formatted_emails
            
        except Exception as e:
            print(f"❌ Error fetching user emails: {e}")
            return []
    
    def _get_attendee_names(self, attendees: List[Dict]) -> Optional[str]:
        """Extract attendee names from calendar event"""
        if not attendees:
            return None
        
        names = []
        for attendee in attendees[:3]:  # Limit to first 3 attendees
            email = attendee.get('email', '')
            display_name = attendee.get('displayName')
            
            if display_name:
                names.append(display_name)
            elif email:
                # Extract name from email
                name = email.split('@')[0].replace('.', ' ').title()
                names.append(name)
        
        return ', '.join(names) if names else None


# Global instance
google_service = GoogleService()