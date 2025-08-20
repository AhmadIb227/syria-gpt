from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    phone_number: Optional[str] = None
    is_email_verified: bool
    is_phone_verified: bool
    two_factor_enabled: bool
    status: str

    class Config:
        from_attributes = True


