from pydantic import BaseModel, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False
    two_factor_code: Optional[str] = None
    redirect_to: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    redirect_to: Optional[str] = None


class TwoFactorChallenge(BaseModel):
    requires_2fa: bool = True
    message: str = "Two-factor authentication required. Provide the 2FA code."


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    phone_number: Optional[str] = None


class TwoFASetupResponse(BaseModel):
    otpauth_url: str
    qr_svg: str
    secret: str


class EmailRequest(BaseModel):
    email: EmailStr


class VerifyEmailRequest(BaseModel):
    token: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class MessageResponse(BaseModel):
    message: str
    link: Optional[str] = None


