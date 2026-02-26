from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from .. import auth, database, models, schemas
# backend/routers/deals.py
from .. import models, schemas, database
# from ..auth import get_current_user
from ..dependencies import get_current_user

router = APIRouter(prefix="/deals", tags=["deals"])


# POST /deals - Create a new deal
@router.post(
    "/", response_model=schemas.DealResponse, status_code=status.HTTP_201_CREATED
)
def create_deal(
    deal_in: schemas.DealCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    # SECURITY: Check that the contact exists AND belongs to this user
    contact = (
        db.query(models.Contact)
        .filter(
            models.Contact.id == deal_in.contact_id,
            models.Contact.user_id == current_user.id,
        )
        .first()
    )

    if not contact:
        raise HTTPException(
            status_code=404, detail="Contact not found or access denied"
        )

    new_deal = models.Deal(**deal_in.model_dump(), user_id=current_user.id)
    db.add(new_deal)
    db.commit()
    db.refresh(new_deal)
    return new_deal

#Update Deals
@router.put("/{deal_id}", response_model=schemas.DealResponse)
def update_deal(
    deal_id: UUID,
    deal_update: schemas.DealUpdate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    deal = db.query(models.Deal).filter(
        models.Deal.id == deal_id,
        models.Deal.user_id == current_user.id
    ).first()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    # Update only fields that were provided
    update_data = deal_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(deal, field, value)
    
    db.commit()
    db.refresh(deal)
    return deal
# GET /deals - List all deals for the user
@router.get("/", response_model=List[schemas.DealResponse])
def get_deals(
    stage: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user),
):
    query = db.query(models.Deal).filter(models.Deal.user_id == current_user.id)

    if stage:
        query = query.filter(models.Deal.stage == stage)

    return query.order_by(models.Deal.created_at.desc()).all()

#Delete Deals
@router.delete("/{deal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_deal(
    deal_id: UUID,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    deal = db.query(models.Deal).filter(
        models.Deal.id == deal_id,
        models.Deal.user_id == current_user.id
    ).first()
    
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    db.delete(deal)
    db.commit()
    return None

#Pipe lines
@router.get("/pipeline", response_model=schemas.PipelineResponse)
def get_pipeline(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Fetch all deals for the user
    deals = db.query(models.Deal).filter(models.Deal.user_id == current_user.id).all()

    #2. Define the stages to ensuer the report is consistent
    stages = ["lead", "proposal", "negotiation", "won", "lost"]

    #3. Initialize the dictionary with zeros
    by_stage = {
        stage: {"count": 0, "total_value": Decimal(0), "deals": []}
        for stage in stages
    }

    #4. Sort deals into their buckets
    total_pipeline_value = Decimal(0)

    for deal in deals:
        stage = deal.stage
        if stage in by_stage:
            by_stage[stage]["count"] += 1
            by_stage[stage]["total_value"] += deal.amount
            by_stage[stage]["deals"].append(deal)

            #Add to total ONLY if not lost
            if stage != "lost":
                total_pipeline_value += deal.amount
    
    return {
        "total_value": total_pipeline_value,
        "deals_by_stage": by_stage
    }