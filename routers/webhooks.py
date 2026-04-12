from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Payment, AmortizationSchedule, CreditProfile, WebhookLog
import stripe
import os
import uuid
from datetime import datetime

router = APIRouter()
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")


def compute_credit_score(profile: CreditProfile) -> int:
    total = (
        profile.on_time_payments + profile.late_payments + profile.missed_payments
    )
    if total == 0:
        return 650
    on_time_ratio = profile.on_time_payments / total
    base = 580
    score = base + int(on_time_ratio * 220) - (profile.missed_payments * 15)
    return max(300, min(850, score))


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(payload, sig, WEBHOOK_SECRET)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid signature")

    log = WebhookLog(
        id=uuid.uuid4(),
        stripe_event_id=event["id"],
        event_type=event["type"],
        payload=dict(event),
    )
    db.add(log)

    if event["type"] == "payment_intent.succeeded":
        intent = event["data"]["object"]
        meta = intent["metadata"]

        payment = Payment(
            id=uuid.uuid4(),
            loan_id=meta["loan_id"],
            schedule_id=meta["schedule_id"],
            user_id=meta["user_id"],
            amount=intent["amount"] / 100,
            payment_type=meta.get("payment_type", "regular"),
            stripe_payment_intent_id=intent["id"],
            stripe_status="succeeded",
            paid_at=datetime.utcnow(),
        )
        db.add(payment)

        schedule = (
            db.query(AmortizationSchedule)
            .filter(AmortizationSchedule.id == meta["schedule_id"])
            .first()
        )
        if schedule:
            schedule.status = "paid"

        profile = (
            db.query(CreditProfile)
            .filter(CreditProfile.user_id == meta["user_id"])
            .first()
        )
        if profile:
            profile.on_time_payments += 1
            profile.total_paid += payment.amount
            profile.mock_credit_score = compute_credit_score(profile)
            profile.last_updated = datetime.utcnow()

    log.processed = True
    db.commit()
    return {"status": "ok"}
