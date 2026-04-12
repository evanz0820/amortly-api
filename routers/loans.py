from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Loan, AmortizationSchedule
from pydantic import BaseModel
from datetime import date, timedelta
from decimal import Decimal
import uuid

router = APIRouter()


class LoanCreate(BaseModel):
    user_id: str
    principal: float
    annual_interest_rate: float
    term_months: int
    start_date: date


def generate_schedule(loan: Loan) -> list[AmortizationSchedule]:
    r = Decimal(str(loan.annual_interest_rate)) / 12
    n = loan.term_months
    p = Decimal(str(loan.principal))
    monthly = p * r / (1 - (1 + r) ** -n)
    balance = p
    schedule: list[AmortizationSchedule] = []
    due_date = loan.start_date
    for i in range(1, n + 1):
        interest = balance * r
        principal = monthly - interest
        balance -= principal
        due_date = due_date + timedelta(days=30)
        schedule.append(
            AmortizationSchedule(
                id=uuid.uuid4(),
                loan_id=loan.id,
                period=i,
                due_date=due_date,
                scheduled_payment=round(monthly, 2),
                principal_portion=round(principal, 2),
                interest_portion=round(interest, 2),
                remaining_balance=max(round(balance, 2), Decimal("0")),
            )
        )
    return schedule


@router.post("/")
def create_loan(payload: LoanCreate, db: Session = Depends(get_db)):
    loan = Loan(**payload.dict(), id=uuid.uuid4())
    db.add(loan)
    db.flush()
    schedule = generate_schedule(loan)
    db.add_all(schedule)
    db.commit()
    db.refresh(loan)
    return loan


@router.get("/")
def get_loans(user_id: str, db: Session = Depends(get_db)):
    return db.query(Loan).filter(Loan.user_id == user_id).all()


@router.get("/{loan_id}/schedule")
def get_schedule(loan_id: str, db: Session = Depends(get_db)):
    return (
        db.query(AmortizationSchedule)
        .filter(AmortizationSchedule.loan_id == loan_id)
        .order_by(AmortizationSchedule.period)
        .all()
    )
