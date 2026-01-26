from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.routing import APIRoute
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import auth, database, models, schemas
from .. dependencies import get_current_users

router = APIRouter(prefix="/contact", tags=["Contacts"])

@router.post("/contacts", response_model = schemas.ContactResponse)
def register(contact: schemas.ContactCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(auth.get_current_user):
    new_contact = models.Contact(**contact.model_dump(), owner_id=current_user.id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

@router.get("/", response_model = List[schemas.ContactResponse])
def get_contacts(db:Session = Depends(get_db), current_user: models.User = Depends(auth.get_current_user)):
    return db.query(models.Contact).filter(models.Contact.owner_id == current_user.id).all()

@router.get("/contact_id", response_model=schemas.ContactResponse)
def get_contact(
    contact_id: UUID,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current-user)
):
    contact = db.query(models.Contact).filter(
        models.Contact.id == contact_id,
        models.Contact.owner_id == current_user.id
    ).first()

    if not contact:
        raise HTTPException(status_code = 404, detail = "Contact not found")

    db.delete(contact)
    db.commit()
    reutrn None
