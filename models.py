from sqlalchemy import (
    Column,
    String,
    Numeric,
    Integer,
    Date,
    DateTime,
    Boolean,
    JSON,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base
import uuid
from datetime import datetime


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    password_hash = Column(String(255), nullable=False)
    stripe_customer_id = Column(String(255), unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Loan(Base):
    __tablename__ = "loans"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    principal = Column(Numeric(12, 2), nullable=False)
    annual_interest_rate = Column(Numeric(5, 4), nullable=False)
    term_months = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    schedule = relationship("AmortizationSchedule", back_populates="loan")


class AmortizationSchedule(Base):
    __tablename__ = "amortization_schedule"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey("loans.id", ondelete="CASCADE"))
    period = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    scheduled_payment = Column(Numeric(10, 2), nullable=False)
    principal_portion = Column(Numeric(10, 2), nullable=False)
    interest_portion = Column(Numeric(10, 2), nullable=False)
    remaining_balance = Column(Numeric(12, 2), nullable=False)
    status = Column(String(50), default="pending")
    loan = relationship("Loan", back_populates="schedule")


class Payment(Base):
    __tablename__ = "payments"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    loan_id = Column(UUID(as_uuid=True), ForeignKey("loans.id"))
    schedule_id = Column(UUID(as_uuid=True), ForeignKey("amortization_schedule.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    amount = Column(Numeric(10, 2), nullable=False)
    payment_type = Column(String(50), default="regular")
    stripe_payment_intent_id = Column(String(255), unique=True)
    stripe_status = Column(String(50))
    paid_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)


class CreditProfile(Base):
    __tablename__ = "credit_profile"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    on_time_payments = Column(Integer, default=0)
    late_payments = Column(Integer, default=0)
    missed_payments = Column(Integer, default=0)
    total_paid = Column(Numeric(12, 2), default=0)
    mock_credit_score = Column(Integer)
    last_updated = Column(DateTime, default=datetime.utcnow)


class WebhookLog(Base):
    __tablename__ = "webhooks_log"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    stripe_event_id = Column(String(255), unique=True)
    event_type = Column(String(100))
    payload = Column(JSON)
    processed = Column(Boolean, default=False)
    received_at = Column(DateTime, default=datetime.utcnow)
