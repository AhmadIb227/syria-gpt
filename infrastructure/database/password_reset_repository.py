from sqlalchemy.orm import Session
from uuid import UUID
from config.model import PasswordReset
from datetime import datetime

class PasswordResetRepository:
    """Repository to handle password reset tokens."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: dict) -> PasswordReset:
        """Create a new password reset record."""
        record = PasswordReset(**data)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_token(self, token: str) -> PasswordReset | None:
        """Retrieve password reset record by token."""
        return self.db.query(PasswordReset).filter_by(token=token).first()

    def mark_used(self, token_id: UUID) -> None:
        """Mark the token as used."""
        record = self.db.query(PasswordReset).get(token_id)
        if record:
            record.is_used = True
            self.db.commit()
