"""User domain entity - core business logic."""

from typing import Optional
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID
from enum import Enum


class UserStatus(Enum):
    """User account status enum."""
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


@dataclass
class User:
    """User domain entity representing core user business object."""
    
    id: Optional[UUID] = None
    email: str = ""
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    password_hash: Optional[str] = None
    google_id: Optional[str] = None
    facebook_id: Optional[str] = None
    is_email_verified: bool = False
    is_phone_verified: bool = False
    two_factor_enabled: bool = False
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.last_name:
            return self.last_name
        return ""
    
    @property
    def is_verified(self) -> bool:
        """Check if user is verified (email or phone)."""
        return self.is_email_verified or self.is_phone_verified
    
    @property
    def can_login(self) -> bool:
        """Check if user can log in."""
        return (
            self.is_active and 
            self.status in [UserStatus.ACTIVE, UserStatus.PENDING_VERIFICATION] and
            (self.password_hash or self.google_id or self.facebook_id)
        )
    
    def activate(self) -> None:
        """Activate user account."""
        self.is_active = True
        self.status = UserStatus.ACTIVE
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        self.is_active = False
        self.status = UserStatus.INACTIVE
    
    def verify_email(self) -> None:
        """Mark email as verified and activate if needed."""
        self.is_email_verified = True
        if self.status == UserStatus.PENDING_VERIFICATION:
            self.status = UserStatus.ACTIVE
    
    def verify_phone(self) -> None:
        """Mark phone as verified and activate if needed."""
        self.is_phone_verified = True
        if self.status == UserStatus.PENDING_VERIFICATION:
            self.status = UserStatus.ACTIVE
    
    def enable_two_factor(self) -> None:
        """Enable two-factor authentication."""
        if not self.is_verified:
            raise ValueError("User must be verified to enable 2FA")
        self.two_factor_enabled = True
    
    def disable_two_factor(self) -> None:
        """Disable two-factor authentication."""
        self.two_factor_enabled = False
    
    def link_google_account(self, google_id: str) -> None:
        """Link Google account to user."""
        if not google_id:
            raise ValueError("Google ID cannot be empty")
        self.google_id = google_id
    
    def link_facebook_account(self, facebook_id: str) -> None:
        """Link Facebook account to user."""
        if not facebook_id:
            raise ValueError("Facebook ID cannot be empty")
        self.facebook_id = facebook_id
    
    def unlink_google_account(self) -> None:
        """Unlink Google account from user."""
        if not self.password_hash and not self.facebook_id:
            raise ValueError("Cannot unlink Google account - no other login method available")
        self.google_id = None
    
    def unlink_facebook_account(self) -> None:
        """Unlink Facebook account from user."""
        if not self.password_hash and not self.google_id:
            raise ValueError("Cannot unlink Facebook account - no other login method available")
        self.facebook_id = None