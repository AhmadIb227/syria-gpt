"""Authentication controller - handles HTTP requests."""

from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from uuid import UUID
from presentation.schemas import TwoFactorVerificationRequest

from application import AuthApplicationService
from presentation.schemas import (
    UserSignUpRequest, UserSignInRequest, UserResponse, TokenResponse,
    GoogleAuthRequest, FacebookAuthRequest, MessageResponse,
    ChangePasswordRequest, EmailVerificationRequest, TwoFactorVerificationRequest # تمت الإضافة هنا
)
from presentation.dependencies import get_auth_service, get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/signup", response_model=MessageResponse)
async def sign_up(
    user_data: UserSignUpRequest,
    auth_service: AuthApplicationService = Depends(get_auth_service)
):
    """Register a new user."""
    try:
        result = await auth_service.register_user(user_data.model_dump())
        return MessageResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/signin", response_model=TokenResponse)
async def sign_in(
    credentials: UserSignInRequest,
    auth_service: AuthApplicationService = Depends(get_auth_service)
):
    """Authenticate user and return tokens."""
    try:
        tokens = await auth_service.authenticate_user(
            credentials.email,
            credentials.password
        )
        return TokenResponse(**tokens)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    

# أضف هذه الدالة بعد دالة sign_in
@router.post("/2fa/verify", response_model=TokenResponse)
async def verify_2fa(
    verification_data: TwoFactorVerificationRequest,
    auth_service: AuthApplicationService = Depends(get_auth_service)
):
    """Verify 2FA code and return final access/refresh tokens."""
    try:
        tokens = await auth_service.verify_2fa_code(
            verification_data.tfa_token,
            verification_data.code
        )
        return TokenResponse(**tokens)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.get("/google")
async def google_auth(
    auth_service: AuthApplicationService = Depends(get_auth_service)
):
    """Get Google OAuth URL."""
    try:
        return auth_service.get_google_auth_url()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e)
        )


@router.post("/google/callback", response_model=TokenResponse)
async def google_callback(
    auth_request: GoogleAuthRequest,
    auth_service: AuthApplicationService = Depends(get_auth_service)
):
    """Handle Google OAuth callback."""
    try:
        tokens = await auth_service.authenticate_with_google(auth_request.code)
        return TokenResponse(**tokens)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/facebook")
async def facebook_auth(
    auth_service: AuthApplicationService = Depends(get_auth_service)
):
    """Get Facebook OAuth URL."""
    try:
        return auth_service.get_facebook_auth_url()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=str(e)
        )


@router.post("/facebook/callback", response_model=TokenResponse)
async def facebook_callback(
    auth_request: FacebookAuthRequest,
    auth_service: AuthApplicationService = Depends(get_auth_service)
):
    """Handle Facebook OAuth callback."""
    try:
        tokens = await auth_service.authenticate_with_facebook(auth_request.code)
        return TokenResponse(**tokens)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(
    verification_request: EmailVerificationRequest,
    auth_service: AuthApplicationService = Depends(get_auth_service)
):
    """Verify user email with token."""
    try:
        result = await auth_service.verify_email(verification_request.token)
        return MessageResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    auth_service: AuthApplicationService = Depends(get_auth_service),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Change user password."""
    try:
        result = await auth_service.change_password(
            UUID(current_user["sub"]),
            password_data.current_password,
            password_data.new_password
        )
        return MessageResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user),
    auth_service: AuthApplicationService = Depends(get_auth_service)
):
    """Get current user information."""
    try:
        # In a real implementation, you would fetch user data from the service
        user_id = current_user.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # For now, return basic info from the token
        # In production, this would call auth_service.get_user_by_id(user_id)
        return UserResponse(
            id=user_id,
            email="user@example.com",  # Would be fetched from service
            first_name="User",
            last_name="Name",
            is_email_verified=True,
            is_phone_verified=False,
            two_factor_enabled=False,
            status="active",
            is_active=True
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user information"
        )