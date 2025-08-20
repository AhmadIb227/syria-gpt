"""Clean authentication routes using repository pattern and service layer."""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends

from config.model import User
from config.schemas import (
    UserSignUp, UserSignIn, UserResponse, TokenResponse,
    EmailVerificationRequest, PasswordResetRequest, PasswordResetConfirm,
    RefreshTokenRequest, GoogleAuthRequest, MessageResponse, ChangePasswordRequest
)
from config.auth import get_current_user, get_current_verified_user
from dependencies import AuthServiceDep

router = APIRouter(tags=["Authentication"])


@router.post("/signup", response_model=Dict[str, Any])
async def sign_up(
    user_data: UserSignUp,
    auth_service: AuthServiceDep
):
    """Register a new user."""
    user_dict = user_data.model_dump()
    return auth_service.register_user(user_dict)


@router.post("/signin", response_model=TokenResponse)
async def sign_in(
    user_credentials: UserSignIn,
    auth_service: AuthServiceDep
):
    """Authenticate user and return tokens."""
    tokens = auth_service.authenticate_user(
        user_credentials.email,
        user_credentials.password
    )
    return TokenResponse(**tokens)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_request: RefreshTokenRequest,
    auth_service: AuthServiceDep
):
    """Refresh access token using refresh token."""
    tokens = auth_service.refresh_access_token(token_request.refresh_token)
    return TokenResponse(**tokens)


@router.post("/signout", response_model=MessageResponse)
async def sign_out(
    token_request: RefreshTokenRequest,
    auth_service: AuthServiceDep,
    current_user: User = Depends(get_current_user),
):
    """Sign out user by revoking refresh token."""
    result = auth_service.sign_out_user(current_user.id, token_request.refresh_token)
    return MessageResponse(**result)


@router.post("/signout-all", response_model=MessageResponse)
async def sign_out_all(
    auth_service: AuthServiceDep,
    current_user: User = Depends(get_current_user),
):
    """Sign out user from all devices."""
    result = auth_service.sign_out_all_devices(current_user.id)
    return MessageResponse(**result)


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verification_request: EmailVerificationRequest,
    auth_service: AuthServiceDep
):
    """Verify user email with token."""
    result = auth_service.verify_email(verification_request.token)
    return MessageResponse(**result)


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification_email(
    auth_service: AuthServiceDep,
    current_user: User = Depends(get_current_user),
):
    """Resend verification email to user."""
    result = auth_service.resend_verification_email(current_user)
    return MessageResponse(**result)


@router.post("/reset-password", response_model=MessageResponse)
async def request_password_reset(
    reset_request: PasswordResetRequest,
    auth_service: AuthServiceDep
):
    """Request password reset for user."""
    result = auth_service.request_password_reset(reset_request.email)
    return MessageResponse(**result)


@router.post("/reset-password/confirm", response_model=MessageResponse)
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    auth_service: AuthServiceDep
):
    """Confirm password reset with token."""
    result = auth_service.confirm_password_reset(reset_data.token, reset_data.new_password)
    return MessageResponse(**result)


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    auth_service: AuthServiceDep,
    current_user: User = Depends(get_current_verified_user),
):
    """Change user password."""
    result = auth_service.change_password(
        current_user.id,
        password_data.current_password,
        password_data.new_password
    )
    return MessageResponse(**result)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user


@router.get("/google")
async def google_auth():
    """Get Google OAuth URL."""
    from urllib.parse import urlencode
    from config.settings import settings
    
    # Validate OAuth configuration
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )
    
    # Use the correct Google OAuth 2.0 authorization endpoint
    base_url = "https://accounts.google.com/o/oauth2/v2/auth"
    
    # Define parameters explicitly with proper types
    params = {
        "client_id": str(settings.GOOGLE_CLIENT_ID).strip(),
        "redirect_uri": str(settings.GOOGLE_REDIRECT_URI).strip(),
        "scope": "openid email profile",
        "response_type": "code",
        "access_type": "offline",
        "prompt": "consent",
        "state": "oauth_security_state"  # Add state parameter for security
    }
    
    # Properly encode the parameters
    google_auth_url = f"{base_url}?{urlencode(params)}"
    
    return {
        "auth_url": google_auth_url,
        "client_id": settings.GOOGLE_CLIENT_ID[:20] + "...",  # Debug info
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "parameters_count": len(params)
    }


@router.post("/google/callback", response_model=TokenResponse)
async def google_callback(
    auth_request: GoogleAuthRequest,
    auth_service: AuthServiceDep
):
    """Handle Google OAuth callback."""
    tokens = await auth_service.authenticate_with_google(auth_request.code)
    return TokenResponse(**tokens)