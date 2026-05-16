"""
database.py
-----------
WHY: We need to store leads and chat history somewhere permanently.
     We use SQLite because it needs ZERO installation — it's just a file.
     SQLAlchemy lets us write Python instead of raw SQL.

HOW TO USE: from app.database import init_db, get_db, Lead, ChatMessage
"""

import uuid
import enum
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from sqlalchemy.sql import func

# --- This creates a file called smart_assistant.db in your project folder ---
# aiosqlite is NOT used here — we keep it sync (simpler, no async headaches)
DATABASE_URL = "sqlite:///./smart_assistant.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # needed for SQLite + FastAPI
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


# ── Enums ──────────────────────────────────────────────────────────────────
class LeadStatus(str, enum.Enum):
    hot  = "hot"
    warm = "warm"
    cold = "cold"


# ── Lead table ─────────────────────────────────────────────────────────────
# WHY: Every time the AI captures someone's contact info, it goes here.
class Lead(Base):
    __tablename__ = "leads"

    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name       = Column(String(200), nullable=False)
    email      = Column(String(200), nullable=True)
    phone      = Column(String(50),  nullable=True)
    company    = Column(String(200), nullable=True)
    status     = Column(SAEnum(LeadStatus), default=LeadStatus.cold, nullable=False)
    notes      = Column(Text, nullable=True)   # what they said in chat
    created_at = Column(DateTime, default=datetime.utcnow)


# ── Chat message table ─────────────────────────────────────────────────────
# WHY: We store every message so the dashboard can show conversation logs.
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id         = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, nullable=False, index=True)
    role       = Column(String(20), nullable=False)   # "user" or "assistant"
    content    = Column(Text, nullable=False)
    intent     = Column(String(50), nullable=True)    # what the AI decided this was
    created_at = Column(DateTime, default=datetime.utcnow)


# ── Workflow log table ─────────────────────────────────────────────────────
# WHY: Every time an automation runs, we record it here for the dashboard.
class WorkflowLog(Base):
    __tablename__ = "workflow_logs"

    id            = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_name = Column(String(100), nullable=False)
    status        = Column(String(20),  nullable=False)  # "success" or "failed"
    result        = Column(Text, nullable=True)
    error         = Column(Text, nullable=True)
    created_at    = Column(DateTime, default=datetime.utcnow)


# ── Create all tables ──────────────────────────────────────────────────────
def init_db():
    """Call once on startup. Creates the .db file and all tables."""
    Base.metadata.create_all(bind=engine)


# ── FastAPI dependency ─────────────────────────────────────────────────────
def get_db():
    """
    WHY: FastAPI needs a way to give each request its own DB connection.
         This function opens one, hands it to the route, then closes it.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()