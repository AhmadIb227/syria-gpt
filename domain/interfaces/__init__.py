"""Domain interfaces package."""

from .user_repository import IUserRepository
from .auth_service import IAuthService
from .oauth_provider import IOAuthProvider
from .two_factor_auth_repository import ITwoFactorAuthRepository

__all__ = ["IUserRepository", "IAuthService", "IOAuthProvider", "ITwoFactorAuthRepository"]