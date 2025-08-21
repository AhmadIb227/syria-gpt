"""Authentication use cases - business logic implementation."""

import random
import string
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime, timedelta

from domain.entities import User, UserStatus
from domain.interfaces import IUserRepository, IOAuthProvider, ITwoFactorAuthRepository
from infrastructure.services.password_service import PasswordService
from infrastructure.services.token_service import TokenService
from infrastructure.services.email_service import EmailService


class AuthUseCases:
    """Authentication use cases implementing business logic."""
    
    def __init__(
        self,
        user_repository: IUserRepository,
        password_service: PasswordService,
        token_service: TokenService,
        email_service: EmailService,
        two_factor_auth_repository: ITwoFactorAuthRepository
    ):
        self.user_repository = user_repository
        self.password_service = password_service
        self.token_service = token_service
        self.email_service = email_service
        self.two_factor_auth_repository = two_factor_auth_repository
    
    async def register_user(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Register a new user."""
        # Validate email uniqueness
        if await self.user_repository.email_exists(user_data["email"]):
            raise ValueError("Email already registered")
        
        # Validate phone uniqueness if provided
        if user_data.get("phone_number"):
            if await self.user_repository.phone_exists(user_data["phone_number"]):
                raise ValueError("Phone number already registered")
        
        # Hash password
        if "password" in user_data:
            user_data["password_hash"] = self.password_service.hash_password(user_data.pop("password"))
        
        # Set default values
        user_data.setdefault("status", UserStatus.PENDING_VERIFICATION.value)
        user_data.setdefault("is_active", True)
        
        # Create user
        user = await self.user_repository.create(user_data)
        
        # Send verification email if email provided
        if user.email and not user.is_email_verified:
            verification_token = self.token_service.generate_verification_token(str(user.id))
            await self.email_service.send_verification_email(user.email, verification_token)
        
        return {
            "message": "User registered successfully. Please check your email for verification.",
            "user_id": str(user.id)
        }
    
    async def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user with email and password."""
        # Get user
        user = await self.user_repository.get_by_email(email)
        if not user:
            raise ValueError("Invalid email or password")

        # Verify password
        if not user.password_hash or not self.password_service.verify_password(
            password, user.password_hash
        ):
            raise ValueError("Invalid email or password")

        # Check if user can login
        if not user.can_login:
            raise ValueError("Account is not active or verified")

        # Handle 2FA if enabled
        if user.two_factor_enabled:
            # 1. Generate 6-digit code
            tfa_code = "".join(random.choices(string.digits, k=6))
            code_hash = self.password_service.hash_password(tfa_code)
            expires_at = datetime.utcnow() + timedelta(minutes=10)

            # 2. Save hashed code and expiry to the database
            await self.two_factor_auth_repository.create_2fa_code(user.id, code_hash, expires_at)
            
            # 3. Send code to user's email
            await self.email_service.send_2fa_code(user.email, tfa_code)
            
            # 4. Generate a temporary 2FA token
            tfa_token = self.token_service.create_2fa_token(str(user.id))
            
            return {
                "message": "2FA required. A code has been sent to your email.",
                "tfa_token": tfa_token,
            }

        # Generate final tokens if 2FA is not enabled
        access_token = self.token_service.create_access_token({"sub": str(user.id)})
        refresh_token = self.token_service.create_refresh_token(str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.token_service.get_access_token_expiry(),
        }

    async def verify_2fa_code(self, tfa_token: str, code: str) -> Dict[str, Any]:
        """Verify the 2FA code and return final tokens."""
        # 1. Verify the 2FA token
        payload = self.token_service.verify_token(tfa_token, token_type="2fa")
        if not payload:
            raise ValueError("Invalid or expired 2FA token")

        user_id = UUID(payload.get("sub"))

        # 2. Get the 2FA code from the database
        tfa_code_obj = await self.two_factor_auth_repository.get_2fa_code_by_user_id(user_id)
        if not tfa_code_obj:
            raise ValueError("Invalid or expired 2FA code")

        # 3. Verify the code
        if not self.password_service.verify_password(code, tfa_code_obj.code_hash):
            raise ValueError("Invalid 2FA code")

        # 4. Mark the code as used
        await self.two_factor_auth_repository.mark_code_as_used(tfa_code_obj.id)

        # 5. Generate final tokens
        access_token = self.token_service.create_access_token({"sub": str(user_id)})
        refresh_token = self.token_service.create_refresh_token(str(user_id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.token_service.get_access_token_expiry(),
        }
    
    async def authenticate_with_oauth(
        self, 
        oauth_provider: IOAuthProvider, 
        auth_code: str
    ) -> Dict[str, Any]:
        """Authenticate user with OAuth provider."""
        # Exchange code for user info
        user_info = await oauth_provider.exchange_code_for_user_info(auth_code)
        
        provider_name = oauth_provider.get_provider_name()
        provider_id = user_info.get("id")
        email = user_info.get("email")
        
        if not provider_id:
            raise ValueError(f"Insufficient user information from {provider_name}")
        
        # Find existing user
        user = None
        if email:
            user = await self.user_repository.get_by_email(email)
        
        if not user:
            if provider_name == "google":
                user = await self.user_repository.get_by_google_id(provider_id)
            elif provider_name == "facebook":
                user = await self.user_repository.get_by_facebook_id(provider_id)
        
        if user:
            # Update existing user
            update_data = {}
            if provider_name == "google" and user.google_id != provider_id:
                update_data["google_id"] = provider_id
            elif provider_name == "facebook" and user.facebook_id != provider_id:
                update_data["facebook_id"] = provider_id
            
            # Update verification status if needed
            if user_info.get("email_verified") and not user.is_email_verified:
                update_data["is_email_verified"] = True
                if user.status == UserStatus.PENDING_VERIFICATION:
                    update_data["status"] = UserStatus.ACTIVE.value
            
            if update_data:
                user = await self.user_repository.update(user.id, update_data)
        else:
            # Create new user
            if not email:
                raise ValueError("Email is required for registration")
            
            user_data = {
                "email": email,
                "first_name": user_info.get("first_name"),
                "last_name": user_info.get("last_name"),
                "is_email_verified": user_info.get("email_verified", False),
                "status": UserStatus.ACTIVE.value if user_info.get("email_verified") else UserStatus.PENDING_VERIFICATION.value
            }
            
            if provider_name == "google":
                user_data["google_id"] = provider_id
            elif provider_name == "facebook":
                user_data["facebook_id"] = provider_id
            
            user = await self.user_repository.create(user_data)
        
        if not user.can_login:
            raise ValueError("Account is not active")
        
        # Generate tokens
        access_token = self.token_service.create_access_token({"sub": str(user.id)})
        refresh_token = self.token_service.create_refresh_token(str(user.id))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.token_service.get_access_token_expiry()
        }
    
    async def verify_email(self, token: str) -> Dict[str, str]:
        """Verify user email with token."""
        # Validate and decode token
        user_id = self.token_service.verify_verification_token(token)
        if not user_id:
            raise ValueError("Invalid or expired verification token")
        
        # Get user and verify email
        user = await self.user_repository.get_by_id(UUID(user_id))
        if not user:
            raise ValueError("User not found")
        
        # Update user verification status
        update_data = {
            "is_email_verified": True,
            "status": UserStatus.ACTIVE.value
        }
        
        await self.user_repository.update(user.id, update_data)
        
        return {"message": "Email verified successfully"}
    
    async def change_password(
        self, 
        user_id: UUID, 
        current_password: str, 
        new_password: str
    ) -> Dict[str, str]:
        """Change user password."""
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Verify current password
        if not user.password_hash or not self.password_service.verify_password(current_password, user.password_hash):
            raise ValueError("Invalid current password")
        
        # Hash new password
        new_password_hash = self.password_service.hash_password(new_password)
        
        # Update password
        await self.user_repository.update(user_id, {"password_hash": new_password_hash})
        
        return {"message": "Password changed successfully"}