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

class ConversationInput(BaseModel):
    """User pastes raw convo text"""
    raw_text: str = Field(..., min_length=10, max_length=10000, description="Raw conversation text from user")

    class config:
        json_schema_extra = {
            "example": {
                "raw_text": "Had a call with John from Acme. He wants pricing for enterprise plan. Said he'll discuss with team next week. Seemed cautious about budget."
            }
        }

class DealInsight(BaseModel):
    """AI-powered deal insights(The improved UI version)"""

    #Contact info extracted
    contact_name: Optional[str] = None
    company: Optional[str] = None
    contact_email: Optional[str] = None

    #Status
    status: str = "Warm Lead" #Warm/Cold/Hot Lead

    #whats happening section
    summary: str
    blocker: Optional[str] = None

    #Timing section
    decision_expected: Optional[str] = None
    window_closes: Optional[str] = None

    #Action section
    next_action: str
    next_action_date: Optional[str] = None

    #Why this matters
    reasoning: str

    #Signal Strength
    signal_strength: str = "3/5" #1/5 to 5/5
    signal_factors: List[str] = []

    class Config:
        json_schema_extra = {
            "example": {
                "contact_name": "John",
                "company": "Acme Corp",
                "status": "Warm lead",
                "summary": "Interested in enterprise plan pricing. Will decide next week with team.",
                "blocker": "Budget concerns",
                "decision_expected": "Next week (by March 28)",
                "window_closes": "Friday, March 26",
                "next_action": "Follow up Thursday, March 25 — catch them before the decision",
                "reasoning": "Clear intent + defined timeline + budget concern mentioned = high conversion if you address pricing objections now",
                "signal_strength": "3/5",
                "signal_factors": ["Clear intent (wants pricing)", "Defined timeline (next week)", "Budget concern mentioned"]
            }
        }

class ConversationAnalysisResponse(BaseModel):
    conversation_id: str
    deal_insights: DealInsight  # changed from deal_insight
    raw_text: str
    created_at: str
    suggest_create_contact: bool = True