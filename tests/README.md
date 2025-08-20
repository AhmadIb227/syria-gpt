# Tests

This directory contains comprehensive tests for the Syria GPT Authentication API following Clean Architecture principles.

## Test Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── unit/                    # Unit tests (isolated components)
│   ├── domain/             # Domain entity tests
│   ├── infrastructure/     # Repository and service tests
│   └── application/        # Application service tests
├── integration/            # Integration tests (API endpoints)
└── fixtures/               # Test data fixtures
```

## Test Categories

### Unit Tests
- **Domain**: Test business entities and their methods
- **Infrastructure**: Test repository implementations and services
- **Application**: Test application service orchestration

### Integration Tests
- **API Endpoints**: Test complete HTTP request/response cycles
- **Database Integration**: Test with real database connections
- **OAuth Integration**: Test OAuth provider integrations

## Running Tests

### All Tests
```bash
pytest
```

### Unit Tests Only
```bash
pytest tests/unit/
```

### Integration Tests Only
```bash
pytest tests/integration/
```

### Specific Test Categories
```bash
# Domain tests
pytest tests/unit/domain/

# Repository tests
pytest tests/unit/infrastructure/

# API tests
pytest tests/integration/
```

### With Coverage
```bash
pytest --cov=. --cov-report=html
```

### Async Tests
All async tests use `pytest-asyncio` and are marked with `@pytest.mark.asyncio`.

## Test Fixtures

### Database Fixtures
- `test_db`: Clean database session for each test
- `user_repository`: Repository instance with test database
- `created_user`: Pre-created user for testing

### Service Fixtures
- `password_service`: Password hashing/verification service
- `token_service`: JWT token service
- `email_service`: Email service (mocked)

### Authentication Fixtures
- `valid_access_token`: Valid JWT access token
- `valid_refresh_token`: Valid JWT refresh token
- `sample_user_data`: Sample user registration data

### OAuth Fixtures
- `mock_google_provider`: Mocked Google OAuth provider
- `mock_facebook_provider`: Mocked Facebook OAuth provider
- `oauth_user_info`: Sample OAuth user information

## Mocking Strategy

### External Services
- OAuth providers are mocked to avoid external API calls
- Email service is mocked to avoid sending real emails
- Database uses SQLite in-memory for fast tests

### Authentication
- JWT tokens are real (not mocked) for integration tests
- Password hashing uses real bcrypt for security validation

## Test Best Practices

1. **Isolation**: Each test is independent and can run alone
2. **Fast**: Unit tests run in milliseconds
3. **Reliable**: Tests don't depend on external services
4. **Comprehensive**: Cover happy paths and error conditions
5. **Clean**: Use fixtures for setup and teardown

## Coverage Goals

- **Domain Layer**: 100% (business logic is critical)
- **Application Layer**: 95% (orchestration logic)
- **Infrastructure Layer**: 90% (repository implementations)
- **Presentation Layer**: 85% (API endpoints)

## Running Specific Tests

### Domain Entity Tests
```bash
pytest tests/unit/domain/test_user_entity.py -v
```

### Repository Tests
```bash
pytest tests/unit/infrastructure/test_user_repository.py -v
```

### API Endpoint Tests
```bash
pytest tests/integration/test_auth_endpoints.py -v
```

### Test a Specific Method
```bash
pytest tests/unit/domain/test_user_entity.py::TestUserEntity::test_user_creation -v
```

## Debugging Tests

### Run with Output
```bash
pytest -s
```

### Run with Detailed Output
```bash
pytest -v -s
```

### Run Failed Tests Only
```bash
pytest --lf
```

### Stop on First Failure
```bash
pytest -x
```