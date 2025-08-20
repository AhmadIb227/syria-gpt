"""Google OAuth provider implementation."""

import httpx
from urllib.parse import urlencode
from typing import Dict, Any
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from domain.interfaces import IOAuthProvider
from config.settings import settings


class GoogleOAuthProvider(IOAuthProvider):
    """Google OAuth provider implementation."""
    
    def __init__(self):
        self.client_id = settings.GOOGLE_CLIENT_ID
        self.client_secret = settings.GOOGLE_CLIENT_SECRET
        self.redirect_uri = settings.GOOGLE_REDIRECT_URI
    
    def get_authorization_url(self) -> str:
        """Get Google OAuth authorization URL."""
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid email profile",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "state": "google_oauth_security_state"
        }
        
        return f"{base_url}?{urlencode(params)}"
    
    async def exchange_code_for_user_info(self, auth_code: str) -> Dict[str, Any]:
        """Exchange authorization code for user information."""
        if not self.client_id or not self.client_secret:
            raise ValueError("Google OAuth not configured")
        
        async with httpx.AsyncClient() as client:
            # Exchange code for tokens
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "code": auth_code,
                    "grant_type": "authorization_code",
                    "redirect_uri": self.redirect_uri,
                }
            )
            
            if token_response.status_code != 200:
                error_data = token_response.json()
                error_detail = error_data.get('error', 'Unknown error')
                if 'error_description' in error_data:
                    error_detail += f": {error_data['error_description']}"
                raise ValueError(f"Google OAuth error: {error_detail}")
            
            token_data = token_response.json()
            id_token_str = token_data.get("id_token")
            
            if not id_token_str:
                raise ValueError("No ID token received from Google")
            
            # Verify and decode ID token
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                google_requests.Request(), 
                self.client_id
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid token issuer')
            
            return {
                "id": idinfo.get('sub'),
                "email": idinfo.get('email'),
                "first_name": idinfo.get('given_name'),
                "last_name": idinfo.get('family_name'),
                "email_verified": idinfo.get('email_verified', False)
            }
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "google"