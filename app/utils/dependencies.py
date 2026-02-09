"""
==============================================
🔗 UTILS/DEPENDENCIES.PY - FastAPI Dependencies
==============================================
FastAPI এর Dependency Injection system ব্যবহার করে 
আমরা common tasks গুলো reuse করতে পারি।

এখানে সবচেয়ে গুরুত্বপূর্ণ dependency হলো:
get_current_user() - যেকোনো protected route এ ব্যবহার করবে
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.utils.security import verify_token


# =============================================
# 🎫 OAuth2 SCHEME
# =============================================

# এটা FastAPI কে বলে: "Authorization header থেকে token নাও"
# tokenUrl: Login endpoint এর URL (Swagger docs এ কাজে লাগে)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login/form")


# =============================================
# 👤 GET CURRENT USER
# =============================================

async def get_current_user(
    token: str = Depends(oauth2_scheme),  # Header থেকে token নিচ্ছে
    db: Session = Depends(get_db)  # Database session নিচ্ছে
) -> User:
    """
    বর্তমানে logged in user কে return করে
    
    কিভাবে কাজ করে?
    1. Request এর Authorization header থেকে token নেয়
    2. Token verify করে user_id বের করে
    3. Database থেকে সেই user কে খুঁজে return করে
    
    ব্যবহার:
    @app.get("/me")
    def get_me(current_user: User = Depends(get_current_user)):
        return current_user
    """
    
    # Credentials exception - token invalid হলে এটা throw করবো
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Token verify করছি
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    # Token থেকে user_id বের করছি
    user_id: int = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Database থেকে user খুঁজছি
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_verified_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Verified user কে return করে
    
    Email verify না করলে access দিবে না!
    কিছু route এ শুধু verified users এর access দিতে চাইলে এটা ব্যবহার করো
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Please verify your email first"
        )
    return current_user