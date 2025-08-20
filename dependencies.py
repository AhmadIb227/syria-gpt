"""Dependency injection for repositories and services."""

from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from fastapi_sqlalchemy import db

from repositories.user_repository import UserRepository
from repositories.auth_repositories import (
    EmailVerificationRepository,
    PasswordResetRepository, 
    RefreshTokenRepository,
    AuthRepositoryManager
)
from services.auth_service import AuthService


def get_db_session() -> Session:
    """Get database session dependency."""
    return db.session


def get_user_repository(
    db_session: Annotated[Session, Depends(get_db_session)]
) -> UserRepository:
    """Get user repository dependency."""
    return UserRepository(db_session)


def get_email_verification_repository(
    db_session: Annotated[Session, Depends(get_db_session)]
) -> EmailVerificationRepository:
    """Get email verification repository dependency."""
    return EmailVerificationRepository(db_session)


def get_password_reset_repository(
    db_session: Annotated[Session, Depends(get_db_session)]
) -> PasswordResetRepository:
    """Get password reset repository dependency."""
    return PasswordResetRepository(db_session)


def get_refresh_token_repository(
    db_session: Annotated[Session, Depends(get_db_session)]
) -> RefreshTokenRepository:
    """Get refresh token repository dependency."""
    return RefreshTokenRepository(db_session)


def get_auth_repository_manager(
    db_session: Annotated[Session, Depends(get_db_session)]
) -> AuthRepositoryManager:
    """Get auth repository manager dependency."""
    return AuthRepositoryManager(db_session)


def get_auth_service(
    db_session: Annotated[Session, Depends(get_db_session)]
) -> AuthService:
    """Get authentication service dependency."""
    user_repo = UserRepository(db_session)
    email_verification_repo = EmailVerificationRepository(db_session)
    password_reset_repo = PasswordResetRepository(db_session)
    refresh_token_repo = RefreshTokenRepository(db_session)
    auth_manager = AuthRepositoryManager(db_session)
    
    return AuthService(
        user_repo,
        email_verification_repo,
        password_reset_repo,
        refresh_token_repo,
        auth_manager
    )


# Type aliases for cleaner injection
UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
EmailVerificationRepositoryDep = Annotated[EmailVerificationRepository, Depends(get_email_verification_repository)]
PasswordResetRepositoryDep = Annotated[PasswordResetRepository, Depends(get_password_reset_repository)]
RefreshTokenRepositoryDep = Annotated[RefreshTokenRepository, Depends(get_refresh_token_repository)]
AuthRepositoryManagerDep = Annotated[AuthRepositoryManager, Depends(get_auth_repository_manager)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]