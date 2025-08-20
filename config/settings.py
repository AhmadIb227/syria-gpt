import sys
from typing import List
from decouple import config


class Settings:
    """Application settings with environment variable support and validation."""

    # Environment
    ENVIRONMENT: str = config("ENVIRONMENT", default="development")
    DEBUG: bool = ENVIRONMENT == "development"

    # Database Configuration
    DATABASE_URL: str = config("DATABASE_URL", default="sqlite:///./syria_gpt.db")

    # Security Configuration
    SECRET_KEY: str = config("SECRET_KEY", default="3e8c7f51e5bd5dac5ba401b1125d43fb")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    REFRESH_TOKEN_EXPIRE_DAYS: int = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7, cast=int)
    EMAIL_VERIFICATION_EXPIRE_HOURS: int = config(
        "EMAIL_VERIFICATION_EXPIRE_HOURS", default=24, cast=int
    )
    PASSWORD_RESET_EXPIRE_HOURS: int = config("PASSWORD_RESET_EXPIRE_HOURS", default=1, cast=int)

    # Email Configuration
    SMTP_SERVER: str = config("SMTP_SERVER", default="smtp.gmail.com")
    SMTP_PORT: int = config("SMTP_PORT", default=587, cast=int)
    SMTP_USERNAME: str = config("SMTP_USERNAME", default="")
    SMTP_PASSWORD: str = config("SMTP_PASSWORD", default="")
    EMAIL_FROM: str = config("EMAIL_FROM", default="noreply@syriagpt.com")

    # OAuth Configuration
    GOOGLE_CLIENT_ID: str = config("GOOGLE_CLIENT_ID", default="")
    GOOGLE_CLIENT_SECRET: str = config("GOOGLE_CLIENT_SECRET", default="")
    GOOGLE_REDIRECT_URI: str = config(
        "GOOGLE_REDIRECT_URI", default="http://localhost:9000/auth/google/callback"
    )

    # Facebook OAuth Configuration
    FACEBOOK_APP_ID: str = config("FACEBOOK_APP_ID", default="")
    FACEBOOK_APP_SECRET: str = config("FACEBOOK_APP_SECRET", default="")
    FACEBOOK_REDIRECT_URI: str = config(
        "FACEBOOK_REDIRECT_URI", default="http://localhost:9000/auth/facebook/callback"
    )

    # Frontend Configuration
    FRONTEND_URL: str = config("FRONTEND_URL", default="http://localhost:3000")

    # CORS Origins
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        """Get allowed CORS origins based on environment."""
        if self.ENVIRONMENT == "production":
            return [self.FRONTEND_URL]
        return [
            self.FRONTEND_URL,
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ]

    def validate(self) -> None:
        """Validate critical settings."""
        errors = []

        if not self.SECRET_KEY or len(self.SECRET_KEY) < 32:
            errors.append("SECRET_KEY must be at least 32 characters long")

        if self.ENVIRONMENT == "production":
            if not self.GOOGLE_CLIENT_ID:
                errors.append("GOOGLE_CLIENT_ID is required in production")
            if not self.GOOGLE_CLIENT_SECRET:
                errors.append("GOOGLE_CLIENT_SECRET is required in production")
            if not self.FACEBOOK_APP_ID:
                errors.append("FACEBOOK_APP_ID is required in production")
            if not self.FACEBOOK_APP_SECRET:
                errors.append("FACEBOOK_APP_SECRET is required in production")
            if not self.SMTP_USERNAME or not self.SMTP_PASSWORD:
                errors.append("SMTP credentials are required in production")

        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(
                f"- {error}" for error in errors
            )
            print(error_msg, file=sys.stderr)
            if self.ENVIRONMENT == "production":
                sys.exit(1)


settings = Settings()
settings.validate()
