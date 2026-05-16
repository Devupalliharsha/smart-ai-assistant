<div align="center">

# 🤖 Smart AI Business Assistant

### Production-Oriented AI Automation Platform for Small Businesses

<img src="https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python" />
<img src="https://img.shields.io/badge/FastAPI-Backend-009688?style=for-the-badge&logo=fastapi" />
<img src="https://img.shields.io/badge/Groq-Llama3-orange?style=for-the-badge" />
<img src="https://img.shields.io/badge/ChromaDB-VectorDB-purple?style=for-the-badge" />
<img src="https://img.shields.io/badge/SQLite-Database-07405E?style=for-the-badge&logo=sqlite" />
<img src="https://img.shields.io/badge/JWT-Authentication-black?style=for-the-badge" />
<img src="https://img.shields.io/badge/Status-MVP-success?style=for-the-badge" />

<br/>
<br/>

### 🚀 AI Chat • 📚 RAG • 📈 Lead Capture • ⚡ Automation • 📊 Analytics

</div>

---

# ✨ Overview

**Smart AI Business Assistant** is a production-oriented AI automation platform designed for startups and small businesses.

It combines:

- 🤖 Multi-Agent AI
- 📚 RAG (Retrieval-Augmented Generation)
- 📈 Lead Management
- ⚡ Workflow Automation
- 📊 Analytics Dashboard
- 🔐 JWT Authentication

All inside a lightweight, scalable FastAPI application.

---

# 🎯 Core Features

<div align="center">

| Feature | Description |
|---|---|
| 🤖 AI Chat | Chat with an intelligent multi-agent AI assistant |
| 🧠 Multi-Agent Pipeline | Planner → Executor → Validator architecture |
| 📚 RAG Document Q&A | Upload documents and let AI answer from them |
| 📈 Automatic Lead Capture | Extracts emails, names, and business leads automatically |
| ⚡ Workflow Automation | Email summarizer, follow-up generator, lead scoring |
| 📊 Analytics Dashboard | Monitor chats, leads, workflows, and activity |
| 🔐 JWT Authentication | Secure admin authentication |
| 🗄 SQLite Database | Lightweight local storage |
| 🔍 ChromaDB Vector Search | Semantic document retrieval |
| 📖 Interactive API Docs | FastAPI Swagger UI |

</div>

---

# 🏗 System Architecture

```text
                    ┌────────────────────┐
                    │    USER MESSAGE    │
                    └─────────┬──────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │      🧠 PLANNER AGENT    │
                │──────────────────────────│
                │ • Detects intent         │
                │ • Determines workflow    │
                │ • Checks RAG necessity   │
                └─────────┬────────────────┘
                          │
                          ▼
                ┌──────────────────────────┐
                │     ⚙ EXECUTOR AGENT     │
                │──────────────────────────│
                │ • Searches documents     │
                │ • Saves leads            │
                │ • Calls Groq API         │
                │ • Generates response     │
                └─────────┬────────────────┘
                          │
                          ▼
                ┌──────────────────────────┐
                │    ✅ VALIDATOR AGENT     │
                │──────────────────────────│
                │ • Detects hallucinations │
                │ • Improves reliability   │
                │ • Returns confidence     │
                └─────────┬────────────────┘
                          │
                          ▼
                ┌──────────────────────────┐
                │ FINAL RESPONSE + LOGGING │
                └──────────────────────────┘
```

---

# 🛠 Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|---|---|---|
| 🐍 Language | Python 3.11 | Stable & highly compatible |
| ⚡ Backend | FastAPI | High-performance async APIs |
| 🤖 AI Model | Groq + Llama 3 8B | Ultra-fast inference |
| 📚 Vector Database | ChromaDB | Semantic search & embeddings |
| 🗄 Database | SQLite | Lightweight local storage |
| 🌐 Frontend | HTML + JavaScript | Lightweight dashboard |
| 🔐 Auth | JWT | Secure authentication |
| 📄 Docs | Swagger/OpenAPI | Interactive API testing |

</div>

---

# 📂 Project Structure

```text
smart-assistant/
│
├── app/
│   ├── __init__.py
│   ├── main.py                # FastAPI entry point
│   ├── database.py            # SQLite models
│   ├── rag.py                 # ChromaDB vector store
│   ├── agents.py              # Multi-agent system
│   ├── workflows.py           # Automation workflows
│   │
│   └── dashboard/
│       └── index.html         # Admin dashboard UI
│
├── chroma_store/              # Vector embeddings
├── smart_assistant.db         # SQLite database
├── .env                       # Environment variables
├── .env.example               # Example configuration
├── requirements.txt           # Python dependencies
└── README.md
```

---

# ⚙ Setup Guide

# 1️⃣ Install Python 3.11

Your system currently uses Python 3.14, which may cause compatibility issues with some dependencies.

Install Python 3.11 alongside it.

## 📥 Download

👉 https://www.python.org/downloads/release/python-3119/

Download:
- **Windows installer (64-bit)**

During installation:
- ✅ Enable **Add Python to PATH**

Verify installation:

```bash
py -3.11 --version
```

Expected output:

```bash
Python 3.11.x
```

---

# 2️⃣ Get a Free Groq API Key

## 🔑 Steps

1. Open:
   https://console.groq.com

2. Create a free account

3. Navigate to:
   - API Keys
   - Create API Key

4. Copy your key

Example:

```text
gsk_xxxxxxxxxxxxxxxxx
```

---

# 3️⃣ Clone or Open Project

```bash
cd smart-assistant
```

---

# 4️⃣ Create Virtual Environment

```bash
py -3.11 -m venv venv
```

---

# 5️⃣ Activate Virtual Environment

## PowerShell

```bash
venv\Scripts\Activate.ps1
```

## CMD

```bash
venv\Scripts\activate.bat
```

Successful activation:

```bash
(venv)
```

---

# 6️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

⏳ Installation may take 2–4 minutes.

---

# 7️⃣ Configure Environment Variables

Copy example file:

```bash
copy .env.example .env
```

Open `.env` and configure:

```env
GROQ_API_KEY=gsk_paste_your_actual_key_here

ADMIN_EMAIL=admin@demo.com
ADMIN_PASSWORD=admin123

SECRET_KEY=your_super_secret_key_here
```

---

# 8️⃣ Run the Server

```bash
uvicorn app.main:app --reload --port 8000
```

Expected output:

```bash
INFO: Application startup complete.
INFO: Uvicorn running on http://127.0.0.1:8000
```

---

# 9️⃣ Open Dashboard

🌐 Open:

```text
http://localhost:8000/dashboard
```

Login using credentials from `.env`.

---

# 🔟 Open API Docs

FastAPI automatically generates Swagger docs.

🌐 Open:

```text
http://localhost:8000/docs
```

Test all endpoints directly from the browser.

---

# 💡 Usage Guide

# 🤖 AI Chat

1. Open Dashboard
2. Navigate to Chat
3. Ask business-related questions

Example:

```text
How can I improve customer retention?
```

---

# 📈 Lead Capture

If users share contact information:

```text
Hi I'm John from Acme Corp.
Email: john@acme.com
Interested in your services.
```

The system automatically:

- Detects lead intent
- Extracts details
- Saves lead to database

---

# 📚 RAG Document Upload

Supported files:
- `.txt`
- `.pdf`

Examples:
- FAQs
- Product catalogues
- Pricing sheets
- Company documents

The AI retrieves answers directly from uploaded files instead of hallucinating.

---

# ⚡ Workflow Automation

Available workflows:

| Workflow | Description |
|---|---|
| 📧 Email Summarizer | Converts long emails into structured summaries |
| ✉ Follow-Up Generator | Generates follow-up emails using Lead IDs |
| 🔥 Lead Scorer | Classifies leads as Hot / Warm / Cold |

---

# 🔐 Authentication

JWT-based authentication secures all protected routes.

Credentials are loaded from:

```env
ADMIN_EMAIL
ADMIN_PASSWORD
```

---

# 🗄 Database Models

# 📈 Lead

Stores:
- Name
- Email
- Company
- Lead Status
- Timestamp

---

# 💬 ChatMessage

Stores:
- User messages
- AI responses
- Confidence scores

---

# ⚡ WorkflowLog

Stores:
- Workflow execution history
- Outputs
- Timestamps

---

# 📚 RAG Pipeline

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
Semantic Search
        │
        ▼
Inject Context Into Prompt
        │
        ▼
Generate Reliable AI Response
```

---

# 🧠 AI Agent Responsibilities

# 🧠 Planner Agent

Responsibilities:
- Intent classification
- Workflow selection
- RAG requirement detection

---

# ⚙ Executor Agent

Responsibilities:
- Document retrieval
- Lead saving
- AI generation via Groq

---

# ✅ Validator Agent

Responsibilities:
- Hallucination detection
- Reliability improvement
- Confidence scoring

---

# 📊 Dashboard Features

The admin dashboard includes:

- 💬 Conversation Logs
- 📈 Lead Analytics
- ⚡ Workflow History
- 📚 Document Management
- 🔍 Search & Filtering
- 📊 System Monitoring

---

# ⚠ Assumptions & Limitations

| Limitation | Reason |
|---|---|
| No Docker | Simpler setup for MVP |
| SQLite instead of PostgreSQL | Lightweight deployment |
| Single admin user | Simpler authentication |
| No streaming responses | Reduced complexity |
| No voice support | Outside MVP scope |
| Groq free-tier limits | 6000 req/day |

---

# 🛑 Common Errors & Fixes

| Error | Solution |
|---|---|
| `ModuleNotFoundError: No module named 'app'` | Run server from root project folder |
| `GROQ_API_KEY not set` | Verify `.env` configuration |
| `Activate.ps1 cannot be loaded` | Run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `Address already in use` | Change port to 8001 |
| Dashboard cannot connect | Ensure FastAPI server is running |

---

# 🚀 Example Commands

# ▶ Run Server

```bash
uvicorn app.main:app --reload --port 8000
```

# ▶ Activate Environment

```bash
venv\Scripts\Activate.ps1
```

# ▶ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔮 Future Improvements

- 👥 Multi-user support
- 🐳 Docker deployment
- 🐘 PostgreSQL integration
- 🔄 Streaming AI responses
- 🎤 Voice assistant support
- 📱 WhatsApp integration
- 🔗 CRM integrations
- 🧵 Background task queues
- 🛡 Role-based access control

---

# 🌍 Why This Project Matters

Small businesses often cannot afford:

- Enterprise AI systems
- CRM automation platforms
- Dedicated AI support tools

This project demonstrates how modern AI can provide:

- 🤖 Automation
- 📈 Lead generation
- 📊 Business intelligence
- 💬 Customer support

Using completely free and open technologies.

---

# 📜 License

MIT License

---

# 👨‍💻 Author devupalliharsha 

Built as a production-oriented AI systems MVP using:

- FastAPI
- Groq
- ChromaDB
- SQLite
- Multi-Agent AI Architecture

---

<div align="center">

# ⭐ If you like this project, consider starring it!


</div>
