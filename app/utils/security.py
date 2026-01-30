"""
==============================================
🔐 UTILS/SECURITY.PY - Security Utilities
==============================================
এখানে ৩টা গুরুত্বপূর্ণ জিনিস আছে:

1. PASSWORD HASHING (পাসওয়ার্ড এনক্রিপ্ট করা)
   - Plain password ডাটাবেসে রাখা বিপদজনক
   - আমরা "hash" করে রাখি (একমুখী এনক্রিপশন)
   - "password123" → "$2b$12$LQv3c1yqBW..."

2. JWT TOKEN (JSON Web Token)
   - Login এর পর user কে একটা "token" দিই
   - এই token দিয়ে user নিজেকে identify করে
   - Token এর ভেতর user id encoded থাকে

3. OTP GENERATION (One Time Password)
   - 6 digit random number
   - Email এ পাঠাই verify করার জন্য
"""

import os
import random
import string
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()


# =============================================
# ⚙️ CONFIG VALUES
# =============================================

# 🔑 Secret Key - JWT sign করতে লাগে (এটা .env এ রাখো, গোপন রাখতে হবে!)
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-this-in-production")

# 📜 Algorithm - JWT এ কোন algorithm ব্যবহার করবে
ALGORITHM = "HS256"

# ⏰ Token কতক্ষণ valid থাকবে (minutes এ)
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

# ⏰ OTP কতক্ষণ valid থাকবে (minutes এ)
OTP_EXPIRE_MINUTES = 10  # 10 minutes


# =============================================
# 🔒 PASSWORD HASHING
# =============================================

# bcrypt ব্যবহার করছি - সবচেয়ে secure hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    Plain password কে hash করে
    
    কেন hash করি?
    - Database hack হলেও password safe থাকে
    - Hash থেকে original password বের করা practically impossible
    
    Example:
    "password123" → "$2b$12$LQv3c1yqBWEHxZtVE5Fz..."
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    User এর দেওয়া password সঠিক কিনা check করে
    
    কিভাবে কাজ করে?
    - User এর দেওয়া password hash করে
    - Database এর hash এর সাথে মিলিয়ে দেখে
    
    Returns: True if match, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# =============================================
# 🎫 JWT TOKEN
# =============================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    JWT Access Token বানায়
    
    JWT কি?
    - একটা encoded string যেটা user info ধারণ করে
    - 3 parts: Header.Payload.Signature
    - Payload এ আমরা user_id রাখি
    
    Example token:
    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIi...
    
    এই token:
    - Frontend localStorage এ রাখে
    - প্রতিটা API request এ header এ পাঠায়
    - Backend verify করে বুঝে কোন user
    """
    to_encode = data.copy()
    
    # Expiration time সেট করছি
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    # JWT encode করে return
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    JWT Token valid কিনা check করে
    
    কি check করে?
    - Token টা tampered হয়নি (signature valid)
    - Token expire হয়নি
    
    Returns: Token এর payload (data) অথবা None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def get_user_id_from_token(token: str) -> Optional[int]:
    """
    Token থেকে user_id বের করে
    """
    payload = verify_token(token)
    if payload:
        return payload.get("sub")  # "sub" এ user_id রাখি
    return None


# =============================================
# 🔢 OTP GENERATION
# =============================================

def generate_otp() -> str:
    """
    6 digit OTP generate করে
    
    Example: "537412", "829103", "456789"
    
    random.choices ব্যবহার করে 0-9 থেকে 6টা digit নিচ্ছি
    """
    return ''.join(random.choices(string.digits, k=6))


def get_otp_expiry() -> datetime:
    """
    OTP এর expiry time return করে
    
    এখন থেকে 10 minutes পর expire হবে
    """
    return datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRE_MINUTES)


def is_otp_valid(otp_expires_at: datetime) -> bool:
    """
    OTP expire হয়েছে কিনা check করে
    
    Returns: True if still valid, False if expired
    """
    if otp_expires_at is None:
        return False
    
    # timezone aware comparison
    now = datetime.now(timezone.utc)
    if otp_expires_at.tzinfo is None:
        otp_expires_at = otp_expires_at.replace(tzinfo=timezone.utc)
    
    return now < otp_expires_at