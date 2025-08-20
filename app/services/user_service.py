from sqlalchemy.orm import Session
from app.repositories.user_repository import UserRepository
from app.core.security import get_password_hash
from app.models.user import User


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


