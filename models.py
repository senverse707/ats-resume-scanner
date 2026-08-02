from datetime import datetime

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    scans = relationship("Scan", back_populates="owner", cascade="all, delete-orphan")


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    resume_filename = Column(String(255))
    job_description = Column(Text)
    score = Column(Float)
    matched_skills = Column(Text)   # stored as comma-separated for simplicity
    missing_skills = Column(Text)
    formatting_flags = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="scans")
