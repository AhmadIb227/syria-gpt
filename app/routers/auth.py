from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from app.schemas.auth import (
    LoginRequest,
    TokenResponse,
    TwoFactorChallenge,
    RegisterRequest,
    EmailRequest,
    VerifyEmailRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
    MessageResponse,
)
from app.services.auth_service import AuthService
from app.core.deps import get_current_user
from app.schemas.user import UserRead
from app.services.user_service import UserService


router = APIRouter()


@router.post("/login", response_model=TokenResponse, responses={402: {"model": TwoFactorChallenge}})
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    service = AuthService(db)
    try:
        result = service.login(
            email=payload.email,
            password=payload.password,
            remember_me=payload.remember_me,
            two_factor_code=payload.two_factor_code,
        )
        if isinstance(result, TwoFactorChallenge):
            # FastAPI doesn't support dynamic response model switch; use HTTP 402 to indicate 2FA required
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=result.model_dump(),
            )
        # Attach redirect if provided
        result.redirect_to = payload.redirect_to
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


@router.get("/providers")
def list_providers():
    return {
        "supported": ["google", "github"],
        "note": "Configure OAuth client IDs/secrets and redirect URIs to enable social login.",
    }


@router.get("/oauth/{provider}/authorize")
def oauth_authorize(provider: str, redirect_uri: str):
    # TODO: Implement using Authlib; return provider authorization URL
    return {"provider": provider, "authorize_url": "TODO", "redirect_uri": redirect_uri}


@router.get("/oauth/{provider}/callback")
def oauth_callback(provider: str, code: str, state: str):
    # TODO: Exchange code for token, fetch user info, upsert user, return JWT
    return {"provider": provider, "status": "TODO"}


@router.get("/me", response_model=UserRead)
def read_me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/register", response_model=UserRead, status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        user = service.register(
            email=payload.email,
            password=payload.password,
            phone_number=payload.phone_number,
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/request-verification", response_model=MessageResponse)
def request_verification(payload: EmailRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        token = service.issue_email_verification(email=payload.email)
        link = f"/auth/verify-email?token={token}"
        return MessageResponse(message="Verification issued", link=link)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/verify-email", response_model=UserRead)
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        user = service.verify_email(token=payload.token)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/request-password-reset", response_model=MessageResponse)
def request_password_reset(payload: PasswordResetRequest, db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        token = service.issue_password_reset(email=payload.email)
        link = f"/auth/reset-password?token={token}"
        return MessageResponse(message="Reset issued", link=link)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("/reset-password", response_model=UserRead)
def reset_password(payload: PasswordResetConfirm, db: Session = Depends(get_db)):
    service = UserService(db)
    try:
        user = service.reset_password(token=payload.token, new_password=payload.new_password)
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


