from decouple import config

class Settings:
    DATABASE_URL = config("DATABASE_URL", default="postgresql+psycopg2://admin:admin123@db:5432/syriagpt")
    SECRET_KEY = config("SECRET_KEY", default="your-secret-key-here-change-in-production")
    ALGORITHM = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    REFRESH_TOKEN_EXPIRE_DAYS = config("REFRESH_TOKEN_EXPIRE_DAYS", default=7, cast=int)
    EMAIL_VERIFICATION_EXPIRE_HOURS = config("EMAIL_VERIFICATION_EXPIRE_HOURS", default=24, cast=int)
    PASSWORD_RESET_EXPIRE_HOURS = config("PASSWORD_RESET_EXPIRE_HOURS", default=1, cast=int)
    
    SMTP_SERVER = config("SMTP_SERVER", default="smtp.gmail.com")
    SMTP_PORT = config("SMTP_PORT", default=587, cast=int)
    SMTP_USERNAME = config("SMTP_USERNAME", default="")
    SMTP_PASSWORD = config("SMTP_PASSWORD", default="")
    EMAIL_FROM = config("EMAIL_FROM", default="noreply@syriagpt.com")
    
    GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID", default="")
    GOOGLE_CLIENT_SECRET = config("GOOGLE_CLIENT_SECRET", default="")
    GOOGLE_REDIRECT_URI = config("GOOGLE_REDIRECT_URI", default="http://localhost:9000/auth/google/callback")
    
    FRONTEND_URL = config("FRONTEND_URL", default="http://localhost:3000")

settings = Settings()