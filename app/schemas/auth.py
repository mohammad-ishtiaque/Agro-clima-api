"""
==============================================
📋 SCHEMAS/AUTH.PY - Request/Response Schemas
==============================================
Pydantic Schemas কি?
- এগুলো হলো "data validation" এর জন্য
- Frontend থেকে যে data আসবে সেটা ঠিক আছে কিনা check করে
- যেমন: email সত্যিই email কিনা, password খালি কিনা

Request Schema: Frontend থেকে data নেওয়ার format
Response Schema: Frontend এ data পাঠানোর format
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# =============================================
# 📝 SIGN UP Schemas
# =============================================

class UserSignUp(BaseModel):
    """
    Sign Up করার সময় Frontend থেকে এই data আসবে
    UI দেখো: Name, Email, Password, Confirm Password
    """
    full_name: str = Field(..., min_length=2, max_length=100, examples=["Rahim Uddin"])
    email: EmailStr = Field(..., examples=["rahim@email.com"])  # EmailStr automatically validates email format
    password: str = Field(..., min_length=6, examples=["mypassword123"])
    confirm_password: str = Field(..., min_length=6, examples=["mypassword123"])


# =============================================
# 🔑 LOGIN Schemas
# =============================================

class UserLogin(BaseModel):
    """
    Login করার সময় Frontend থেকে এই data আসবে
    UI দেখো: Email, Password
    """
    email: EmailStr
    password: str


class Token(BaseModel):
    """
    Login successful হলে এই response যাবে
    JWT Token দিয়ে user identify করা হয় (পরে বুঝাচ্ছি)
    """
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"  # User এর info ও পাঠাবো


# =============================================
# ✅ OTP VERIFICATION Schemas
# =============================================

class OTPVerify(BaseModel):
    """
    OTP verify করার সময় Frontend থেকে এই data আসবে
    UI দেখো: 6 digit code boxes
    """
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6, examples=["537412"])


class ResendOTP(BaseModel):
    """
    OTP আবার পাঠানোর জন্য
    শুধু email লাগবে
    """
    email: EmailStr


# =============================================
# 🔄 FORGOT PASSWORD Schemas
# =============================================

class ForgotPassword(BaseModel):
    """
    Password ভুলে গেলে OTP পাঠানোর জন্য
    UI দেখো: "Enter Your Email" field
    """
    email: EmailStr


class ResetPassword(BaseModel):
    """
    নতুন Password সেট করার জন্য
    UI দেখো: "Create new password" + "Confirm Password"
    OTP verify করার পরই এটা কাজ করবে
    """
    email: EmailStr
    otp_code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)


# =============================================
# 👤 USER Response Schemas
# =============================================

class UserResponse(BaseModel):
    """
    User এর info Frontend এ পাঠানোর format
    ⚠️ Password কখনোই response এ পাঠাবো না!
    """
    id: int
    email: str
    full_name: Optional[str] = None
    is_verified: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # SQLAlchemy model থেকে automatically convert করতে


# =============================================
# 📢 General Response Schemas
# =============================================

class MessageResponse(BaseModel):
    """
    সাধারণ message response
    যেমন: "OTP sent successfully", "Password changed" etc.
    """
    message: str
    success: bool = True


# Forward reference resolve করার জন্য
Token.model_rebuild()