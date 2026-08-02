"""
Database configuration.

By default uses SQLite (zero setup, great for local dev/testing).
To use MySQL instead, set the DATABASE_URL environment variable, e.g.:

    export DATABASE_URL="mysql+pymysql://username:password@localhost:3306/ats_scanner"

Then just run the app as normal — no code changes needed.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ats_scanner.db")

# SQLite needs this special connect_arg; MySQL doesn't.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a DB session and closes it after the request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
