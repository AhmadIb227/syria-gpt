"""Application service for authentication - orchestrates use cases."""

from typing import Dict, Any
from uuid import UUID

from domain.use_cases import AuthUseCases
from infrastructure.external_services import GoogleOAuthProvider, FacebookOAuthProvider


class AuthApplicationService:
    """Application service that orchestrates authentication use cases."""

    def __init__(
        self,
        auth_use_cases: AuthUseCases,
        google_provider: GoogleOAuthProvider = None,
        facebook_provider: FacebookOAuthProvider = None,
    ):
        self.auth_use_cases = auth_use_cases
        self.google_provider = google_provider or GoogleOAuthProvider()
        self.facebook_provider = facebook_provider or FacebookOAuthProvider()

    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Register a new user."""
        return await self.auth_use_cases.register_user(user_data)

    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with email and password."""
        return await self.auth_use_cases.authenticate_user(email, password)

    def get_google_auth_url(self) -> Dict[str, Any]:
        """Get Google OAuth authorization URL."""
        auth_url = self.google_provider.get_authorization_url()
        return {"auth_url": auth_url, "provider": "google"}

    def get_facebook_auth_url(self) -> Dict[str, Any]:
        """Get Facebook OAuth authorization URL."""
        auth_url = self.facebook_provider.get_authorization_url()
        return {"auth_url": auth_url, "provider": "facebook"}

    async def authenticate_with_google(self, auth_code: str) -> Dict[str, Any]:
        """Authenticate user with Google OAuth."""
        return await self.auth_use_cases.authenticate_with_oauth(self.google_provider, auth_code)

    async def authenticate_with_facebook(self, auth_code: str) -> Dict[str, Any]:
        """Authenticate user with Facebook OAuth."""
        return await self.auth_use_cases.authenticate_with_oauth(self.facebook_provider, auth_code)

    async def verify_email(self, token: str) -> Dict[str, str]:
        """Verify user email with token."""
        return await self.auth_use_cases.verify_email(token)

    async def change_password(
        self, user_id: UUID, current_password: str, new_password: str
    ) -> Dict[str, str]:
        """Change user password."""
        return await self.auth_use_cases.change_password(user_id, current_password, new_password)

    async def request_password_reset(self, email: str) -> Dict[str, str]:
        """Request password reset link via email."""
        return await self.auth_use_cases.request_password_reset(email)

    async def confirm_password_reset(self, token: str, new_password: str) -> Dict[str, str]:
        """Confirm password reset using token and new password."""
        return await self.auth_use_cases.confirm_password_reset(token, new_password)

    async def sign_out_user(self, user_id: UUID, refresh_token: str) -> Dict[str, str]:
        """Sign out user from a single device/session."""
        return await self.auth_use_cases.sign_out_user(user_id, refresh_token)

    async def sign_out_all_devices(self, user_id: UUID) -> Dict[str, str]:
        """Sign out user from all devices by incrementing token_version."""
        return await self.auth_use_cases.sign_out_all_devices(user_id)

    async def verify_2fa_code(self, tfa_token: str, code: str) -> Dict[str, Any]:
        """Verify the 2FA code and return final tokens."""
        return await self.auth_use_cases.verify_2fa_code(tfa_token, code)
