# Amortly — API

A FastAPI backend for the Amortly loan management platform. Handles loan creation, amortization schedule generation, Stripe payment processing, webhook handling, and mock credit scoring.

## Tech Stack

- **FastAPI** — web framework
- **SQLAlchemy** — ORM
- **PostgreSQL** — database
- **Stripe** — payment processing and webhooks
- **Pydantic** — request/response validation
- **Uvicorn** — ASGI server

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL running locally
- Stripe account with test keys

### 1. Set Up the Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn sqlalchemy psycopg2-binary stripe python-dotenv pydantic
```

### 2. Configure Environment Variables

Copy `.env` and fill in your values:

```
DATABASE_URL=postgresql://postgres:password@localhost/amortly
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

### 3. Create the Database

Run the SQL in `schema.sql` (or manually in `psql`):

```bash
psql -U postgres -f schema.sql
```

This creates the `amortly` database and all tables: `users`, `loans`, `amortization_schedule`, `payments`, `credit_profile`, `webhooks_log`.

### 4. Seed a Test User

```bash
psql -U postgres -d amortly -f seed.sql
```

Or manually:

```sql
INSERT INTO users (id, email, name)
VALUES ('323ba38f-ae2c-4a01-9cf7-5642c87686be', 'test@amortly.com', 'Test User');

INSERT INTO credit_profile (user_id, mock_credit_score)
VALUES ('323ba38f-ae2c-4a01-9cf7-5642c87686be', 650);
```

### 5. Run the Server

```bash
uvicorn main:app --reload --port 8000
```

API docs available at [http://localhost:8000/docs](http://localhost:8000/docs).

### 6. Forward Stripe Webhooks (for local development)

```bash
stripe listen --forward-to localhost:8000/webhooks/stripe
```

Copy the webhook signing secret (`whsec_...`) into your `.env`.

## Project Structure

```
amortly-api/
├── main.py             # FastAPI app, CORS config, router registration
├── database.py         # SQLAlchemy engine, session, Base
├── models.py           # ORM models (User, Loan, Schedule, Payment, CreditProfile, WebhookLog)
├── schema.sql          # Database DDL
├── seed.sql            # Test data
├── .env                # Environment variables (not committed)
└── routers/
    ├── __init__.py
    ├── loans.py        # POST /loans, GET /loans, GET /loans/:id/schedule
    ├── payments.py     # POST /payments/intent, GET /payments
    ├── credit_profile.py  # GET /credit-profile/:user_id
    └── webhooks.py     # POST /webhooks/stripe (handles payment_intent.succeeded)
```

## API Endpoints

### Loans

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/loans` | Create a new loan and generate its amortization schedule |
| `GET` | `/loans?user_id=` | List all loans for a user |
| `GET` | `/loans/:id/schedule` | Get the amortization schedule for a loan |

### Payments

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/payments/intent` | Create a Stripe PaymentIntent |
| `GET` | `/payments?user_id=` | List all payments for a user |

### Credit Profile

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/credit-profile/:user_id` | Get the mock credit profile for a user |

### Webhooks

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/webhooks/stripe` | Stripe webhook handler — records payments, updates schedule status, recalculates credit score |

## How It Works

### Amortization Schedule

When a loan is created, the API generates a full amortization schedule using the standard formula:

```
monthly_payment = P * r / (1 - (1 + r)^-n)
```

Each period calculates the interest portion, principal portion, and remaining balance.

### Credit Score

The mock credit score (300–850) is calculated on each successful payment:

```
score = 580 + (on_time_ratio * 220) - (missed_payments * 15)
```

### Payment Flow

1. Frontend calls `POST /payments/intent` with loan/schedule details
2. API creates a Stripe PaymentIntent and returns the `client_secret`
3. Frontend uses Stripe.js to confirm the payment
4. Stripe sends a `payment_intent.succeeded` webhook
5. API records the payment, marks the schedule period as paid, and updates the credit score

## Deployment (Railway)

1. Push to GitHub
2. Create a project on [railway.app](https://railway.app)
3. Add a **PostgreSQL** service (Railway auto-provides `DATABASE_URL`)
4. Add a **service** from your repo
5. Set environment variables: `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
6. Set start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
7. Create a Stripe webhook endpoint pointing to `https://your-app.up.railway.app/webhooks/stripe`
8. Run `schema.sql` and `seed.sql` against the Railway Postgres instance

Add a `requirements.txt` for Railway:

```
fastapi
uvicorn
sqlalchemy
psycopg2-binary
stripe
python-dotenv
pydantic
```
