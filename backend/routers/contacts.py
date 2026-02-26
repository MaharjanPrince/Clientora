from typing import List, Optional
from uuid import UUID

from click import prompt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import auth, database, models, schemas
import os
import json
from groq import Groq
from datetime import datetime, timezone

# from ..auth import get_current_user
from ..dependencies import get_current_user


#Initializing the Groq Client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

router = APIRouter(prefix="/contacts", tags=["contacts"])

# Dependency to get the database
get_db = database.get_db


@router.post("/", response_model=schemas.ContactResponse)
def create_contact(
    contact: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    new_contact = models.Contact(**contact.model_dump(), user_id=current_user.id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


@router.get("/", response_model=List[schemas.ContactResponse])
def get_contacts(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Contact).filter(models.Contact.user_id == current_user.id).all()
    )


@router.get("/{contact_id}", response_model=schemas.ContactResponse)
def get_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    contact = (
        db.query(models.Contact)
        .filter(
            models.Contact.id == contact_id, models.Contact.user_id == current_user.id
        )
        .first()
    )

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.put("/{contact_id}", response_model=schemas.ContactResponse)
def update_contact(
    contact_id: UUID,
    contact_update: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    contact = (
        db.query(models.Contact)
        .filter(
            models.Contact.id == contact_id, models.Contact.user_id == current_user.id
        )
        .first()
    )

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    # Update only fields that were provided
    update_data = contact_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(contact, field, value)

    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    contact = (
        db.query(models.Contact)
        .filter(
            models.Contact.id == contact_id, models.Contact.user_id == current_user.id
        )
        .first()
    )

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return None


@router.post("/{contact_id}/notes", response_model=schemas.NoteResponse)
def create_note(
    contact_id: UUID,
    note: schemas.NoteCreation,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Security check: If the user owns this contact or not
    contact = (
        db.query(models.Contact)
        .filter(
            models.Contact.id == contact_id, models.Contact.user_id == current_user.id
        )
        .first()
    )

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    new_note = models.Note(**note.model_dump(), contact_id=contact_id)
    db.add(new_note)
    db.commit()
    db.refresh(new_note)
    return new_note


@router.get("/{contact_id}/notes", response_model=List[schemas.NoteResponse])
def get_notes(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # SECURITY CHECK: Does the user own this contact?
    contact = (
        db.query(models.Contact)
        .filter(
            models.Contact.id == contact_id, models.Contact.user_id == current_user.id
        )
        .first()
    )

    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    return (
        db.query(models.Note)
        .filter(models.Note.contact_id == contact_id)
        .order_by(models.Note.created_at.desc())
        .all()
    )

#Security and Data Fetching
@router.get("/{contact_id}/context", response_model = schemas.ContactContext)
def get_contact_context(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """ Get AI  generated context summary for a contact based on their notes and interactions. """

    #Step 1: Security Check - Does the user own this contact?
    contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id, models.Contact.user_id == current_user.id
    ).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    #Step 2: Fetch all notes for this contact
    notes = (
        db.query(models.Note)
        .filter(models.Note.contact_id == contact_id)
        .order_by(models.Note.created_at.desc())
        .all()
    )

    #Step 3: handle case whwre there are no notes yet
    if not notes:
        return {
            "contact_id": str(contact_id),
            "contact_name": contact.name,
            "summary": "No conversation historyyet. Add notes to track interaction.",
            "next_action": "Have your first conversation and document it."
        }
    
    #Step 4: Format all notes into readable text for AI
    notes_text = "\n\n".join([
        f"Date: {note.created_at.strftime('%B %d, %Y')}\n"
        f"Title: {note.title}\n"
        f"Note: {note.content}"
        for note in notes
    ])

    # Step 5: Build the prompt for Groq
    prompt = f"""You are analyzing business conversation notes for a contact named {contact.name}.

    Your job: Provide a concise summary that helps prepare for the next interaction.

    CONVERSATION HISTORY:
    {notes_text}

    Analyze these notes and respond with a JSON object in this EXACT format:
    {{
    "summary": "2-3 sentence overview of the relationship and recent discussions",
    "last_topic": "What was discussed most recently",
    "decision_points": ["List of pending decisions or choices they're making"],
    "commitments": ["Things you promised to do"],
    "next_action": "Specific next step to move this forward"
    }}

    RULES:
    - Be concise and business-focused
    - Extract facts from the notes (don't make things up)
    - If a field has no info, use [] for arrays or brief statement for strings
    - Make next_action specific and actionable
    - Return ONLY valid JSON, no extra text"""

    #Step 6: Call Groq to analyze
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.1-8b-instant", #Fast, free model
            messages=[
                {
                "role": "system",
                "content": "You are a business relationship assistant. Analyze the conversation notes and provide a summary in the requested JSON format."
                },
                {
                "role": "user",
                "content": prompt
                }
            ],
            temperature = 0.3, #Lower = more focused, less creative
            max_tokens = 500, #limit response length
            response_format = {"type": "json_object"} #Force JSON response
        )

        ai_response = response.choices[0].message.content

    except Exception as e:
        print(f"DEBUG - Groq API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

    #Step 7: Parse the AI response
    try:
        context = json.loads(ai_response)
    except json.JSONDecodeError as e:
        
        #Fallback if AI returns invalid JSON
        context = {
            "summary": ai_response[:200],
            "next_action": "Review conversation and determine next step"
        }
    
    #Step 8: Add metadata
    context["contact_id"] = str(contact_id)
    context["contact_name"] = contact.name
    context["last_interaction"] = notes[0].created_at.strftime('%B %d, %Y')
    context["days_since_contact"] = (datetime.now(timezone.utc) - notes[0].created_at).days

    return context