"""
==============================================
🚀 MAIN.PY - FastAPI Application Entry Point
==============================================
এখানে আমাদের FastAPI app তৈরি হয়।
সব routers এখানে include করতে হয়।
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database import get_db, engine, Base
from app.models import User, Assessment  # Models import করলে tables create হবে
from app.routers import auth  # Auth router import


# =============================================
# 📦 CREATE TABLES
# =============================================
# এটা automatically সব tables create করে দিবে
# যদি table আগে থেকে না থাকে

Base.metadata.create_all(bind=engine)


# =============================================
# 🚀 CREATE APP
# =============================================

app = FastAPI(
    title="AgroClima API",
    description="🌿 Agricultural Climate Assessment API",
    version="1.0.0"
)


# =============================================
# 🌐 CORS MIDDLEWARE
# =============================================
# CORS = Cross-Origin Resource Sharing
# এটা লাগে যখন Frontend (React/Flutter) আলাদা server এ থাকে

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production এ specific origins দাও
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================
# 📌 INCLUDE ROUTERS
# =============================================

# Auth Router যুক্ত করছি
# এতে /auth/signup, /auth/login etc. available হবে
app.include_router(auth.router)


# =============================================
# 🏠 ROOT ENDPOINT
# =============================================

@app.get("/")
def read_root():
    return {
        "message": "Welcome to AgroClima API! 🌿",
        "docs": "/docs",
        "endpoints": {
            "auth": {
                "signup": "POST /auth/signup",
                "verify_email": "POST /auth/verify-email",
                "resend_otp": "POST /auth/resend-otp",
                "login": "POST /auth/login",
                "forgot_password": "POST /auth/forgot-password",
                "reset_password": "POST /auth/reset-password",
                "me": "GET /auth/me"
            }
        }
    }


# =============================================
# 🏥 HEALTH CHECK ENDPOINT
# =============================================

@app.get("/health")
def health_check():
    """API সচল আছে কিনা check"""
    return {"status": "healthy", "message": "API is running! ✅"}


@app.get("/db-check")
def db_check():
    """Database connection check"""
    try:
        db = next(get_db())
        db.execute(text("SELECT 1"))
        return {"status": "success", "message": "Database Connection Successful! 🟢"}
    except Exception as e:
        return {"status": "error", "message": f"Connection Failed: {str(e)} 🔴"}