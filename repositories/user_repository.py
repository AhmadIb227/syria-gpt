"""User repository implementation."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_

from config.model import User
from repositories.base import BaseRepository


class UserRepositoryInterface:
    """Interface for user repository operations."""
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        pass
    
    def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        pass
    
    def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        """Get user by phone number."""
        pass
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users."""
        pass
    
    def get_verified_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get email-verified users."""
        pass
    
    def search_users(self, query: str, skip: int = 0, limit: int = 10) -> List[User]:
        """Search users by name or email."""
        pass
    
    def update_verification_status(self, user_id: UUID, email_verified: bool = None, phone_verified: bool = None) -> Optional[User]:
        """Update user verification status."""
        pass
    
    def activate_user(self, user_id: UUID) -> Optional[User]:
        """Activate user account."""
        pass
    
    def deactivate_user(self, user_id: UUID) -> Optional[User]:
        """Deactivate user account."""
        pass


class UserRepository(BaseRepository[User], UserRepositoryInterface):
    """User repository with specialized user operations."""
    
    def __init__(self, db: Session):
        """Initialize user repository."""
        super().__init__(db, User)
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user with proper defaults."""
        # Set default status if not provided
        if 'status' not in user_data:
            user_data['status'] = 'pending_verification'
        
        # Ensure boolean fields have defaults
        user_data.setdefault('is_email_verified', False)
        user_data.setdefault('is_phone_verified', False)
        user_data.setdefault('two_factor_enabled', False)
        user_data.setdefault('is_active', True)
        
        return self.create(user_data)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.get_by_field('email', email)
    
    def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Get user by Google ID."""
        return self.get_by_field('google_id', google_id)
    
    def get_by_phone_number(self, phone_number: str) -> Optional[User]:
        """Get user by phone number."""
        return self.get_by_field('phone_number', phone_number)
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users."""
        return self.db.query(User).filter(
            User.is_active == True
        ).offset(skip).limit(limit).all()
    
    def get_verified_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get email-verified users."""
        return self.db.query(User).filter(
            User.is_email_verified == True
        ).offset(skip).limit(limit).all()
    
    def search_users(self, query: str, skip: int = 0, limit: int = 10) -> List[User]:
        """Search users by name or email."""
        search_term = f"%{query}%"
        return self.db.query(User).filter(
            or_(
                User.email.ilike(search_term),
                User.first_name.ilike(search_term),
                User.last_name.ilike(search_term)
            )
        ).offset(skip).limit(limit).all()
    
    def get_user_with_relations(self, user_id: UUID) -> Optional[User]:
        """Get user with all related data loaded."""
        return self.db.query(User).options(
            joinedload(User.email_verifications),
            joinedload(User.password_resets),
            joinedload(User.refresh_tokens)
        ).filter(User.id == user_id).first()
    
    def update_verification_status(self, user_id: UUID, email_verified: bool = None, phone_verified: bool = None) -> Optional[User]:
        """Update user verification status."""
        update_data = {}
        
        if email_verified is not None:
            update_data['is_email_verified'] = email_verified
            
        if phone_verified is not None:
            update_data['is_phone_verified'] = phone_verified
        
        # Update status based on verification
        if email_verified:
            update_data['status'] = 'active'
        
        if update_data:
            return self.update(user_id, update_data)
        
        return self.get_by_id(user_id)
    
    def activate_user(self, user_id: UUID) -> Optional[User]:
        """Activate user account."""
        return self.update(user_id, {
            'is_active': True,
            'status': 'active'
        })
    
    def deactivate_user(self, user_id: UUID) -> Optional[User]:
        """Deactivate user account."""
        return self.update(user_id, {
            'is_active': False,
            'status': 'inactive'
        })
    
    def enable_two_factor(self, user_id: UUID) -> Optional[User]:
        """Enable two-factor authentication for user."""
        return self.update(user_id, {'two_factor_enabled': True})
    
    def disable_two_factor(self, user_id: UUID) -> Optional[User]:
        """Disable two-factor authentication for user."""
        return self.update(user_id, {'two_factor_enabled': False})
    
    def update_google_id(self, user_id: UUID, google_id: str) -> Optional[User]:
        """Update user's Google ID for OAuth linking."""
        return self.update(user_id, {'google_id': google_id})
    
    def get_users_by_status(self, status: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by status."""
        return self.get_many_by_field('status', status, skip, limit)
    
    def count_active_users(self) -> int:
        """Count active users."""
        return self.count_by_field('is_active', True)
    
    def count_verified_users(self) -> int:
        """Count email-verified users."""
        return self.count_by_field('is_email_verified', True)
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists."""
        return self.db.query(User).filter(User.email == email).first() is not None
    
    def phone_exists(self, phone_number: str) -> bool:
        """Check if phone number already exists."""
        return self.db.query(User).filter(User.phone_number == phone_number).first() is not None
    
    def google_id_exists(self, google_id: str) -> bool:
        """Check if Google ID already exists."""
        return self.db.query(User).filter(User.google_id == google_id).first() is not None