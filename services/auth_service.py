"""Authentication service with business logic."""

from typing import Dict, Any, Optional
from uuid import UUID
from fastapi import HTTPException, status
import httpx
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from config.model import User
from config.auth import AuthUtils
from config.email_service import email_service
from config.settings import settings
from repositories.user_repository import UserRepository
from repositories.auth_repositories import (
    EmailVerificationRepository,
    PasswordResetRepository,
    RefreshTokenRepository,
    AuthRepositoryManager
)


class AuthService:
    """Authentication service handling business logic."""
    
    def __init__(
        self,
        user_repo: UserRepository,
        email_verification_repo: EmailVerificationRepository,
        password_reset_repo: PasswordResetRepository,
        refresh_token_repo: RefreshTokenRepository,
        auth_manager: AuthRepositoryManager
    ):
        self.user_repo = user_repo
        self.email_verification_repo = email_verification_repo
        self.password_reset_repo = password_reset_repo
        self.refresh_token_repo = refresh_token_repo
        self.auth_manager = auth_manager
    
    def register_user(self, user_data: Dict[str, Any]) -> Dict[str, str]:
        """Register a new user with email verification."""
        # Validation
        if self.user_repo.email_exists(user_data["email"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        if user_data.get("phone_number") and self.user_repo.phone_exists(user_data["phone_number"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Phone number already registered"
            )
        
        # Hash password and create user
        hashed_password = AuthUtils.get_password_hash(user_data["password"])
        
        user_create_data = {
            "email": user_data["email"],
            "password_hash": hashed_password,
            "first_name": user_data.get("first_name"),
            "last_name": user_data.get("last_name"),
            "phone_number": user_data.get("phone_number"),
            "status": "pending_verification"
        }
        
        user = self.user_repo.create_user(user_create_data)
        
        # Create and send verification token
        verification_token = AuthUtils.generate_verification_token()
        self.email_verification_repo.create_verification(
            user.id, 
            verification_token, 
            settings.EMAIL_VERIFICATION_EXPIRE_HOURS
        )
        
        # Send verification email
        email_service.send_verification_email(user.email, verification_token)
        
        return {
            "message": "User registered successfully. Please check your email for verification.",
            "user_id": str(user.id)
        }
    
    def authenticate_user(self, email: str, password: str) -> Dict[str, Any]:
        """Authenticate user and return tokens."""
        # Get user
        user = self.user_repo.get_by_email(email)
        
        # Verify credentials
        if not user or not AuthUtils.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Check if account is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Generate tokens
        access_token = AuthUtils.create_access_token(data={"sub": str(user.id)})
        refresh_token = AuthUtils.create_refresh_token(str(user.id))
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "token_type": "bearer"
        }
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token."""
        # Validate refresh token
        if not self.refresh_token_repo.is_valid_token(refresh_token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Get refresh token record
        refresh_token_record = self.refresh_token_repo.get_by_token(refresh_token)
        if not refresh_token_record:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user and verify active status
        user = self.user_repo.get_by_id(refresh_token_record.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Revoke old token and create new ones
        self.refresh_token_repo.revoke_token(refresh_token)
        
        access_token = AuthUtils.create_access_token(data={"sub": str(user.id)})
        new_refresh_token = AuthUtils.create_refresh_token(str(user.id))
        
        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "token_type": "bearer"
        }
    
    def verify_email(self, token: str) -> Dict[str, str]:
        """Verify user email with token."""
        # Validate token
        if not self.email_verification_repo.is_valid_token(token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        # Get verification record
        verification_record = self.email_verification_repo.get_by_token(token)
        if not verification_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification token not found"
            )
        
        # Mark token as used and verify user
        self.email_verification_repo.mark_as_used(token)
        self.user_repo.update_verification_status(
            verification_record.user_id, 
            email_verified=True
        )
        
        return {"message": "Email verified successfully"}
    
    def request_password_reset(self, email: str) -> Dict[str, str]:
        """Request password reset for user."""
        user = self.user_repo.get_by_email(email)
        
        if user and user.is_active:
            # Revoke existing reset tokens
            self.password_reset_repo.revoke_user_tokens(user.id)
            
            # Create new reset token
            reset_token = AuthUtils.generate_reset_token()
            self.password_reset_repo.create_reset_token(
                user.id,
                reset_token,
                settings.PASSWORD_RESET_EXPIRE_HOURS
            )
            
            # Send reset email
            email_service.send_password_reset_email(user.email, reset_token)
        
        return {"message": "If the email exists, a password reset link has been sent"}
    
    def confirm_password_reset(self, token: str, new_password: str) -> Dict[str, str]:
        """Confirm password reset with token."""
        # Validate token
        if not self.password_reset_repo.is_valid_token(token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Get reset record
        reset_record = self.password_reset_repo.get_by_token(token)
        if not reset_record:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token not found"
            )
        
        # Get user
        user = self.user_repo.get_by_id(reset_record.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Mark token as used
        self.password_reset_repo.mark_as_used(token)
        
        # Update password and revoke all refresh tokens
        hashed_password = AuthUtils.get_password_hash(new_password)
        self.user_repo.update(reset_record.user_id, {"password_hash": hashed_password})
        self.refresh_token_repo.revoke_user_tokens(user.id)
        
        return {"message": "Password reset successfully"}
    
    def change_password(self, user_id: UUID, current_password: str, new_password: str) -> Dict[str, str]:
        """Change user password."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not AuthUtils.verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid current password"
            )
        
        # Update password and revoke all refresh tokens
        hashed_password = AuthUtils.get_password_hash(new_password)
        self.user_repo.update(user_id, {"password_hash": hashed_password})
        self.refresh_token_repo.revoke_user_tokens(user_id)
        
        return {"message": "Password changed successfully"}
    
    def resend_verification_email(self, user: User) -> Dict[str, str]:
        """Resend verification email to user."""
        if user.is_email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified"
            )
        
        # Revoke existing verification tokens
        self.email_verification_repo.revoke_user_tokens(user.id)
        
        # Create new verification token
        verification_token = AuthUtils.generate_verification_token()
        self.email_verification_repo.create_verification(
            user.id,
            verification_token,
            settings.EMAIL_VERIFICATION_EXPIRE_HOURS
        )
        
        # Send verification email
        email_service.send_verification_email(user.email, verification_token)
        
        return {"message": "Verification email sent successfully"}
    
    def sign_out_user(self, user_id: UUID, refresh_token: str) -> Dict[str, str]:
        """Sign out user by revoking refresh token."""
        refresh_token_record = self.refresh_token_repo.get_by_token(refresh_token)
        
        if refresh_token_record and refresh_token_record.user_id == user_id:
            self.refresh_token_repo.revoke_token(refresh_token)
        
        return {"message": "Successfully signed out"}
    
    def sign_out_all_devices(self, user_id: UUID) -> Dict[str, str]:
        """Sign out user from all devices."""
        revoked_count = self.refresh_token_repo.revoke_user_tokens(user_id)
        
        return {"message": "Successfully signed out from all devices"}
    
    async def authenticate_with_google(self, auth_code: str) -> Dict[str, Any]:
        """Authenticate user with Google OAuth."""
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail="Google OAuth not configured"
            )
        
        try:
            # Exchange code for tokens
            async with httpx.AsyncClient() as client:
                token_response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "code": auth_code,
                        "grant_type": "authorization_code",
                        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                    }
                )
                
                if token_response.status_code != 200:
                    error_detail = "Failed to exchange code for token"
                    try:
                        error_data = token_response.json()
                        if 'error' in error_data:
                            error_detail = f"Google OAuth error: {error_data['error']}"
                            if 'error_description' in error_data:
                                error_detail += f" - {error_data['error_description']}"
                    except:
                        error_detail += f" (HTTP {token_response.status_code})"
                    
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_detail
                    )
                
                token_data = token_response.json()
                id_token_str = token_data.get("id_token")
                
                if not id_token_str:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No ID token received"
                    )
                
                # Verify and decode ID token
                idinfo = id_token.verify_oauth2_token(
                    id_token_str, 
                    google_requests.Request(), 
                    settings.GOOGLE_CLIENT_ID
                )
                
                if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                    raise ValueError('Wrong issuer.')
                
                # Extract user info
                google_id = idinfo.get('sub')
                email = idinfo.get('email')
                first_name = idinfo.get('given_name')
                last_name = idinfo.get('family_name')
                email_verified = idinfo.get('email_verified', False)
                
                if not google_id or not email:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Insufficient user information from Google"
                    )
                
                # Find or create user
                user = self.user_repo.get_by_email(email) or self.user_repo.get_by_google_id(google_id)
                
                if user:
                    # Update existing user
                    update_data = {}
                    if user.google_id != google_id:
                        update_data['google_id'] = google_id
                    if email_verified and not user.is_email_verified:
                        update_data['is_email_verified'] = True
                        update_data['status'] = "active"
                    if not user.first_name and first_name:
                        update_data['first_name'] = first_name
                    if not user.last_name and last_name:
                        update_data['last_name'] = last_name
                    
                    if update_data:
                        self.user_repo.update(user.id, update_data)
                        user = self.user_repo.get_by_id(user.id)  # Refresh user data
                
                else:
                    # Create new user
                    user_data = {
                        "email": email,
                        "google_id": google_id,
                        "first_name": first_name,
                        "last_name": last_name,
                        "is_email_verified": email_verified,
                        "status": "active" if email_verified else "pending_verification"
                    }
                    user = self.user_repo.create_user(user_data)
                
                if not user.is_active:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Account is deactivated"
                    )
                
                # Generate tokens
                access_token = AuthUtils.create_access_token(data={"sub": str(user.id)})
                refresh_token = AuthUtils.create_refresh_token(str(user.id))
                
                return {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
                    "token_type": "bearer"
                }
        
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Authentication failed"
            )