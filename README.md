# Syria GPT Authentication API

Clean Architecture implementation for Syria GPT with OAuth 2.0 integration.

## Architecture

This project follows Clean Architecture principles with clear separation of concerns:

```
├── domain/                 # Core business logic
│   ├── entities/          # Domain entities
│   ├── interfaces/        # Repository & service interfaces
│   └── use_cases/         # Business use cases
├── infrastructure/        # External concerns
│   ├── database/          # Repository implementations
│   ├── external_services/ # OAuth providers
│   └── services/          # Infrastructure services
├── application/           # Application services
├── presentation/          # HTTP API layer
│   ├── api/              # Controllers
│   └── schemas/          # Request/Response models
└── config/               # Configuration
```

## Features

- **Authentication**: Email/password and OAuth 2.0
- **OAuth Providers**: Google and Facebook
- **Clean Architecture**: Proper layer separation
- **Repository Pattern**: Data access abstraction
- **Dependency Injection**: Loose coupling

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment variables in `.env`:
```env
DATABASE_URL=sqlite:///./syria_gpt.db
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
FACEBOOK_APP_ID=your-facebook-app-id
FACEBOOK_APP_SECRET=your-facebook-app-secret
```

3. Start the server:
```bash
uvicorn main:app --port 9000 --reload
```

## API Endpoints

- `POST /auth/signup` - User registration
- `POST /auth/signin` - User login
- `GET /auth/google` - Google OAuth URL
- `POST /auth/google/callback` - Google OAuth callback
- `GET /auth/facebook` - Facebook OAuth URL
- `POST /auth/facebook/callback` - Facebook OAuth callback
- `GET /auth/me` - Current user info
- `POST /auth/change-password` - Change password

## Clean Architecture Benefits

1. **Independence**: Business logic independent of frameworks
2. **Testability**: Easy to unit test core logic
3. **Maintainability**: Clear boundaries and responsibilities
4. **Flexibility**: Easy to swap implementations

## Layer Responsibilities

- **Domain**: Core business rules and entities
- **Application**: Orchestrates use cases
- **Infrastructure**: External services and data persistence
- **Presentation**: HTTP API and user interface concerns