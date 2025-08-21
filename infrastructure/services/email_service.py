"""Email service for sending emails."""

import asyncio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        # Email configuration would come from settings
        pass
    
    async def send_verification_email(self, email: str, token: str) -> None:
        """Send email verification email."""
        # In a real implementation, this would send an actual email
        logger.info(f"Sending verification email to {email} with token {token[:10]}...")
        
        # Simulate async email sending
        await asyncio.sleep(0.1)
        
        logger.info(f"Verification email sent to {email}")
    
    async def send_password_reset_email(self, email: str, token: str) -> None:
        """Send password reset email."""
        logger.info(f"Sending password reset email to {email} with token {token[:10]}...")
        
        # Simulate async email sending
        await asyncio.sleep(0.1)
        
        logger.info(f"Password reset email sent to {email}")
    
    async def send_welcome_email(self, email: str, name: str) -> None:
        """Send welcome email to new user."""
        logger.info(f"Sending welcome email to {email} for {name}")
        
        # Simulate async email sending
        await asyncio.sleep(0.1)
        
        logger.info(f"Welcome email sent to {email}")

    async def send_2fa_code(self, email: str, code: str) -> None:
        """Send 2FA code email."""
        logger.info(f"Sending 2FA code to {email}: {code}")
        
        # Simulate async email sending
        await asyncio.sleep(0.1)
        
        logger.info(f"2FA code sent to {email}")
