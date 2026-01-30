"""
==============================================
🔐 ROUTERS/AUTH.PY - Authentication Routes
==============================================
এখানে সব Auth related API endpoints আছে:

📝 POST /auth/signup        → নতুন account তৈরি
✅ POST /auth/verify-email  → OTP দিয়ে email verify
🔄 POST /auth/resend-otp    → OTP আবার পাঠানো
🔑 POST /auth/login         → Login করা
📧 POST /auth/forgot-password → Password reset OTP পাঠানো
🔒 POST /auth/reset-password  → নতুন password সেট করা
👤 GET  /auth/me            → Current user info

প্রতিটা endpoint এ detail comment আছে!
"""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas.auth import (
    UserSignUp, UserLogin, Token, OTPVerify, 
    ResendOTP, ForgotPassword, ResetPassword,
    UserResponse, MessageResponse
)
from app.utils.security import (
    hash_password, verify_password, create_access_token,
    generate_otp, get_otp_expiry, is_otp_valid,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.utils.email import send_otp_email
from app.utils.dependencies import get_current_user, get_current_verified_user


# Router তৈরি
router = APIRouter(
    prefix="/auth",  # সব route এর আগে /auth যুক্ত হবে
    tags=["Authentication"]  # Swagger docs এ group করার জন্য
)


# =============================================
# 📝 SIGN UP - নতুন Account তৈরি
# =============================================

@router.post("/signup", response_model=MessageResponse)
async def signup(user_data: UserSignUp, db: Session = Depends(get_db)):
    """
    📝 নতুন User তৈরি করে এবং OTP পাঠায়
    
    Flow:
    1. Email আগে থেকে আছে কিনা check
    2. Password match করছে কিনা check
    3. Password hash করে database এ save
    4. OTP generate করে email এ পাঠানো
    
    UI Flow: Sign UP screen → OTP screen
    """
    
    # 1️⃣ Email আগে থেকে আছে কিনা check
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 2️⃣ Password match check
    if user_data.password != user_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # 3️⃣ OTP generate
    otp_code = generate_otp()
    otp_expires = get_otp_expiry()
    
    # 4️⃣ নতুন User তৈরি
    new_user = User(
        email=user_data.email,
        hashed_password=hash_password(user_data.password),  # Password hash করে রাখছি
        full_name=user_data.full_name,
        is_verified=False,  # Email verify হয়নি এখনো
        otp_code=otp_code,
        otp_expires_at=otp_expires
    )
    
    # 5️⃣ Database এ save
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 6️⃣ OTP email পাঠানো
    await send_otp_email(user_data.email, otp_code, purpose="verify")
    
    return MessageResponse(
        message="Account created! Please check your email for OTP verification.",
        success=True
    )


# =============================================
# ✅ VERIFY EMAIL - OTP দিয়ে Email Verify
# =============================================

@router.post("/verify-email", response_model=Token)
async def verify_email(otp_data: OTPVerify, db: Session = Depends(get_db)):
    """
    ✅ OTP verify করে email confirm করে
    
    Flow:
    1. User খুঁজে বের করা
    2. OTP সঠিক কিনা check
    3. OTP expire হয়েছে কিনা check
    4. is_verified = True করা
    5. Login token দিয়ে দেওয়া (auto login)
    
    UI Flow: OTP screen → Home/Dashboard
    """
    
    # 1️⃣ User খুঁজছি
    user = db.query(User).filter(User.email == otp_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 2️⃣ Already verified check
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # 3️⃣ OTP match check
    if user.otp_code != otp_data.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code"
        )
    
    # 4️⃣ OTP expire check
    if not is_otp_valid(user.otp_expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one."
        )
    
    # 5️⃣ User verify করছি
    user.is_verified = True
    user.otp_code = None  # OTP clear করে দিচ্ছি
    user.otp_expires_at = None
    db.commit()
    
    # 6️⃣ Auto login - Token generate করে দিচ্ছি
    access_token = create_access_token(
        data={"sub": user.id},  # Token এ user id রাখছি
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


# =============================================
# 🔄 RESEND OTP - আবার OTP পাঠানো
# =============================================

@router.post("/resend-otp", response_model=MessageResponse)
async def resend_otp(data: ResendOTP, db: Session = Depends(get_db)):
    """
    🔄 নতুন OTP generate করে আবার email এ পাঠায়
    
    UI এ "Resend OTP" button click করলে এটা call হয়
    """
    
    # User খুঁজছি
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Already verified check
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # নতুন OTP generate
    otp_code = generate_otp()
    otp_expires = get_otp_expiry()
    
    # Update করছি
    user.otp_code = otp_code
    user.otp_expires_at = otp_expires
    db.commit()
    
    # Email পাঠাচ্ছি
    await send_otp_email(data.email, otp_code, purpose="verify")
    
    return MessageResponse(
        message="New OTP sent to your email!",
        success=True
    )


# =============================================
# 🔑 LOGIN - Sign In
# =============================================

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    🔑 Email & Password দিয়ে Login
    
    Flow:
    1. Email দিয়ে user খুঁজে বের করা
    2. Password verify করা
    3. Email verified কিনা check
    4. JWT token দিয়ে দেওয়া
    
    UI Flow: Sign In screen → Home/Dashboard
    """
    
    # 1️⃣ User খুঁজছি
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # 2️⃣ Password verify
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # 3️⃣ Email verified check (optional - আপনি চাইলে এটা বাদ দিতে পারেন)
    if not user.is_verified:
        # Unverified user এর জন্য নতুন OTP পাঠাচ্ছি
        otp_code = generate_otp()
        user.otp_code = otp_code
        user.otp_expires_at = get_otp_expiry()
        db.commit()
        await send_otp_email(user.email, otp_code, purpose="verify")
        
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first. A new OTP has been sent."
        )
    
    # 4️⃣ Token generate
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


# =============================================
# 🔑 LOGIN (OAuth2 Form - For Swagger UI)
# =============================================

@router.post("/login/form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    🔑 OAuth2 compatible login (Swagger UI এর জন্য)
    
    এটা ওই একই login, শুধু form-data format এ input নেয়
    """
    login_data = UserLogin(email=form_data.username, password=form_data.password)
    return await login(login_data, db)


# =============================================
# 📧 FORGOT PASSWORD - Password Reset Request
# =============================================

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(data: ForgotPassword, db: Session = Depends(get_db)):
    """
    📧 Password ভুলে গেলে OTP পাঠায়
    
    UI এ "Forgot Password?" click → Email input → "Send Confirmation"
    """
    
    # User খুঁজছি
    user = db.query(User).filter(User.email == data.email).first()
    
    # ⚠️ Security Best Practice:
    # User না পেলেও same message দিচ্ছি
    # এতে attacker বুঝতে পারবে না কোন email registered আছে
    if not user:
        return MessageResponse(
            message="If this email exists, you will receive an OTP shortly.",
            success=True
        )
    
    # OTP generate করে পাঠাচ্ছি
    otp_code = generate_otp()
    user.otp_code = otp_code
    user.otp_expires_at = get_otp_expiry()
    db.commit()
    
    await send_otp_email(data.email, otp_code, purpose="reset")
    
    return MessageResponse(
        message="If this email exists, you will receive an OTP shortly.",
        success=True
    )


# =============================================
# 🔒 RESET PASSWORD - নতুন Password সেট করা
# =============================================

@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(data: ResetPassword, db: Session = Depends(get_db)):
    """
    🔒 OTP verify করে নতুন password সেট করা
    
    UI Flow: 
    Forgot Password → OTP screen → Create New Password screen
    
    ⚠️ এটা একটা combined endpoint:
    - OTP verify করছে
    - নতুন password সেট করছে
    """
    
    # 1️⃣ User খুঁজছি
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 2️⃣ OTP match check
    if user.otp_code != data.otp_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP code"
        )
    
    # 3️⃣ OTP expire check
    if not is_otp_valid(user.otp_expires_at):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one."
        )
    
    # 4️⃣ Password match check
    if data.new_password != data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    # 5️⃣ Password update
    user.hashed_password = hash_password(data.new_password)
    user.otp_code = None  # OTP clear
    user.otp_expires_at = None
    db.commit()
    
    return MessageResponse(
        message="Password changed successfully! You can now login.",
        success=True
    )


# =============================================
# 👤 GET CURRENT USER - Logged in User Info
# =============================================

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    👤 বর্তমান logged in user এর info return করে
    
    এটা protected route:
    - Authorization header এ token থাকতে হবে
    - Token valid না হলে 401 error
    
    Frontend এটা ব্যবহার করে:
    - User logged in আছে কিনা check
    - Profile page এ user info দেখানো
    """
    return UserResponse.model_validate(current_user)


# =============================================
# 🔓 PROTECTED ROUTE EXAMPLE
# =============================================

@router.get("/protected-example")
async def protected_route(current_user: User = Depends(get_current_verified_user)):
    """
    🔓 Example protected route - শুধু verified users এর জন্য
    
    get_current_verified_user dependency ব্যবহার করলে:
    - Token valid হতে হবে
    - Email verified হতে হবে
    """
    return {
        "message": f"Hello {current_user.full_name or current_user.email}! This is a protected route.",
        "user_id": current_user.id
    }