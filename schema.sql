-- Amortly database schema
-- Usage: createdb amortly && psql amortly < schema.sql

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    stripe_customer_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS loans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    principal NUMERIC(12, 2) NOT NULL,
    annual_interest_rate NUMERIC(5, 4) NOT NULL,
    term_months INT NOT NULL,
    start_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS amortization_schedule (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id UUID REFERENCES loans(id) ON DELETE CASCADE,
    period INT NOT NULL,
    due_date DATE NOT NULL,
    scheduled_payment NUMERIC(10, 2) NOT NULL,
    principal_portion NUMERIC(10, 2) NOT NULL,
    interest_portion NUMERIC(10, 2) NOT NULL,
    remaining_balance NUMERIC(12, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending'
);

CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id UUID REFERENCES loans(id),
    schedule_id UUID REFERENCES amortization_schedule(id),
    user_id UUID REFERENCES users(id),
    amount NUMERIC(10, 2) NOT NULL,
    payment_type VARCHAR(50) DEFAULT 'regular',
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    stripe_status VARCHAR(50),
    paid_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS credit_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) UNIQUE,
    on_time_payments INT DEFAULT 0,
    late_payments INT DEFAULT 0,
    missed_payments INT DEFAULT 0,
    total_paid NUMERIC(12, 2) DEFAULT 0,
    mock_credit_score INT,
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS webhooks_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    stripe_event_id VARCHAR(255) UNIQUE,
    event_type VARCHAR(100),
    payload JSONB,
    processed BOOLEAN DEFAULT FALSE,
    received_at TIMESTAMP DEFAULT NOW()
);
