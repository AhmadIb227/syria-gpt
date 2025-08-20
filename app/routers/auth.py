from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from config.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, TwoFactorChallenge, RegisterRequest
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


