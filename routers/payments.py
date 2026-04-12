from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Payment
from pydantic import BaseModel
import stripe
import os

router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


class PaymentIntentRequest(BaseModel):
    loan_id: str
    schedule_id: str
    user_id: str
    amount: float
    payment_type: str = "regular"


@router.post("/intent")
def create_intent(payload: PaymentIntentRequest, db: Session = Depends(get_db)):
    intent = stripe.PaymentIntent.create(
        amount=int(payload.amount * 100),
        currency="usd",
        metadata={
            "loan_id": payload.loan_id,
            "schedule_id": payload.schedule_id,
            "user_id": payload.user_id,
            "payment_type": payload.payment_type,
        },
    )
    return {"client_secret": intent.client_secret}


@router.get("/")
def get_payments(user_id: str, db: Session = Depends(get_db)):
    return db.query(Payment).filter(Payment.user_id == user_id).all()
