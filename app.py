"""
ATS Resume Scanner - FastAPI Service (with auth + history)
-------------------------------------------------------------
Endpoints:
    POST /auth/signup      -> create account
    POST /auth/login       -> get JWT access token
    POST /scan               -> (auth required) scan a resume, saves to history
    GET  /history            -> (auth required) list past scans

Run with:
    uvicorn app:app --reload --port 8000
"""

import tempfile
import os

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import User, Scan
from schemas import UserCreate, UserLogin, Token, ScanResponse, ScanHistoryItem
from auth import hash_password, verify_password, create_access_token, decode_access_token
from scanner import extract_text_from_pdf, extract_skills, compute_score, check_formatting_flags

# Create tables on startup (fine for dev; use Alembic migrations for production).
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ATS Resume Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTPBearer just expects a raw token pasted in — matches our JSON-based
# /auth/login (as opposed to OAuth2PasswordBearer, which expects OAuth2's
# form-encoded username/password login flow that we don't implement).
bearer_scheme = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    token = credentials.credentials
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.email == payload["sub"]).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@app.get("/")
def health_check():
    return {"status": "ok", "service": "ATS Resume Scanner API"}


# ---------- Auth ----------

@app.post("/auth/signup", response_model=Token)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(email=user_in.email, hashed_password=hash_password(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.email})
    return Token(access_token=token)


@app.post("/auth/login", response_model=Token)
def login(user_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_access_token({"sub": user.email})
    return Token(access_token=token)


# ---------- Scanning ----------

@app.post("/scan", response_model=ScanResponse)
async def scan_resume(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes are supported right now.")
    if not job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty.")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            content = await resume.read()
            tmp.write(content)
            tmp_path = tmp.name

        resume_text = extract_text_from_pdf(tmp_path)
        if not resume_text.strip():
            raise HTTPException(status_code=422, detail="Couldn't extract text from this PDF. It may be a scanned image.")

        resume_skills = extract_skills(resume_text)
        jd_skills = extract_skills(job_description)
        result = compute_score(resume_skills, jd_skills)
        flags = check_formatting_flags(tmp_path)

        # Save to history
        scan_record = Scan(
            user_id=current_user.id,
            resume_filename=resume.filename,
            job_description=job_description,
            score=result["score"],
            matched_skills=",".join(result["matched"]),
            missing_skills=",".join(result["missing"]),
            formatting_flags="||".join(flags),
        )
        db.add(scan_record)
        db.commit()

        return ScanResponse(
            score=result["score"],
            matched_skills=result["matched"],
            missing_skills=result["missing"],
            formatting_flags=flags,
        )
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.get("/history", response_model=list[ScanHistoryItem])
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    scans = (
        db.query(Scan)
        .filter(Scan.user_id == current_user.id)
        .order_by(Scan.created_at.desc())
        .all()
    )
    return [
        ScanHistoryItem(
            id=s.id,
            resume_filename=s.resume_filename,
            score=s.score,
            matched_skills=s.matched_skills.split(",") if s.matched_skills else [],
            missing_skills=s.missing_skills.split(",") if s.missing_skills else [],
            created_at=s.created_at,
        )
        for s in scans
    ]
