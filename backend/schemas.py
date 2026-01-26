from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from pydantic.types import UUID1


# User registration Schema
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="password must contain ....")
    name: str


# Token
class Token(BaseModel):
    access_token: str
    token_type: str


# User response
# User response
class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime
    is_active: bool

    # This allows Pydantic to read data from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)
