"""
==============================================
📦 MODELS.PY - Database Tables/Models
==============================================
এখানে আমরা আমাদের ডাটাবেস টেবিল গুলো define করছি।
SQLAlchemy এগুলোকে automatically MySQL এ টেবিল বানিয়ে দিবে।
"""

from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    👤 User Model - ইউজারদের তথ্য রাখার জন্য
    
    Auth এর জন্য নতুন fields যোগ করেছি:
    - is_verified: ইমেইল verify করেছে কিনা
    - otp_code: 6 digit OTP code
    - otp_expires_at: OTP কখন expire হবে
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    
    # 🔐 Email Verification Fields
    is_verified = Column(Boolean, default=False)  # ইমেইল verify করেছে কিনা
    
    # 🔢 OTP Fields (One Time Password)
    otp_code = Column(String(6), nullable=True)  # 6 digit code (যেমন: 537412)
    otp_expires_at = Column(DateTime(timezone=True), nullable=True)  # কখন expire হবে
    
    # 📅 Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship: One user can have many assessments
    assessments = relationship("Assessment", back_populates="owner")


class Assessment(Base):
    """
    📊 Assessment Model - মূল্যায়ন/রিপোর্ট রাখার জন্য
    """
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Inputs (What the user gave us)
    latitude = Column(Float)
    longitude = Column(Float)
    observation_date = Column(Date)
    
    # Outputs (What we calculated)
    final_result = Column(String(20))  # Dry, Normal, or Wet
    score = Column(Integer)  # The weighted score
    
    # Additional Info
    station_name = Column(String(100))
    soil_map_unit = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Link to User
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="assessments")