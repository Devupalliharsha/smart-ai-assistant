# Smart AI Business Assistant

A production-oriented MVP that lets small businesses chat with an AI, capture leads, automate tasks, and monitor everything from an admin dashboard.

---

# Overview

Smart AI Business Assistant is an AI-powered business automation platform built for small businesses and startups.

It combines:
- Multi-agent AI reasoning
- RAG (Retrieval-Augmented Generation)
- Lead capture
- Workflow automation
- Analytics dashboard
- Secure authentication

All inside a single lightweight FastAPI application.

---

# Features

| Feature | Description |
|---|---|
| AI Chat | Users chat with an AI powered by a 3-agent pipeline |
| Multi-Agent System | Planner → Executor → Validator architecture |
| RAG (Document Q&A) | Upload business documents and let AI answer from them |
| Lead Capture | Automatically extracts and stores contact information |
| Workflow Automation | Email summarizer, follow-up generator, lead scoring |
| Dashboard | View analytics, leads, workflows, and conversations |
| JWT Authentication | Secure admin login |
| SQLite Database | Lightweight local database |
| ChromaDB | Local vector database for embeddings |
| FastAPI Docs | Interactive API testing UI |

---

# Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Language | Python 3.11 | Stable and highly compatible |
| Backend Framework | FastAPI | Fast, modern, automatic docs |
| AI Provider | Groq (Llama 3 8B) | Free and extremely fast |
| Vector Database | ChromaDB | Lightweight local vector store |
| Database | SQLite | No setup required |
| Frontend | HTML + JavaScript | Lightweight browser dashboard |
| Authentication | JWT | Secure route protection |

---

# Architecture

```text
User Message
     │
     ▼
[ PLANNER ]
Analyzes intent:
- QA
- Lead capture
- General chat
- RAG needed?
     │
     ▼
[ EXECUTOR ]
- Searches documents (if needed)
- Saves leads
- Calls Groq API
- Generates response
     │
     ▼
[ VALIDATOR ]
- Reviews response
- Detects hallucinations
- Improves reliability
- Returns confidence score
     │
     ▼
Final Response + Database Logging
```

---

# Project Structure

```text
smart-assistant/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── rag.py
│   ├── agents.py
│   ├── workflows.py
│   └── dashboard/
│       └── index.html
│
├── chroma_store/
├── smart_assistant.db
├── .env
├── .env.example
└── requirements.txt
```

---

# Setup Guide

# Step 1 — Install Python 3.11

Your system currently uses Python 3.14, which may cause compatibility issues with some packages.

Install Python 3.11 alongside it.

## Download

Go to:

https://www.python.org/downloads/release/python-3119/

Download:
- Windows installer (64-bit)

During installation:
- Enable **"Add Python to PATH"**

Verify installation:

```bash
py -3.11 --version
```

Expected output:

```bash
Python 3.11.x
```

---

# Step 2 — Get a Free Groq API Key

1. Open:
   https://console.groq.com

2. Create a free account

3. Navigate to:
   - API Keys
   - Create API Key

4. Copy your API key

It will look like:

```text
gsk_xxxxxxxxxxxxxxxxx
```

---

# Step 3 — Create Virtual Environment

Open terminal inside the project folder:

```bash
cd smart-assistant
```

Create virtual environment:

```bash
py -3.11 -m venv venv
```

---

# Step 4 — Activate Virtual Environment

## PowerShell

```bash
venv\Scripts\Activate.ps1
```

## Command Prompt

```bash
venv\Scripts\activate.bat
```

If successful, terminal shows:

```bash
(venv)
```

---

# Step 5 — Install Dependencies

```bash
pip install -r requirements.txt
```

This may take 2–4 minutes.

---

# Step 6 — Configure Environment Variables

Copy example file:

```bash
copy .env.example .env
```

Open `.env` and configure:

```env
GROQ_API_KEY=gsk_paste_your_actual_key_here
ADMIN_EMAIL=admin@demo.com
ADMIN_PASSWORD=admin123
SECRET_KEY=anyrandomlongstring123
```

---

# Step 7 — Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

Expected output:

```bash
INFO: Application startup complete.
INFO: Uvicorn running on http://127.0.0.1:8000
```

On first run:
- `smart_assistant.db` is created automatically
- `chroma_store/` is created automatically

---

# Step 8 — Open Dashboard

Open browser:

```text
http://localhost:8000/dashboard
```

Login using credentials from `.env`.

---

# Step 9 — Open API Documentation

FastAPI automatically generates interactive API docs.

Open:

```text
http://localhost:8000/docs
```

You can test every API endpoint directly from the browser.

---

# How to Use

# AI Chat

1. Open Dashboard
2. Go to Chat tab
3. Ask any business-related question

Example:

```text
How can I improve customer retention?
```

---

# Lead Capture

If a user shares contact information:

```text
Hi I'm John from Acme Corp.
My email is john@acme.com.
Interested in your services.
```

The system automatically:
- Detects lead intent
- Extracts details
- Saves lead to database

---

# Document Upload (RAG)

1. Open Documents tab
2. Upload:
   - `.txt`
   - `.pdf`

Examples:
- FAQs
- Product catalogues
- Company policies
- Pricing sheets

The AI will now answer using your uploaded data instead of hallucinating.

---

# Workflow Automation

Open Workflows tab.

Available workflows:

| Workflow | Purpose |
|---|---|
| Email Summarizer | Converts long emails into structured summaries |
| Follow-Up Generator | Generates follow-up emails from Lead ID |
| Lead Scorer | Classifies leads as Hot / Warm / Cold |

---

# Authentication

JWT authentication protects all routes.

Admin credentials are loaded from:

```env
ADMIN_EMAIL
ADMIN_PASSWORD
```

---

# Database Models

## Lead

Stores:
- Name
- Email
- Company
- Lead status
- Timestamp

## ChatMessage

Stores:
- User messages
- AI responses
- Confidence scores

## WorkflowLog

Stores:
- Workflow execution history
- Outputs
- Timestamps

---

# RAG System

The RAG pipeline works like this:

```text
Upload Document
      │
      ▼
Chunk Text
      │
      ▼
Generate Embeddings
      │
      ▼
Store in ChromaDB
      │
      ▼
Search Relevant Chunks During Chat
      │
      ▼
Inject Context Into AI Prompt
```

---

# AI Agent Pipeline

## 1. Planner Agent

Responsibilities:
- Detect intent
- Decide workflow
- Decide if RAG is needed

## 2. Executor Agent

Responsibilities:
- Search documents
- Save leads
- Generate response using Groq API

## 3. Validator Agent

Responsibilities:
- Detect hallucinations
- Improve answer quality
- Generate confidence score

---

# Assumptions & Limitations

| Limitation | Reason |
|---|---|
| No Docker | Simpler local setup |
| SQLite instead of PostgreSQL | Easier MVP deployment |
| Single admin user | Simplifies authentication |
| No streaming responses | Reduced complexity |
| No voice support | Outside MVP scope |
| Groq free-tier limits | 6000 requests/day |

---

# Common Errors & Fixes

| Error | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'app'` | Run server from root project folder |
| `GROQ_API_KEY not set` | Verify `.env` configuration |
| `Activate.ps1 cannot be loaded` | Run: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `Address already in use` | Change port to 8001 |
| Dashboard cannot connect | Ensure FastAPI server is running |

---

# Example Commands

## Run Server

```bash
uvicorn app.main:app --reload --port 8000
```

## Activate Environment

```bash
venv\Scripts\Activate.ps1
```

## Install Packages

```bash
pip install -r requirements.txt
```

---

# Future Improvements

- Multi-user support
- PostgreSQL integration
- Docker deployment
- Streaming AI responses
- Voice assistant support
- WhatsApp integration
- CRM integrations
- Role-based permissions
- Background task queues

---

# Why This Project Matters

Small businesses often cannot afford:
- Enterprise AI systems
- CRM automation tools
- AI customer support teams

This project demonstrates how modern AI systems can deliver:
- Automation
- Lead generation
- Business intelligence
- Customer support

Using completely free and open technologies.

---

# License

MIT License

---

# Author

Built as a production-oriented AI systems MVP using:
- FastAPI
- Groq
- ChromaDB
- SQLite
- Multi-Agent AI Architecture