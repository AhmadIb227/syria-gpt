# Syria GPT API - Auth Setup (US-006)

This repo includes a basic authentication stack: JWT login, optional 2FA challenge, and Alembic migration for `users`.

## Endpoints

- POST `/auth/login`
  - Request:
    `{ "email": "user@example.com", "password": "secret", "remember_me": true, "two_factor_code": "123456" }`
  - Responses:
    - 200: `{ "access_token": "...", "token_type": "bearer", "expires_in": 2592000 }`
    - 402: `{ "requires_2fa": true, "message": "Two-factor authentication required. Provide the 2FA code." }`
    - 401: Invalid credentials

- GET `/auth/providers`
  - Returns supported social providers (configure via OAuth later)

## Migrations

- Initialize DB (inside Docker): `alembic upgrade head`

## Notes

- Set `JWT_SECRET_KEY` via environment for production.
- `users` table migration is provided in `alembic/versions`.

