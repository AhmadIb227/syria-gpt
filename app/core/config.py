import os
from datetime import timedelta


class Settings:
    # Ideally load from environment or .env
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "change-this-secret-in-prod")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REMEMBER_ME_EXPIRE_DAYS: int = int(os.getenv("REMEMBER_ME_EXPIRE_DAYS", "30"))
    SESSION_SECRET_KEY: str = os.getenv("SESSION_SECRET_KEY", "change-this-session-secret")
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    # Google OAuth
    GOOGLE_CLIENT_ID: str | None = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str | None = os.getenv("GOOGLE_CLIENT_SECRET")

    @property
    def access_token_expire(self) -> timedelta:
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def remember_me_expire(self) -> timedelta:
        return timedelta(days=self.REMEMBER_ME_EXPIRE_DAYS)


settings = Settings()


