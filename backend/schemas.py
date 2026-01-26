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
class UserResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    created_at: datetime
    is_active: bool

    # This allows Pydantic to read data from SQLAlchemy models
    model_config = ConfigDict(from_attributes=True)


# Contact Creation
class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    phone_no: int


# Contact Response
class ContactResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Note Creation
class NoteCreation(BaseModel):
    title: str
    content: str


# Note Response
class NoteResponse(BaseModel):
    title: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
