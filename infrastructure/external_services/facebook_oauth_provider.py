"""Facebook OAuth provider implementation."""

import httpx
from urllib.parse import urlencode
from typing import Dict, Any

from domain.interfaces import IOAuthProvider
from config.settings import settings


class FacebookOAuthProvider(IOAuthProvider):
    """Facebook OAuth provider implementation."""
    
    def __init__(self):
        self.app_id = settings.FACEBOOK_APP_ID
        self.app_secret = settings.FACEBOOK_APP_SECRET
        self.redirect_uri = settings.FACEBOOK_REDIRECT_URI
    
    def get_authorization_url(self) -> str:
        """Get Facebook OAuth authorization URL."""
        base_url = "https://www.facebook.com/v21.0/dialog/oauth"
        
        params = {
            "client_id": self.app_id,
            "redirect_uri": self.redirect_uri,
            "scope": "email public_profile",
            "response_type": "code",
            "state": "facebook_oauth_security_state"
        }
        
        return f"{base_url}?{urlencode(params)}"
    
    async def exchange_code_for_user_info(self, auth_code: str) -> Dict[str, Any]:
        """Exchange authorization code for user information."""
        if not self.app_id or not self.app_secret:
            raise ValueError("Facebook OAuth not configured")
        
        async with httpx.AsyncClient() as client:
            # Exchange code for access token
            token_response = await client.post(
                "https://graph.facebook.com/v21.0/oauth/access_token",
                params={
                    "client_id": self.app_id,
                    "client_secret": self.app_secret,
                    "redirect_uri": self.redirect_uri,
                    "code": auth_code,
                }
            )
            
            if token_response.status_code != 200:
                error_data = token_response.json()
                error_detail = "Failed to exchange code for token"
                if 'error' in error_data:
                    error_detail = f"Facebook OAuth error: {error_data['error']['message']}"
                raise ValueError(error_detail)
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            if not access_token:
                raise ValueError("No access token received from Facebook")
            
            # Get user info from Facebook
            user_response = await client.get(
                "https://graph.facebook.com/me",
                params={
                    "access_token": access_token,
                    "fields": "id,email,first_name,last_name,verified"
                }
            )
            
            if user_response.status_code != 200:
                raise ValueError("Failed to get user info from Facebook")
            
            user_info = user_response.json()
            
            return {
                "id": user_info.get('id'),
                "email": user_info.get('email'),
                "first_name": user_info.get('first_name'),
                "last_name": user_info.get('last_name'),
                "email_verified": user_info.get('verified', False)
            }
    
    def get_provider_name(self) -> str:
        """Get provider name."""
        return "facebook"