from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, loans, payments, credit_profile, webhooks

app = FastAPI(title="Amortly API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(loans.router, prefix="/loans", tags=["loans"])
app.include_router(payments.router, prefix="/payments", tags=["payments"])
app.include_router(credit_profile.router, prefix="/credit-profile", tags=["credit"])
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
