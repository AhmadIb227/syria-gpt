"""Email service for sending emails."""

import asyncio
from typing import Dict, Any
import logging
from config.settings import settings
from email.message import EmailMessage
from aiosmtplib import SMTP

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails."""
    
    def __init__(self):
        # Email configuration would come from settings
        self.smtp_host = "smtp.gmail.com"
        self.smtp_port = 587
        self.username = settings.SMTP_USERNAME
        self.password = settings.SMTP_PASSWORD
        pass
    
    async def send_verification_email(self, email: str, token: str) -> None:
        """Send email verification email."""
        # In a real implementation, this would send an actual email
        logger.info(f"Sending verification email to {email} with token {token[:10]}...")
        
        # Simulate async email sending
        await asyncio.sleep(0.1)
        
        logger.info(f"Verification email sent to {email}")
    
    async def send_password_reset_email(self, recipient_email: str, token: str) -> None:
        """Send password reset email with token link."""
        reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

        message = EmailMessage()
        message["From"] = self.username
        message["To"] = recipient_email
        message["Subject"] = "إعادة تعيين كلمة المرور"
        message.set_content(
            f"مرحبًا،\n\nلتعيين كلمة المرور الجديدة، اضغط على الرابط أدناه:\n{reset_link}\n\n"
            f"سيكون الرابط صالحًا لمدة ساعة فقط.\n\n"
            f"إذا لم تطلب إعادة تعيين كلمة المرور، تجاهل هذا البريد."
        )

        try:
            smtp = SMTP(hostname=self.smtp_host, port=self.smtp_port, start_tls=True)
            await smtp.connect()
            await smtp.login(self.username, self.password)
            await smtp.send_message(message)
            await smtp.quit()
            logger.info(f"Password reset email sent to {recipient_email}")
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
    
    async def send_welcome_email(self, email: str, name: str) -> None:
        """Send welcome email to new user."""
        logger.info(f"Sending welcome email to {email} for {name}")
        
        # Simulate async email sending
        await asyncio.sleep(0.1)
        
        logger.info(f"Welcome email sent to {email}")