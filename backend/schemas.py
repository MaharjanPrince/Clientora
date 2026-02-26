from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional, List, Dict
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
    phone_no: Optional[str] = None  # making this optional
    company_name: Optional[str] = None


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_no: Optional[str] = None
    company_name: Optional[str] = None


# Contact Response
class ContactResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    company_name: Optional[str] = None
    phone_no: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Note Creation
class NoteCreation(BaseModel):
    title: str
    content: str


# Note Response
class NoteResponse(BaseModel):
    id: UUID
    contact_id: UUID
    title: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class DealCreate(BaseModel):
    title: str
    contact_id: UUID
    amount: Decimal
    stage: Literal["lead", "proposal", "negotiation", "won", "lost"] = "lead"

class DealUpdate(BaseModel):
    title: Optional[str] = None
    amount: Optional[Decimal] = None
    stage: Optional[Literal["lead", "proposal", "negotiation", "won", "lost"]] = (
        None
    )

class DealResponse(BaseModel):
    id: UUID
    user_id: UUID
    contact_id: UUID
    title: str
    amount: Decimal
    stage: str
    created_at: datetime
    updated_at: Optional[datetime] = None  # updated_at can be null initially

    model_config = ConfigDict(from_attributes=True)

class StageStats(BaseModel):
    """Stats for a single pipeline stage"""
    count: int
    total_value: Decimal
    deals: List[DealResponse]

class PipelineResponse(BaseModel):
    """Full pipeline view with all stages"""
    total_value: Decimal
    deals_by_stage: Dict[str, StageStats]


class ContactContext(BaseModel):
    contact_id: str
    contact_name: str
    last_interaction: str
    days_since_contact: int
    summary: str
    last_topic: Optional[str] = None
    decision_points: Optional[List[str]] = []
    commitments: Optional[List[str]] = []
    next_action: str


class StageStats(BaseModel):
    """Stats for a pipeline stage"""
    count: int
    total_value: Decimal

class ContactNeedingFollowup(BaseModel):
    """Contact that needs attention"""
    id: str
    name: str
    company_name: Optional[str]
    email: str
    days_since_contact: int
    last_note_date: str

class RecentActivity(BaseModel):
    """Recent activity item"""
    type: str  # "note_added" or "deal_updated"
    date: str
    contact_name: str
    contact_id: str
    days_ago: int
    # Note-specific fields
    note_title: Optional[str] = None
    # Deal-specific fields
    deal_title: Optional[str] = None
    deal_stage: Optional[str] = None
    deal_amount: Optional[Decimal] = None

class DashboardResponse(BaseModel):
    """Complete dashboard data"""
    total_pipeline_value: Decimal
    deals_by_stage: Dict[str, StageStats]
    contacts_needing_followup: List[ContactNeedingFollowup]
    recent_activity: List[RecentActivity]