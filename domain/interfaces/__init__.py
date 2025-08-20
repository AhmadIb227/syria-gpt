"""Domain interfaces package."""

from .user_repository import IUserRepository
from .auth_service import IAuthService
from .oauth_provider import IOAuthProvider

__all__ = ["IUserRepository", "IAuthService", "IOAuthProvider"]