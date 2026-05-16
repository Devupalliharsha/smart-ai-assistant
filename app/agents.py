"""
agents.py
---------
Uses Ollama (local, free, offline) as the primary LLM.
Falls back to Groq if Ollama is not reachable.

WHY OLLAMA: It runs on your machine — no API key, no cost, no internet needed.
WHY GROQ FALLBACK: If Ollama is slow or down, Groq keeps things working.

OLLAMA SETUP (run once in a separate terminal):
  ollama pull llama3.2        <- downloads the model (~2GB, one time only)
  ollama serve                <- starts the local server (may already be running)

HOW TO USE: from app.agents import run_pipeline
"""

import os
import json
import re
import uuid

from app.rag import retrieve_context
from app.database import SessionLocal, Lead, LeadStatus, ChatMessage

# ── Model config ───────────────────────────────────────────────────────────
OLLAMA_URL   = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2"     # small, fast, fits on most laptops
GROQ_MODEL   = "llama3-8b-8192"


# ── LLM call — tries Ollama first, then Groq ──────────────────────────────

def _call(system: str, user: str, max_tokens: int = 512) -> str:
    """
    WHY: We try Ollama first because it's free and local.
         If it fails (not running, model not downloaded), we try Groq.
    """
    # --- Try Ollama ---
    try:
        import urllib.request
        payload = json.dumps({
            "model": OLLAMA_MODEL,
            "messages": [
                {"role": "system",  "content": system},
                {"role": "user",    "content": user},
            ],
            "stream": False,
            "options": {"num_predict": max_tokens, "temperature": 0.2},
        }).encode()

        req = urllib.request.Request(
            OLLAMA_URL,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        # 10 second timeout — if Ollama is slow, don't hang forever
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return data["message"]["content"]

    except Exception as ollama_err:
        print(f"[Ollama unavailable: {ollama_err}] — falling back to Groq")

    # --- Fallback: Groq ---
    groq_key = os.getenv("GROQ_API_KEY", "")
    if not groq_key:
        raise RuntimeError(
            "Ollama is not reachable AND no GROQ_API_KEY set in .env.\n"
            "Fix: run 'ollama serve' in a terminal, OR add GROQ_API_KEY to .env"
        )
    from groq import Groq
    client = Groq(api_key=groq_key)
    resp   = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user",   "content": user},
        ],
        max_tokens=max_tokens,
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""


def _parse_json(text: str) -> dict:
    """Strip markdown fences and parse JSON safely."""
    clean = re.sub(r"```(?:json)?|```", "", text).strip()
    try:
        return json.loads(clean)
    except Exception:
        return {}


# ── AGENT 1: PLANNER ──────────────────────────────────────────────────────

PLANNER_PROMPT = """You are a Planner agent for a business assistant.
Read the user message and output ONLY valid JSON (no other text):
{
  "intent": "qa" or "lead_capture" or "general",
  "needs_rag": true or false,
  "lead": {
    "name": null or string,
    "email": null or string,
    "phone": null or string,
    "company": null or string,
    "status": "hot" or "warm" or "cold"
  }
}

intent rules:
- "qa"           = user is asking a business question
- "lead_capture" = user shares contact info or wants to buy/inquire
- "general"      = greeting, small talk, unclear

needs_rag = true if the answer might be in uploaded business documents.
For lead.status: hot = ready to buy, warm = interested, cold = just browsing."""


def planner(message: str, history: list) -> dict:
    """Reads the message, classifies intent, extracts lead info if present."""
    history_text = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in history[-4:])
    prompt = f"Recent conversation:\n{history_text}\n\nNew message: {message}"
    raw    = _call(PLANNER_PROMPT, prompt, max_tokens=300)
    plan   = _parse_json(raw)
    if "intent"    not in plan: plan["intent"]    = "general"
    if "needs_rag" not in plan: plan["needs_rag"] = False
    if "lead"      not in plan: plan["lead"]      = {}
    return plan


# ── AGENT 2: EXECUTOR ─────────────────────────────────────────────────────

EXECUTOR_PROMPT = """You are a helpful business assistant.
Answer the user's question clearly and professionally.

Rules:
- If document context is provided, base your answer on it.
- If no context is available for a factual question, say you don't have that info.
- For lead capture: warmly confirm you've noted their details and say someone will follow up.
- Keep answers short (3-5 sentences max).
- Never make up prices, dates, or statistics."""


def executor(message: str, plan: dict, history: list) -> str:
    """Fetches RAG context, saves lead if found, generates the answer."""
    context = ""
    if plan.get("needs_rag"):
        context = retrieve_context(message)

    lead_data = plan.get("lead", {})
    if plan.get("intent") == "lead_capture" and (lead_data.get("name") or lead_data.get("email")):
        _save_lead(lead_data, message)

    context_block = f"\n\nRelevant documents:\n{context}" if context else ""
    history_text  = "\n".join(f"{m['role'].upper()}: {m['content']}" for m in history[-6:])
    user_prompt   = f"{context_block}\n\nConversation:\n{history_text}\n\nUser: {message}"
    return _call(EXECUTOR_PROMPT, user_prompt, max_tokens=400)


def _save_lead(lead_data: dict, notes: str):
    raw_status = (lead_data.get("status") or "cold").lower()
    if raw_status not in ("hot", "warm", "cold"):
        raw_status = "cold"
    db = SessionLocal()
    try:
        lead = Lead(
            name    = lead_data.get("name") or "Unknown",
            email   = lead_data.get("email"),
            phone   = lead_data.get("phone"),
            company = lead_data.get("company"),
            status  = LeadStatus(raw_status),
            notes   = notes[:500],
        )
        db.add(lead)
        db.commit()
    finally:
        db.close()


# ── AGENT 3: VALIDATOR ────────────────────────────────────────────────────

VALIDATOR_PROMPT = """You are a Validator agent. Check if the assistant's answer is good.
Output ONLY valid JSON:
{
  "approved": true or false,
  "confidence": 0.0 to 1.0,
  "final_answer": "the answer to use"
}

Reject (approved=false) if the answer makes up specific facts not in the context,
is rude, or is completely off-topic (like including irrelevant contact info). 
CRITICAL: If you reject the answer, your 'final_answer' MUST NOT contain your critique. Instead, rewrite the 'final_answer' to politely inform the user: "I apologize, but I cannot accurately answer that based on the provided documents."
"""


def validator(question: str, answer: str, context: str) -> dict:
    """Reviews the executor's answer and fixes it if needed."""
    prompt = (
        f"User asked: {question}\n\n"
        f"Context used: {context[:800] if context else 'None'}\n\n"
        f"Assistant answer: {answer}"
    )
    raw    = _call(VALIDATOR_PROMPT, prompt, max_tokens=400)
    result = _parse_json(raw)
    if not result.get("final_answer"):
        result["final_answer"] = answer
    if "confidence" not in result:
        result["confidence"] = 0.7
    return result


# ── MAIN PIPELINE ─────────────────────────────────────────────────────────

def run_pipeline(message: str, session_id: str, history: list) -> dict:
    """
    Runs Planner -> Executor -> Validator in sequence.
    Saves both user + assistant messages to the DB.
    Returns: {answer, intent, confidence, lead_saved, session_id}
    """
    plan      = planner(message, history)
    context   = retrieve_context(message) if plan.get("needs_rag") else ""
    answer    = executor(message, plan, history)
    validated = validator(message, answer, context)

    db = SessionLocal()
    try:
        db.add(ChatMessage(session_id=session_id, role="user", content=message))
        db.add(ChatMessage(
            session_id=session_id, role="assistant",
            content=validated["final_answer"], intent=plan["intent"]
        ))
        db.commit()
    finally:
        db.close()

    lead_data  = plan.get("lead", {})
    lead_saved = (
        plan.get("intent") == "lead_capture"
        and bool(lead_data.get("name") or lead_data.get("email"))
    )
    return {
        "answer":     validated["final_answer"],
        "intent":     plan["intent"],
        "confidence": validated.get("confidence", 0.7),
        "lead_saved": lead_saved,
        "session_id": session_id,
    }