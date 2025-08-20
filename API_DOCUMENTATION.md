# Syria GPT Authentication API Documentation

## Overview
This is a comprehensive authentication API built with FastAPI that provides user registration, login, password management, email verification, and Google OAuth 2.0 integration.

## Base URL
- Development: `http://localhost:9000`
- API Documentation: `http://localhost:9000/docs`

## Authentication Flow

### 1. Traditional Email/Password Authentication
1. User registers with email and password (`POST /auth/signup`)
2. System sends verification email
3. User verifies email (`POST /auth/verify-email`)
4. User can now sign in (`POST /auth/signin`)

### 2. Google OAuth 2.0 Authentication
1. Get Google auth URL (`GET /auth/google`)
2. Redirect user to Google for authentication
3. Handle callback with auth code (`POST /auth/google/callback`)

## API Endpoints

### Health & Status

#### GET /health
Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "Syria GPT Authentication API"
}
```

### Authentication Endpoints

#### POST /auth/signup
Register a new user account.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890"
}
```

**Response:**
```json
{
  "message": "User registered successfully. Please check your email for verification.",
  "user_id": "uuid-string"
}
```

#### POST /auth/signin
Sign in with email and password.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST /auth/refresh
Refresh access token using refresh token.

**Request Body:**
```json
{
  "refresh_token": "refresh-token"
}
```

**Response:**
```json
{
  "access_token": "new-jwt-token",
  "refresh_token": "new-refresh-token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST /auth/signout
Sign out current session (revoke refresh token).

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "refresh_token": "refresh-token"
}
```

**Response:**
```json
{
  "message": "Successfully signed out"
}
```

#### POST /auth/signout-all
Sign out from all devices (revoke all refresh tokens).

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "message": "Successfully signed out from all devices"
}
```

### Email Verification

#### POST /auth/verify-email
Verify email address with token.

**Request Body:**
```json
{
  "token": "verification-token"
}
```

**Response:**
```json
{
  "message": "Email verified successfully"
}
```

#### POST /auth/resend-verification
Resend email verification.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "message": "Verification email sent successfully"
}
```

### Password Management

#### POST /auth/reset-password
Request password reset email.

**Request Body:**
```json
{
  "email": "user@example.com"
}
```

**Response:**
```json
{
  "message": "If the email exists, a password reset link has been sent"
}
```

#### POST /auth/reset-password/confirm
Confirm password reset with token.

**Request Body:**
```json
{
  "token": "reset-token",
  "new_password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "Password reset successfully"
}
```

#### POST /auth/change-password
Change password (requires authentication).

**Headers:** `Authorization: Bearer <access_token>`

**Request Body:**
```json
{
  "current_password": "currentpassword",
  "new_password": "newpassword123"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

### User Information

#### GET /auth/me
Get current user information.

**Headers:** `Authorization: Bearer <access_token>`

**Response:**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "is_email_verified": true,
  "is_phone_verified": false,
  "two_factor_enabled": false,
  "status": "active",
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Google OAuth 2.0

#### GET /auth/google
Get Google OAuth 2.0 authorization URL.

**Response:**
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?..."
}
```

#### POST /auth/google/callback
Handle Google OAuth callback.

**Request Body:**
```json
{
  "code": "google-auth-code"
}
```

**Response:**
```json
{
  "access_token": "jwt-token",
  "refresh_token": "refresh-token",
  "token_type": "bearer",
  "expires_in": 1800
}
```

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
# Database
DATABASE_URL=postgresql+psycopg2://admin:admin123@db:5432/syriagpt

# JWT
SECRET_KEY=your-super-secret-jwt-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Email
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM=noreply@syriagpt.com

# Google OAuth
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:9000/auth/google/callback

# Frontend
FRONTEND_URL=http://localhost:3000
```

## Database Schema

### Tables Created:
- `users` - User accounts
- `email_verifications` - Email verification tokens
- `password_resets` - Password reset tokens
- `refresh_tokens` - Refresh tokens for sessions

## Security Features

- Password hashing with bcrypt
- JWT access tokens with expiration
- Refresh token rotation
- Email verification requirement
- Password reset with time-limited tokens
- CORS configuration
- Input validation with Pydantic
- SQL injection protection with SQLAlchemy ORM

## Testing

Run the test script to verify API functionality:

```bash
python test_auth.py
```

## Running the Application

### With Docker:
```bash
docker-compose up -d
```

### Manually:
```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

## Error Handling

The API returns standard HTTP status codes:
- `200` - Success
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error

Error responses follow this format:
```json
{
  "detail": "Error message description"
}
```

## Rate Limiting & Security Considerations

For production deployment, consider implementing:
- Rate limiting on authentication endpoints
- Account lockout after failed attempts
- HTTPS enforcement
- Environment-specific CORS settings
- Database connection pooling
- Monitoring and logging
- Regular security audits