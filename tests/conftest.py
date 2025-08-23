"""Test configuration and fixtures."""

import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from unittest.mock import Mock

from main import create_app
from database.models import Base
from config.database import get_db
from domain.entities import User, UserStatus
from infrastructure.services import PasswordService, TokenService, EmailService
from infrastructure.external_services import GoogleOAuthProvider, FacebookOAuthProvider
from infrastructure.database import UserRepositoryImpl


# Test database URL - using PostgreSQL for testing
# Use Docker service name when running inside Docker, localhost when running outside
import os
DB_HOST = os.getenv("DB_HOST", "db" if os.path.exists("/.dockerenv") else "localhost")
TEST_DATABASE_URL = f"postgresql://admin:admin123@{DB_HOST}:5432/syriagpt_test"




@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_db(test_engine) -> Generator[Session, None, None]:
    """Create test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def client(test_db: Session) -> Generator[TestClient, None, None]:
    """Create test client with test database."""
    app = create_app()
    def override_get_db():
        try:
            yield test_db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def password_service() -> PasswordService:
    """Create password service instance."""
    return PasswordService()


@pytest.fixture
def token_service(test_db: Session) -> TokenService:
    """Create token service instance."""
    from infrastructure.database.repositories.password_reset_repository import PasswordResetRepository
    password_reset_repo = PasswordResetRepository(test_db)
    return TokenService(password_reset_repo)


@pytest.fixture
def email_service() -> EmailService:
    """Create email service instance."""
    return EmailService()


@pytest.fixture
def mock_google_provider() -> Mock:
    """Create mock Google OAuth provider."""
    mock = Mock(spec=GoogleOAuthProvider)
    mock.get_provider_name.return_value = "google"
    mock.get_authorization_url.return_value = "https://accounts.google.com/oauth/authorize?..."
    return mock


@pytest.fixture
def mock_facebook_provider() -> Mock:
    """Create mock Facebook OAuth provider."""
    mock = Mock(spec=FacebookOAuthProvider)
    mock.get_provider_name.return_value = "facebook"
    mock.get_authorization_url.return_value = "https://www.facebook.com/dialog/oauth?..."
    return mock


@pytest.fixture
def user_repository(test_db: Session) -> UserRepositoryImpl:
    """Create user repository instance."""
    return UserRepositoryImpl(test_db)


@pytest.fixture
def sample_user_data() -> dict:
    """Sample user data for testing."""
    return {
        "email": "test@example.com",
        "password": "testpassword123",
        "first_name": "Test",
        "last_name": "User",
        "phone_number": "+963123456789"
    }


@pytest.fixture
async def created_user(user_repository: UserRepositoryImpl, password_service: PasswordService) -> User:
    """Create a test user in database."""
    user_data = {
        "email": "testuser@example.com",
        "password_hash": password_service.hash_password("testpassword123"),
        "first_name": "Test",
        "last_name": "User",
        "is_email_verified": True,
        "status": UserStatus.ACTIVE.value,
        "is_active": True
    }
    user = await user_repository.create(user_data)
    return user


@pytest.fixture
async def valid_access_token(token_service: TokenService, created_user: User) -> str:
    """Create valid access token for testing."""
    user = await created_user
    return token_service.create_access_token({"sub": str(user.id)})


@pytest.fixture
async def valid_refresh_token(token_service: TokenService, created_user: User) -> str:
    """Create valid refresh token for testing."""
    user = await created_user
    return token_service.create_refresh_token(str(user.id))


@pytest.fixture
def oauth_user_info() -> dict:
    """Sample OAuth user info for testing."""
    return {
        "id": "12345678901234567890",
        "email": "oauth@example.com",
        "first_name": "OAuth",
        "last_name": "User",
        "email_verified": True
    }