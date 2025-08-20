import uuid
from datetime import datetime, timedelta
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi_sqlalchemy import db
from sqlalchemy import and_, or_
import httpx
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from config.model import User, EmailVerification, PasswordReset, RefreshToken
from config.schemas import (
    UserSignUp, UserSignIn, UserResponse, TokenResponse,
    EmailVerificationRequest, PasswordResetRequest, PasswordResetConfirm,
    RefreshTokenRequest, GoogleAuthRequest, MessageResponse, ChangePasswordRequest
)
from config.auth import AuthUtils, get_current_user, get_current_verified_user
from config.email_service import email_service
from config.settings import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=Dict[str, Any])
async def sign_up(user_data: UserSignUp):
    existing_user = db.session.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = AuthUtils.get_password_hash(user_data.password)
    
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone_number=user_data.phone_number,
        status="pending_verification"
    )
    
    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    
    verification_token = AuthUtils.generate_verification_token()
    expires_at = datetime.utcnow() + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS)
    
    email_verification = EmailVerification(
        user_id=user.id,
        token=verification_token,
        expires_at=expires_at
    )
    
    db.session.add(email_verification)
    db.session.commit()
    
    email_service.send_verification_email(user.email, verification_token)
    
    return {
        "message": "User registered successfully. Please check your email for verification.",
        "user_id": str(user.id)
    }

@router.post("/signin", response_model=TokenResponse)
async def sign_in(user_credentials: UserSignIn):
    user = db.session.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not AuthUtils.verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account is deactivated"
        )
    
    access_token = AuthUtils.create_access_token(data={"sub": str(user.id)})
    refresh_token = AuthUtils.create_refresh_token(str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(token_request: RefreshTokenRequest):
    refresh_token_record = db.session.query(RefreshToken).filter(
        and_(
            RefreshToken.token == token_request.refresh_token,
            RefreshToken.expires_at > datetime.utcnow(),
            RefreshToken.is_revoked == False
        )
    ).first()
    
    if not refresh_token_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user = db.session.query(User).filter(User.id == refresh_token_record.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    refresh_token_record.is_revoked = True
    db.session.commit()
    
    access_token = AuthUtils.create_access_token(data={"sub": str(user.id)})
    new_refresh_token = AuthUtils.create_refresh_token(str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

@router.post("/signout", response_model=MessageResponse)
async def sign_out(
    token_request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user)
):
    refresh_token_record = db.session.query(RefreshToken).filter(
        and_(
            RefreshToken.token == token_request.refresh_token,
            RefreshToken.user_id == current_user.id,
            RefreshToken.is_revoked == False
        )
    ).first()
    
    if refresh_token_record:
        refresh_token_record.is_revoked = True
        db.session.commit()
    
    return MessageResponse(message="Successfully signed out")

@router.post("/signout-all", response_model=MessageResponse)
async def sign_out_all(current_user: User = Depends(get_current_user)):
    db.session.query(RefreshToken).filter(
        and_(
            RefreshToken.user_id == current_user.id,
            RefreshToken.is_revoked == False
        )
    ).update({"is_revoked": True})
    
    db.session.commit()
    
    return MessageResponse(message="Successfully signed out from all devices")

@router.post("/verify-email", response_model=MessageResponse)
async def verify_email(verification_request: EmailVerificationRequest):
    verification_record = db.session.query(EmailVerification).filter(
        and_(
            EmailVerification.token == verification_request.token,
            EmailVerification.expires_at > datetime.utcnow(),
            EmailVerification.is_used == False
        )
    ).first()
    
    if not verification_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )
    
    user = db.session.query(User).filter(User.id == verification_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    verification_record.is_used = True
    user.is_email_verified = True
    user.status = "active"
    
    db.session.commit()
    
    return MessageResponse(message="Email verified successfully")

@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification_email(current_user: User = Depends(get_current_user)):
    if current_user.is_email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    db.session.query(EmailVerification).filter(
        and_(
            EmailVerification.user_id == current_user.id,
            EmailVerification.is_used == False
        )
    ).update({"is_used": True})
    
    verification_token = AuthUtils.generate_verification_token()
    expires_at = datetime.utcnow() + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS)
    
    email_verification = EmailVerification(
        user_id=current_user.id,
        token=verification_token,
        expires_at=expires_at
    )
    
    db.session.add(email_verification)
    db.session.commit()
    
    email_service.send_verification_email(current_user.email, verification_token)
    
    return MessageResponse(message="Verification email sent successfully")

@router.post("/reset-password", response_model=MessageResponse)
async def request_password_reset(reset_request: PasswordResetRequest):
    user = db.session.query(User).filter(User.email == reset_request.email).first()
    
    if user and user.is_active:
        db.session.query(PasswordReset).filter(
            and_(
                PasswordReset.user_id == user.id,
                PasswordReset.is_used == False
            )
        ).update({"is_used": True})
        
        reset_token = AuthUtils.generate_reset_token()
        expires_at = datetime.utcnow() + timedelta(hours=settings.PASSWORD_RESET_EXPIRE_HOURS)
        
        password_reset = PasswordReset(
            user_id=user.id,
            token=reset_token,
            expires_at=expires_at
        )
        
        db.session.add(password_reset)
        db.session.commit()
        
        email_service.send_password_reset_email(user.email, reset_token)
    
    return MessageResponse(message="If the email exists, a password reset link has been sent")

@router.post("/reset-password/confirm", response_model=MessageResponse)
async def confirm_password_reset(reset_data: PasswordResetConfirm):
    reset_record = db.session.query(PasswordReset).filter(
        and_(
            PasswordReset.token == reset_data.token,
            PasswordReset.expires_at > datetime.utcnow(),
            PasswordReset.is_used == False
        )
    ).first()
    
    if not reset_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    user = db.session.query(User).filter(User.id == reset_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    reset_record.is_used = True
    user.password_hash = AuthUtils.get_password_hash(reset_data.new_password)
    
    db.session.query(RefreshToken).filter(
        and_(
            RefreshToken.user_id == user.id,
            RefreshToken.is_revoked == False
        )
    ).update({"is_revoked": True})
    
    db.session.commit()
    
    return MessageResponse(message="Password reset successfully")

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_verified_user)
):
    if not AuthUtils.verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid current password"
        )
    
    current_user.password_hash = AuthUtils.get_password_hash(password_data.new_password)
    
    db.session.query(RefreshToken).filter(
        and_(
            RefreshToken.user_id == current_user.id,
            RefreshToken.is_revoked == False
        )
    ).update({"is_revoked": True})
    
    db.session.commit()
    
    return MessageResponse(message="Password changed successfully")

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@router.get("/google")
async def google_auth():
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"scope=openid email profile&"
        f"response_type=code&"
        f"access_type=offline"
    )
    return {"auth_url": google_auth_url}

@router.post("/google/callback", response_model=TokenResponse)
async def google_callback(auth_request: GoogleAuthRequest):
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": auth_request.code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            token_data = token_response.json()
            id_token_str = token_data.get("id_token")
            
            if not id_token_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No ID token received"
                )
            
            idinfo = id_token.verify_oauth2_token(
                id_token_str, 
                google_requests.Request(), 
                settings.GOOGLE_CLIENT_ID
            )
            
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
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
            
            user = db.session.query(User).filter(
                or_(User.email == email, User.google_id == google_id)
            ).first()
            
            if user:
                if user.google_id != google_id:
                    user.google_id = google_id
                if email_verified and not user.is_email_verified:
                    user.is_email_verified = True
                    user.status = "active"
                if not user.first_name and first_name:
                    user.first_name = first_name
                if not user.last_name and last_name:
                    user.last_name = last_name
                
                db.session.commit()
                
            else:
                user = User(
                    email=email,
                    google_id=google_id,
                    first_name=first_name,
                    last_name=last_name,
                    is_email_verified=email_verified,
                    status="active" if email_verified else "pending_verification"
                )
                
                db.session.add(user)
                db.session.commit()
                db.session.refresh(user)
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Account is deactivated"
                )
            
            access_token = AuthUtils.create_access_token(data={"sub": str(user.id)})
            refresh_token = AuthUtils.create_refresh_token(str(user.id))
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
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