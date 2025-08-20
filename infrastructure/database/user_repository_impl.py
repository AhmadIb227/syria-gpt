"""User repository implementation using SQLAlchemy."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from domain.entities import User, UserStatus
from domain.interfaces import IUserRepository
from config.model import User as UserModel


class UserRepositoryImpl(IUserRepository):
    """SQLAlchemy implementation of user repository."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def _model_to_entity(self, user_model: UserModel) -> User:
        """Convert SQLAlchemy model to domain entity."""
        if not user_model:
            return None
        
        return User(
            id=user_model.id,
            email=user_model.email or "",
            first_name=user_model.first_name,
            last_name=user_model.last_name,
            phone_number=user_model.phone_number,
            password_hash=user_model.password_hash,
            google_id=user_model.google_id,
            facebook_id=user_model.facebook_id,
            is_email_verified=user_model.is_email_verified or False,
            is_phone_verified=user_model.is_phone_verified or False,
            two_factor_enabled=user_model.two_factor_enabled or False,
            status=UserStatus(user_model.status) if user_model.status else UserStatus.PENDING_VERIFICATION,
            is_active=user_model.is_active if user_model.is_active is not None else True,
            created_at=user_model.created_at,
            updated_at=user_model.updated_at
        )
    
    def _entity_to_model_data(self, user: User) -> Dict[str, Any]:
        """Convert domain entity to model data."""
        return {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": user.phone_number,
            "password_hash": user.password_hash,
            "google_id": user.google_id,
            "facebook_id": user.facebook_id,
            "is_email_verified": user.is_email_verified,
            "is_phone_verified": user.is_phone_verified,
            "two_factor_enabled": user.two_factor_enabled,
            "status": user.status.value if isinstance(user.status, UserStatus) else user.status,
            "is_active": user.is_active
        }
    
    async def create(self, user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        # Set defaults
        user_data.setdefault('is_email_verified', False)
        user_data.setdefault('is_phone_verified', False)
        user_data.setdefault('two_factor_enabled', False)
        user_data.setdefault('is_active', True)
        
        user_model = UserModel(**user_data)
        self.db.add(user_model)
        self.db.commit()
        self.db.refresh(user_model)
        
        return self._model_to_entity(user_model)
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._model_to_entity(user_model) if user_model else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        user_model = self.db.query(UserModel).filter(UserModel.email == email).first()
        return self._model_to_entity(user_model) if user_model else None
    
    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        user_model = self.db.query(UserModel).filter(UserModel.google_id == google_id).first()
        return self._model_to_entity(user_model) if user_model else None
    
    async def get_by_facebook_id(self, facebook_id: str) -> Optional[User]:
        """Get user by Facebook ID."""
        user_model = self.db.query(UserModel).filter(UserModel.facebook_id == facebook_id).first()
        return self._model_to_entity(user_model) if user_model else None
    
    async def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        """Get user by phone number."""
        user_model = self.db.query(UserModel).filter(UserModel.phone_number == phone_number).first()
        return self._model_to_entity(user_model) if user_model else None
    
    async def update(self, user_id: UUID, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user data."""
        user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user_model:
            return None
        
        for key, value in update_data.items():
            if hasattr(user_model, key):
                setattr(user_model, key, value)
        
        self.db.commit()
        self.db.refresh(user_model)
        
        return self._model_to_entity(user_model)
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete user."""
        user_model = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user_model:
            return False
        
        self.db.delete(user_model)
        self.db.commit()
        return True
    
    async def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        return self.db.query(UserModel).filter(UserModel.email == email).first() is not None
    
    async def phone_exists(self, phone_number: str) -> bool:
        """Check if phone number already exists."""
        return self.db.query(UserModel).filter(UserModel.phone_number == phone_number).first() is not None
    
    async def google_id_exists(self, google_id: str) -> bool:
        """Check if Google ID already exists."""
        return self.db.query(UserModel).filter(UserModel.google_id == google_id).first() is not None
    
    async def facebook_id_exists(self, facebook_id: str) -> bool:
        """Check if Facebook ID already exists."""
        return self.db.query(UserModel).filter(UserModel.facebook_id == facebook_id).first() is not None
    
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users."""
        user_models = (
            self.db.query(UserModel)
            .filter(UserModel.is_active == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._model_to_entity(model) for model in user_models]
    
    async def get_verified_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get email-verified users."""
        user_models = (
            self.db.query(UserModel)
            .filter(UserModel.is_email_verified == True)
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [self._model_to_entity(model) for model in user_models]