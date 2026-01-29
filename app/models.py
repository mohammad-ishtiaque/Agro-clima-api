from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(255))
    full_name = Column(String(100), nullable=True)
    
    # Relationship: One user can have many assessments
    assessments = relationship("Assessment", back_populates="owner")

class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(Integer, primary_key=True, index=True)
    
    # Inputs (What the user gave us)
    latitude = Column(Float)
    longitude = Column(Float)
    observation_date = Column(Date)
    
    # Outputs (What we calculated)
    # We will save the logic result here (Dry, Normal, or Wet)
    final_result = Column(String(20)) 
    score = Column(Integer) # The weighted score (e.g., 16)
    
    # Additional Info (For the report)
    station_name = Column(String(100))
    soil_map_unit = Column(String(255))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Link to User
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="assessments")