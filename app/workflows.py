"""
workflows.py
------------
3 automations. Uses Ollama first, falls back to Groq.
Same _call() pattern as agents.py.
"""

import os, json, re
from app.agents import _call   # reuse the same Ollama->Groq fallback


def _parse(text: str) -> dict:
    clean = re.sub(r"```(?:json)?|```", "", text).strip()
    try:    return json.loads(clean)
    except: return {"result": text}


def summarize_email(email_body: str) -> dict:
    """
    WHY: SMEs get lots of emails. This extracts the key info instantly.
    RETURNS: {subject, summary, action_items, priority}
    """
    system = """Summarize business emails. Output ONLY valid JSON:
{
  "subject": "guessed subject line",
  "summary": "2-sentence summary",
  "action_items": ["item1", "item2"],
  "priority": "high" or "medium" or "low"
}"""
    raw = _call(system, f"Email:\n{email_body}")
    return _parse(raw)


def generate_followup(name: str, company, status: str, notes) -> dict:
    """
    WHY: Writes a personalised follow-up email for a captured lead automatically.
    RETURNS: {subject, body, suggested_send_time}
    """
    system = """Write a short professional follow-up email for a sales lead.
Output ONLY valid JSON:
{
  "subject": "email subject line",
  "body": "email body (3-4 sentences)",
  "suggested_send_time": "e.g. within 24 hours"
}"""
    user = (
        f"Lead name: {name}\n"
        f"Company: {company or 'unknown'}\n"
        f"Status: {status}\n"
        f"Notes: {notes or 'none'}"
    )
    raw = _call(system, user)
    return _parse(raw)


def score_lead(name: str, notes: str) -> dict:
    """
    WHY: AI re-evaluates the lead and classifies as hot/warm/cold.
    RETURNS: {status, reason, score}
    """
    system = """Classify a sales lead. Output ONLY valid JSON:
{
  "status": "hot" or "warm" or "cold",
  "reason": "one sentence explanation",
  "score": integer 1-10
}
hot = ready to buy now, warm = interested but uncertain, cold = just browsing."""
    raw = _call(system, f"Lead: {name}\nWhat they said: {notes}")
    return _parse(raw)