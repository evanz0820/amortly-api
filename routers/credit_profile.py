from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import CreditProfile
import uuid

router = APIRouter()


@router.get("/{user_id}")
def get_credit_profile(user_id: str, db: Session = Depends(get_db)):
    return (
        db.query(CreditProfile).filter(CreditProfile.user_id == uuid.UUID(user_id)).first()
    )
