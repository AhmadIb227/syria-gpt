from typing import Optional, Tuple, Union
from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token
from app.core.config import settings
from app.schemas.auth import TokenResponse, TwoFactorChallenge
import pyotp


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def login(
        self,
        *,
        email: str,
        password: str,
        remember_me: bool,
        two_factor_code: Optional[str] = None,
    ) -> Union[TokenResponse, TwoFactorChallenge]:
        user = self.user_repo.get_by_email(email)
        if not user:
            raise ValueError("Invalid credentials")

        if not verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")

        # 2FA check (placeholder; integrate pyotp or SMS/Email code store)
        if user.two_factor_enabled:
            if not two_factor_code:
                return TwoFactorChallenge()
            if not user.two_factor_secret:
                raise ValueError("2FA not properly configured")
            totp = pyotp.TOTP(user.two_factor_secret)
            if not totp.verify(two_factor_code, valid_window=1):
                raise ValueError("Invalid 2FA code")

        expires_delta = (
            settings.remember_me_expire if remember_me else settings.access_token_expire
        )
        access_token = create_access_token(
            subject=str(user.id),
            secret_key=settings.JWT_SECRET_KEY,
            expires_delta=expires_delta,
        )
        return TokenResponse(
            access_token=access_token,
            expires_in=int(expires_delta.total_seconds()),
        )


