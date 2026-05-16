"""
main.py
-------
WHY: This is the central file FastAPI reads to start the server.
     Every URL route (endpoint) is defined here.
     It wires together database, RAG, and agents into a working API.

RUN WITH: uvicorn app.main:app --reload --port 8000
"""

import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from dotenv import load_dotenv
load_dotenv()   # reads your .env file

from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import (
    init_db, get_db, Lead, LeadStatus, ChatMessage, WorkflowLog
)
from app.rag import ingest_document, retrieve_context, list_documents, delete_document
from app.agents import run_pipeline
from app.workflows import summarize_email, generate_followup, score_lead

# ── JWT config (reads from .env) ───────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-change-this")
ALGORITHM  = "HS256"
pwd_ctx    = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2     = OAuth2PasswordBearer(tokenUrl="/auth/token")

# ── Hardcoded admin user for simplicity ────────────────────────────────────
# WHY: A full user table would add complexity. For this MVP we use one
#      admin account defined in .env — enough for the assignment.
ADMIN_EMAIL    = os.getenv("ADMIN_EMAIL", "admin@demo.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")


# ── Startup ────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()   # creates smart_assistant.db and all tables
    yield


app = FastAPI(title="Smart Business Assistant", version="1.0.0", lifespan=lifespan)

# Allow the dashboard HTML (served as a static file) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve dashboard/index.html at http://localhost:8000/dashboard/
app.mount("/dashboard", StaticFiles(directory="app/dashboard", html=True), name="dashboard")


# ── Auth helpers ───────────────────────────────────────────────────────────

def create_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(hours=8)
    return jwt.encode({"sub": email, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2)) -> str:
    """
    WHY: Any route that uses Depends(get_current_user) requires a valid
         JWT token. This protects all non-public routes.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email   = payload.get("sub")
        if not email:
            raise HTTPException(401, "Invalid token")
        return email
    except JWTError:
        raise HTTPException(401, "Invalid token")


# ── Auth routes ────────────────────────────────────────────────────────────

@app.post("/auth/token")
def login(form: OAuth2PasswordRequestForm = Depends()):
    """
    WHY: The dashboard calls this to get a JWT token.
         Send username + password, get back a token to use in other calls.
    """
    if form.username != ADMIN_EMAIL or form.password != ADMIN_PASSWORD:
        raise HTTPException(401, "Wrong email or password")
    return {"access_token": create_token(form.username), "token_type": "bearer"}


# ── Chat route ─────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message:    str
    session_id: str  = ""
    history:    list = []


@app.post("/chat")
def chat(body: ChatRequest, user: str = Depends(get_current_user)):
    """
    WHY: This is the main endpoint. The dashboard sends messages here.
         It runs the full Planner → Executor → Validator pipeline
         and returns the AI's answer.
    """
    session_id = body.session_id or str(uuid.uuid4())
    result     = run_pipeline(body.message, session_id, body.history)
    return result


# ── Document / RAG routes ──────────────────────────────────────────────────

@app.post("/documents/upload")
def upload_doc(
    file: UploadFile = File(...),
    user: str = Depends(get_current_user),
):
    """
    WHY: Lets the admin upload business documents (.txt, .pdf).
         These get chunked and stored in ChromaDB for RAG retrieval.
    """
    content = file.file.read()
    result  = ingest_document(content, file.filename)
    return result


@app.get("/documents")
def get_docs(user: str = Depends(get_current_user)):
    return list_documents()


@app.delete("/documents/{doc_id}")
def remove_doc(doc_id: str, user: str = Depends(get_current_user)):
    deleted = delete_document(doc_id)
    return {"deleted_chunks": deleted}


# ── Lead routes ────────────────────────────────────────────────────────────

@app.get("/leads")
def get_leads(
    status: str | None = Query(None),
    db:     Session    = Depends(get_db),
    user:   str        = Depends(get_current_user),
):
    """Returns all captured leads. Optional ?status=hot filter."""
    q = db.query(Lead).order_by(Lead.created_at.desc())
    if status:
        q = q.filter(Lead.status == LeadStatus(status))
    leads = q.limit(100).all()
    return [
        {
            "id": l.id, "name": l.name, "email": l.email,
            "phone": l.phone, "company": l.company,
            "status": l.status, "notes": l.notes,
            "created_at": str(l.created_at),
        }
        for l in leads
    ]


# ── Workflow routes ────────────────────────────────────────────────────────

class EmailBody(BaseModel):
    email_body: str


@app.post("/workflows/summarize-email")
def wf_summarize(body: EmailBody, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    result = summarize_email(body.email_body)
    db.add(WorkflowLog(
        workflow_name="email_summarization",
        status="success" if "error" not in result else "failed",
        result=str(result),
    ))
    db.commit()
    return result


@app.post("/workflows/followup/{lead_id}")
def wf_followup(lead_id: str, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(404, "Lead not found")
    result = generate_followup(lead.name, lead.company, lead.status, lead.notes)
    db.add(WorkflowLog(workflow_name="lead_followup", status="success", result=str(result)))
    db.commit()
    return result


@app.post("/workflows/score/{lead_id}")
def wf_score(lead_id: str, user: str = Depends(get_current_user), db: Session = Depends(get_db)):
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(404, "Lead not found")
    result = score_lead(lead.name, lead.notes or "")
    # Update the lead's status in DB
    new_status = result.get("status", "cold")
    if new_status in ("hot", "warm", "cold"):
        lead.status = LeadStatus(new_status)
        db.commit()
    db.add(WorkflowLog(workflow_name="lead_scoring", status="success", result=str(result)))
    db.commit()
    return result


# ── Admin / analytics routes ───────────────────────────────────────────────

@app.get("/admin/analytics")
def analytics(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    """
    WHY: The dashboard calls this to show the stats cards and charts.
         Returns counts for leads, messages, and workflows.
    """
    total_leads = db.query(func.count(Lead.id)).scalar() or 0
    hot   = db.query(func.count(Lead.id)).filter(Lead.status == LeadStatus.hot).scalar()  or 0
    warm  = db.query(func.count(Lead.id)).filter(Lead.status == LeadStatus.warm).scalar() or 0
    cold  = db.query(func.count(Lead.id)).filter(Lead.status == LeadStatus.cold).scalar() or 0
    msgs  = db.query(func.count(ChatMessage.id)).scalar() or 0
    wf_ok = db.query(func.count(WorkflowLog.id)).filter(WorkflowLog.status == "success").scalar() or 0
    wf_all= db.query(func.count(WorkflowLog.id)).scalar() or 0

    return {
        "leads":     {"total": total_leads, "hot": hot, "warm": warm, "cold": cold},
        "messages":  msgs,
        "workflows": {"total": wf_all, "success": wf_ok, "failed": wf_all - wf_ok},
    }


@app.get("/admin/logs")
def conv_logs(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    logs = db.query(ChatMessage).order_by(ChatMessage.created_at.desc()).limit(100).all()
    return [
        {
            "role": l.role, "content": l.content[:200],
            "intent": l.intent, "session_id": l.session_id,
            "created_at": str(l.created_at),
        }
        for l in logs
    ]


@app.get("/admin/workflow-logs")
def wf_logs(db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    logs = db.query(WorkflowLog).order_by(WorkflowLog.created_at.desc()).limit(100).all()
    return [
        {
            "id": l.id, "workflow": l.workflow_name,
            "status": l.status, "result": l.result,
            "created_at": str(l.created_at),
        }
        for l in logs
    ]


@app.get("/health")
def health():
    return {"status": "ok"}