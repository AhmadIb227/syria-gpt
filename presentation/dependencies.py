"""Dependency injection for presentation layer."""

from typing import Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from application import AuthApplicationService
from domain.use_cases import AuthUseCases
from infrastructure.database import UserRepositoryImpl
from infrastructure.services import PasswordService, TokenService, EmailService
from infrastructure.external_services import GoogleOAuthProvider, FacebookOAuthProvider
from config.model import get_db

# Security
security = HTTPBearer()

# Singleton services
_password_service = None
_token_service = None
_email_service = None
_google_provider = None
_facebook_provider = None


def get_password_service() -> PasswordService:
    """Get singleton password service."""
    global _password_service
    if _password_service is None:
        _password_service = PasswordService()
    return _password_service


def get_token_service() -> TokenService:
    """Get singleton token service."""
    global _token_service
    if _token_service is None:
        _token_service = TokenService()
    return _token_service


def get_email_service() -> EmailService:
    """Get singleton email service."""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service


def get_google_provider() -> GoogleOAuthProvider:
    """Get singleton Google OAuth provider."""
    global _google_provider
    if _google_provider is None:
        _google_provider = GoogleOAuthProvider()
    return _google_provider


def get_facebook_provider() -> FacebookOAuthProvider:
    """Get singleton Facebook OAuth provider."""
    global _facebook_provider
    if _facebook_provider is None:
        _facebook_provider = FacebookOAuthProvider()
    return _facebook_provider


def get_auth_service(db: Session = Depends(get_db)) -> AuthApplicationService:
    """Get authentication application service."""
    user_repository = UserRepositoryImpl(db)
    auth_use_cases = AuthUseCases(
        user_repository=user_repository,
        password_service=get_password_service(),
        token_service=get_token_service(),
        email_service=get_email_service()
    )
    return AuthApplicationService(
        auth_use_cases=auth_use_cases,
        google_provider=get_google_provider(),
        facebook_provider=get_facebook_provider()
    )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Get current user from JWT token."""
    token = credentials.credentials
    token_service = get_token_service()
    
    payload = token_service.verify_token(token, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload