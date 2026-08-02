from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ScanResponse(BaseModel):
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    formatting_flags: list[str]


class ScanHistoryItem(BaseModel):
    id: int
    resume_filename: str
    score: float
    matched_skills: list[str]
    missing_skills: list[str]
    created_at: datetime

    class Config:
        from_attributes = True
