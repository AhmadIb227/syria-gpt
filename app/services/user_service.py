from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash
from app.models.user import User
import secrets


class UserService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = UserRepository(db)

    def register(self, *, email: str, password: str, phone_number: str | None = None) -> User:
        existing = self.repo.get_by_email(email)
        if existing:
            raise ValueError("Email already in use")
        password_hash = get_password_hash(password)
        user = User(email=email, password_hash=password_hash, phone_number=phone_number)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # Email verification token generation (demo: store in user.token)
    def issue_email_verification(self, *, email: str) -> str:
        user = self.repo.get_by_email(email)
        if not user:
            raise ValueError("User not found")
        token = secrets.token_urlsafe(24)
        user.token = token
        self.db.add(user)
        self.db.commit()
        return token

    def verify_email(self, *, token: str) -> User:
        user = self.db.query(User).filter(User.token == token).first()
        if not user:
            raise ValueError("Invalid token")
        user.is_email_verified = True
        user.status = "active"
        user.token = None
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # Password reset token
    def issue_password_reset(self, *, email: str) -> str:
        user = self.repo.get_by_email(email)
        if not user:
            raise ValueError("User not found")
        token = secrets.token_urlsafe(24)
        user.reset_token = token
        self.db.add(user)
        self.db.commit()
        return token

    def reset_password(self, *, token: str, new_password: str) -> User:
        user = self.db.query(User).filter(User.reset_token == token).first()
        if not user:
            raise ValueError("Invalid token")
        user.password_hash = get_password_hash(new_password)
        user.reset_token = None
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


