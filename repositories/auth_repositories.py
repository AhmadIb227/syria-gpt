"""Authentication-related repositories."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_

from config.model import EmailVerification, PasswordReset, RefreshToken
from repositories.base import BaseRepository


class EmailVerificationRepository(BaseRepository[EmailVerification]):
    """Repository for email verification tokens."""
    
    def __init__(self, db: Session):
        """Initialize email verification repository."""
        super().__init__(db, EmailVerification)
    
    def create_verification(self, user_id: UUID, token: str, expires_hours: int = 24) -> EmailVerification:
        """Create a new email verification token."""
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
        verification_data = {
            'user_id': user_id,
            'token': token,
            'expires_at': expires_at,
            'is_used': False
        }
        
        return self.create(verification_data)
    
    def get_by_token(self, token: str) -> Optional[EmailVerification]:
        """Get verification by token."""
        return self.get_by_field('token', token)
    
    def get_by_user_id(self, user_id: UUID) -> List[EmailVerification]:
        """Get all verifications for a user."""
        return self.get_many_by_field('user_id', user_id)
    
    def get_active_verification(self, user_id: UUID) -> Optional[EmailVerification]:
        """Get active (unused, non-expired) verification for user."""
        return self.db.query(EmailVerification).filter(
            and_(
                EmailVerification.user_id == user_id,
                EmailVerification.is_used == False,
                EmailVerification.expires_at > datetime.utcnow()
            )
        ).order_by(EmailVerification.created_at.desc()).first()
    
    def mark_as_used(self, token: str) -> Optional[EmailVerification]:
        """Mark verification token as used."""
        verification = self.get_by_token(token)
        if verification:
            return self.update(verification.id, {'is_used': True})
        return None
    
    def is_valid_token(self, token: str) -> bool:
        """Check if token is valid (exists, not used, not expired)."""
        verification = self.get_by_token(token)
        if not verification:
            return False
        
        return (
            not verification.is_used and 
            verification.expires_at > datetime.utcnow()
        )
    
    def cleanup_expired(self) -> int:
        """Delete expired verification tokens."""
        expired_tokens = self.db.query(EmailVerification).filter(
            EmailVerification.expires_at <= datetime.utcnow()
        ).all()
        
        count = len(expired_tokens)
        for token in expired_tokens:
            self.db.delete(token)
        
        self.db.commit()
        return count
    
    def revoke_user_tokens(self, user_id: UUID) -> int:
        """Mark all user's verification tokens as used."""
        tokens = self.db.query(EmailVerification).filter(
            and_(
                EmailVerification.user_id == user_id,
                EmailVerification.is_used == False
            )
        ).all()
        
        for token in tokens:
            token.is_used = True
        
        self.db.commit()
        return len(tokens)


class PasswordResetRepository(BaseRepository[PasswordReset]):
    """Repository for password reset tokens."""
    
    def __init__(self, db: Session):
        """Initialize password reset repository."""
        super().__init__(db, PasswordReset)
    
    def create_reset_token(self, user_id: UUID, token: str, expires_hours: int = 1) -> PasswordReset:
        """Create a new password reset token."""
        expires_at = datetime.utcnow() + timedelta(hours=expires_hours)
        
        reset_data = {
            'user_id': user_id,
            'token': token,
            'expires_at': expires_at,
            'is_used': False
        }
        
        return self.create(reset_data)
    
    def get_by_token(self, token: str) -> Optional[PasswordReset]:
        """Get password reset by token."""
        return self.get_by_field('token', token)
    
    def get_by_user_id(self, user_id: UUID) -> List[PasswordReset]:
        """Get all password resets for a user."""
        return self.get_many_by_field('user_id', user_id)
    
    def get_active_reset(self, user_id: UUID) -> Optional[PasswordReset]:
        """Get active (unused, non-expired) reset token for user."""
        return self.db.query(PasswordReset).filter(
            and_(
                PasswordReset.user_id == user_id,
                PasswordReset.is_used == False,
                PasswordReset.expires_at > datetime.utcnow()
            )
        ).order_by(PasswordReset.created_at.desc()).first()
    
    def mark_as_used(self, token: str) -> Optional[PasswordReset]:
        """Mark reset token as used."""
        reset = self.get_by_token(token)
        if reset:
            return self.update(reset.id, {'is_used': True})
        return None
    
    def is_valid_token(self, token: str) -> bool:
        """Check if token is valid (exists, not used, not expired)."""
        reset = self.get_by_token(token)
        if not reset:
            return False
        
        return (
            not reset.is_used and 
            reset.expires_at > datetime.utcnow()
        )
    
    def cleanup_expired(self) -> int:
        """Delete expired reset tokens."""
        expired_tokens = self.db.query(PasswordReset).filter(
            PasswordReset.expires_at <= datetime.utcnow()
        ).all()
        
        count = len(expired_tokens)
        for token in expired_tokens:
            self.db.delete(token)
        
        self.db.commit()
        return count
    
    def revoke_user_tokens(self, user_id: UUID) -> int:
        """Mark all user's reset tokens as used."""
        tokens = self.db.query(PasswordReset).filter(
            and_(
                PasswordReset.user_id == user_id,
                PasswordReset.is_used == False
            )
        ).all()
        
        for token in tokens:
            token.is_used = True
        
        self.db.commit()
        return len(tokens)


class RefreshTokenRepository(BaseRepository[RefreshToken]):
    """Repository for refresh tokens."""
    
    def __init__(self, db: Session):
        """Initialize refresh token repository."""
        super().__init__(db, RefreshToken)
    
    def create_refresh_token(self, user_id: UUID, token: str, expires_days: int = 7) -> RefreshToken:
        """Create a new refresh token."""
        expires_at = datetime.utcnow() + timedelta(days=expires_days)
        
        token_data = {
            'user_id': user_id,
            'token': token,
            'expires_at': expires_at,
            'is_revoked': False
        }
        
        return self.create(token_data)
    
    def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string."""
        return self.get_by_field('token', token)
    
    def get_by_user_id(self, user_id: UUID) -> List[RefreshToken]:
        """Get all refresh tokens for a user."""
        return self.get_many_by_field('user_id', user_id)
    
    def get_active_tokens(self, user_id: UUID) -> List[RefreshToken]:
        """Get active (non-revoked, non-expired) tokens for user."""
        return self.db.query(RefreshToken).filter(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
        ).order_by(RefreshToken.created_at.desc()).all()
    
    def revoke_token(self, token: str) -> Optional[RefreshToken]:
        """Revoke a refresh token."""
        refresh_token = self.get_by_token(token)
        if refresh_token:
            return self.update(refresh_token.id, {'is_revoked': True})
        return None
    
    def revoke_user_tokens(self, user_id: UUID) -> int:
        """Revoke all user's refresh tokens."""
        tokens = self.db.query(RefreshToken).filter(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False
            )
        ).all()
        
        for token in tokens:
            token.is_revoked = True
        
        self.db.commit()
        return len(tokens)
    
    def is_valid_token(self, token: str) -> bool:
        """Check if token is valid (exists, not revoked, not expired)."""
        refresh_token = self.get_by_token(token)
        if not refresh_token:
            return False
        
        return (
            not refresh_token.is_revoked and 
            refresh_token.expires_at > datetime.utcnow()
        )
    
    def cleanup_expired(self) -> int:
        """Delete expired refresh tokens."""
        expired_tokens = self.db.query(RefreshToken).filter(
            RefreshToken.expires_at <= datetime.utcnow()
        ).all()
        
        count = len(expired_tokens)
        for token in expired_tokens:
            self.db.delete(token)
        
        self.db.commit()
        return count
    
    def cleanup_revoked(self) -> int:
        """Delete revoked refresh tokens older than 30 days."""
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_revoked_tokens = self.db.query(RefreshToken).filter(
            and_(
                RefreshToken.is_revoked == True,
                RefreshToken.created_at <= cutoff_date
            )
        ).all()
        
        count = len(old_revoked_tokens)
        for token in old_revoked_tokens:
            self.db.delete(token)
        
        self.db.commit()
        return count
    
    def get_token_count_by_user(self, user_id: UUID) -> int:
        """Get count of active tokens for a user."""
        return self.db.query(RefreshToken).filter(
            and_(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
        ).count()


class AuthRepositoryManager:
    """Manager class that provides access to all auth repositories."""
    
    def __init__(self, db: Session):
        """Initialize all auth repositories."""
        self.db = db
        self.email_verification = EmailVerificationRepository(db)
        self.password_reset = PasswordResetRepository(db)
        self.refresh_token = RefreshTokenRepository(db)
    
    def cleanup_expired_tokens(self) -> Dict[str, int]:
        """Cleanup expired tokens across all repositories."""
        return {
            'email_verifications': self.email_verification.cleanup_expired(),
            'password_resets': self.password_reset.cleanup_expired(),
            'refresh_tokens': self.refresh_token.cleanup_expired(),
            'revoked_tokens': self.refresh_token.cleanup_revoked(),
        }
    
    def revoke_all_user_tokens(self, user_id: UUID) -> Dict[str, int]:
        """Revoke all tokens for a user."""
        return {
            'email_verifications': self.email_verification.revoke_user_tokens(user_id),
            'password_resets': self.password_reset.revoke_user_tokens(user_id),
            'refresh_tokens': self.refresh_token.revoke_user_tokens(user_id),
        }