"""
Gmail Service
=============

Service layer for Gmail API operations.
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import base64
import hashlib
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from app.config.settings import settings

logger = logging.getLogger(__name__)

class GmailService:
    """Service for handling Gmail API operations."""
    
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    
    def __init__(self):
        self.service = None
        self.credentials = None
    
    async def authenticate_user(self, auth_code: str) -> Dict[str, Any]:
        """Authenticate user with Google OAuth."""
        try:
            # Exchange auth code for credentials
            flow = InstalledAppFlow.from_client_config(
                {
                    "installed": {
                        "client_id": settings.google_client_id,
                        "client_secret": settings.google_client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [settings.google_redirect_uri]
                    }
                },
                self.SCOPES
            )
            
            flow.fetch_token(code=auth_code)
            credentials = flow.credentials
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=credentials)
            
            # Get user profile
            profile = self.service.users().getProfile(userId='me').execute()
            
            return {
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes,
                "email": profile['emailAddress'],
                "name": profile.get('name', ''),
                "expires_at": credentials.expiry.isoformat() if credentials.expiry else None
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            raise
    
    def _create_credentials_from_dict(self, creds_dict: Dict[str, Any]) -> Credentials:
        """Create Credentials object from dictionary."""
        return Credentials(
            token=creds_dict['access_token'],
            refresh_token=creds_dict['refresh_token'],
            token_uri=creds_dict['token_uri'],
            client_id=creds_dict['client_id'],
            client_secret=creds_dict['client_secret'],
            scopes=creds_dict['scopes']
        )
    
    async def fetch_emails(self, user_id: str, credentials_dict: Dict[str, Any], 
                          max_results: int = 500, query: str = None) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail API."""
        try:
            # Create credentials
            credentials = self._create_credentials_from_dict(credentials_dict)
            
            # Refresh token if needed
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            # Build service
            self.service = build('gmail', 'v1', credentials=credentials)
            
            # Build query
            if not query:
                # Default query: emails from last 6 months
                six_months_ago = datetime.now() - timedelta(days=180)
                query = f"after:{six_months_ago.strftime('%Y/%m/%d')}"
            
            emails = []
            page_token = None
            
            while len(emails) < max_results:
                try:
                    # Get message list
                    response = self.service.users().messages().list(
                        userId='me',
                        q=query,
                        maxResults=min(100, max_results - len(emails)),
                        pageToken=page_token
                    ).execute()
                    
                    messages = response.get('messages', [])
                    if not messages:
                        break
                    
                    # Get full message details
                    for message in messages:
                        try:
                            msg = self.service.users().messages().get(
                                userId='me',
                                id=message['id'],
                                format='full'
                            ).execute()
                            
                            # Extract email data
                            email_data = self._extract_email_data(msg)
                            if email_data:
                                emails.append(email_data)
                            
                            # Rate limiting
                            await asyncio.sleep(0.1)
                            
                        except HttpError as e:
                            if e.resp.status == 404:
                                logger.warning(f"Message {message['id']} not found")
                                continue
                            else:
                                raise
                    
                    page_token = response.get('nextPageToken')
                    if not page_token:
                        break
                        
                except HttpError as e:
                    if e.resp.status == 429:  # Rate limit exceeded
                        logger.warning("Rate limit exceeded, waiting...")
                        await asyncio.sleep(60)
                        continue
                    else:
                        raise
            
            logger.info(f"Fetched {len(emails)} emails for user {user_id}")
            return emails
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            raise
    
    def _extract_email_data(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract relevant data from Gmail message."""
        try:
            # Get headers
            headers = message.get('payload', {}).get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
            from_header = next((h['value'] for h in headers if h['name'] == 'From'), '')
            to_header = next((h['value'] for h in headers if h['name'] == 'To'), '')
            date_header = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Get body
            body = self._get_message_body(message.get('payload', {}))
            
            # Generate hash
            body_hash = hashlib.sha256(body.encode('utf-8')).hexdigest()
            
            # Parse date
            try:
                received_date = datetime.fromisoformat(date_header.replace(' ', 'T'))
            except:
                received_date = datetime.utcnow()
            
            return {
                'gmail_id': message['id'],
                'thread_id': message.get('threadId', ''),
                'subject': subject,
                'from_address': from_header,
                'to_address': to_header,
                'received_date': received_date,
                'body': body,
                'body_hash': body_hash,
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', []),
                'internal_date': message.get('internalDate', ''),
                'size_estimate': message.get('sizeEstimate', 0)
            }
            
        except Exception as e:
            logger.error(f"Error extracting email data: {e}")
            return None
    
    def _get_message_body(self, payload: Dict[str, Any]) -> str:
        """Extract message body from payload."""
        try:
            if 'parts' in payload:
                # Multipart message
                body = ""
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain':
                        data = part.get('body', {}).get('data', '')
                        if data:
                            body += base64.urlsafe_b64decode(data).decode('utf-8')
                    elif part.get('mimeType') == 'text/html':
                        # Fallback to HTML if no plain text
                        if not body:
                            data = part.get('body', {}).get('data', '')
                            if data:
                                body += base64.urlsafe_b64decode(data).decode('utf-8')
                return body
            else:
                # Simple message
                data = payload.get('body', {}).get('data', '')
                if data:
                    return base64.urlsafe_b64decode(data).decode('utf-8')
                return ""
                
        except Exception as e:
            logger.error(f"Error getting message body: {e}")
            return ""
    
    async def get_user_profile(self, credentials_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Get user profile information."""
        try:
            credentials = self._create_credentials_from_dict(credentials_dict)
            
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            self.service = build('gmail', 'v1', credentials=credentials)
            profile = self.service.users().getProfile(userId='me').execute()
            
            return {
                'email': profile['emailAddress'],
                'name': profile.get('name', ''),
                'messages_total': profile.get('messagesTotal', 0),
                'threads_total': profile.get('threadsTotal', 0),
                'history_id': profile.get('historyId', '')
            }
            
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            raise
    
    async def check_quota(self, credentials_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Check Gmail API quota usage."""
        try:
            credentials = self._create_credentials_from_dict(credentials_dict)
            
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            
            self.service = build('gmail', 'v1', credentials=credentials)
            
            # Get quota info (this is a simplified version)
            # In production, you'd want to track quota usage more carefully
            return {
                'quota_limit': settings.gmail_api_quota_limit,
                'quota_used': 0,  # Would need to track this
                'quota_remaining': settings.gmail_api_quota_limit
            }
            
        except Exception as e:
            logger.error(f"Error checking quota: {e}")
            raise

# Global Gmail service instance
gmail_service = GmailService() 