from sqlalchemy.orm import Session
from typing import Optional
from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: str) -> Optional[User]:
        try:
            return self.db.get(User, user_id)
        except TypeError:
            # For older SQLAlchemy fallback (shouldn't hit with v2)
            return self.db.query(User).filter(User.id == user_id).first()

    def create(self, *, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


