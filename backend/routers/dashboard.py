from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from ..import models, schemas
from ..dependencies import get_current_user
from ..database import get_db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

#Routing
@router.get("/", response_model=schemas.DashboardResponse)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """Get complete dashboard overview"""
    #Pipeline Statistics (all deals for this user)
    deals = db.query(models.Deal).filter(models.Deal.user_id == current_user.id).all()

    #initializing stage stats
    stages= ["lead", "proposal", "negotiation", "won", "lost"]
    deals_by_stage = {
        stage: {
            "count": 0,
            "total_value": Decimal(0)
        } for stage in stages
    }
    # Group deals by stage
    for deal in deals:
        if deal.stage in deals_by_stage:
            deals_by_stage[deal.stage]["count"] += 1
            deals_by_stage[deal.stage]["total_value"] += deal.amount
    
    # Calculate total pipeline value (exclude lost deals)
    total_pipeline_value = sum(
        deal.amount for deal in deals
        if deal.stage != "lost"
    )

    # Part 2: Contacts Needing Follow-Up
    # Find contacts with no recent notes (30+ days)
    now_uct = datetime.now(timezone.utc)
    thirty_days_ago = now_uct - timedelta(days=30)
    
    # Get all contacts
    contacts = db.query(models.Contact).filter(
        models.Contact.user_id == current_user.id
    ).all()
    
    contacts_needing_followup = []
    
    for contact in contacts:
        # Get most recent note for this contact
        last_note = db.query(models.Note).filter(
            models.Note.contact_id == contact.id
        ).order_by(
            models.Note.created_at.desc()
        ).first()
        
        # If no notes OR last note is old
        if not last_note or last_note.created_at < thirty_days_ago:
            days_since = (now_uct - last_note.created_at).days if last_note else 999
            
            contacts_needing_followup.append({
                "id": str(contact.id),
                "name": contact.name,
                "company_name": contact.company_name,
                "email": contact.email,
                "days_since_contact": days_since,
                "last_note_date": last_note.created_at.strftime("%B %d, %Y") if last_note else "Never contacted"
            })
    
    # Sort by days since contact (most urgent first)
    contacts_needing_followup.sort(key=lambda x: x["days_since_contact"], reverse=True)

    #Recent activity feed(Getting recent notes)
    recent_notes = db.query(models.Note).join(models.Contact).filter(models.Contact.user_id == current_user.id).order_by(models.Note.created_at.desc()).limit(10).all()

    #Recent deal updates 
    recent_deals = db.query(models.Deal).filter(models.Deal.user_id == current_user.id).order_by(models.Deal.created_at.desc()).limit(10).all()

    #Combining and sort by date
    activity = []

    #Add notes to activity 
    for note in recent_notes:
        contact = db.query(models.Contact).filter(models.Contact.id == note.contact_id).first()
        activity.append({
            "type": "note_added",
            "date": note.created_at,
            "contact_name": contact.name if contact else "Unknown",
            "contact_id": str(note.contact_id),
            "note_title": note.title,
            "days_ago": (datetime.now(timezone.utc) - note.created_at).days
        })

    #Add deals to activity 
    for deal in recent_deals:
        contact = db.query(models.Contact).filter(models.Contact.id == deal.contact_id).first()
        activity.append({
            "type": "deal_added",
            "date": deal.created_at,
            "contact_name": contact.name if contact else "Unknown",
            "contact_id": str(deal.contact_id),
            "deal_amount": deal.amount,
            "deal_stage": deal.stage,
            "days_ago": (datetime.now(timezone.utc) - deal.created_at).days
        })

    #Sort activity by date (newest first)
    activity.sort(key=lambda x: x["date"], reverse=True)
    # Take top 15 items
    recent_activity = activity[:15]
    
    # Format dates for display
    for item in recent_activity:
        item["date"] = item["date"].strftime("%B %d, %Y at %I:%M %p")

    return {  # noqa: F706
        "total_pipeline_value": total_pipeline_value,
        "deals_by_stage": deals_by_stage,
        "contacts_needing_followup": contacts_needing_followup,
        "recent_activity": recent_activity
    }