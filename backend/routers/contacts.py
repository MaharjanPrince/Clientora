from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import auth, database, models, schemas

# from ..auth import get_current_user
from ..dependencies import get_current_user

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
