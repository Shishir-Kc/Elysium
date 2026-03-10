# Elysium - Home Server

Elysium is a FastAPI-based home server application that provides various services including server health monitoring, email automation, AI chat capabilities, and background task processing.

## Technology Stack

- **Framework**: FastAPI
- **Task Queue**: Celery with Redis
- **AI**: LangChain with Groq integration
- **Email**: aiosmtplib
- **Async HTTP**: httpx
- **Python**: 3.12+

---

## Project Architecture

```
Elysium/
├── main.py                     # FastAPI application entry point
├── server_logging.py          # Server-wide logging configuration
├── pyproject.toml             # Project metadata and dependencies
├── requirements.txt           # Python dependencies
│
├── api/
│   └── v1/                    # API Version 1
│       ├── __init__.py        # Router aggregation
│       │
│       ├── server_status/     # Server health endpoints
│       │   └── server_health.py
│       │
│       ├── Hyper_status/      # Hyper server monitoring
│       │   └── hyper_stats.py
│       │
│       ├── email/             # Email endpoints
│       │   └── email.py
│       │
│       ├── ai/               # AI chat endpoints
│       │   └── ai_chat.py
│       │
│       ├── Test_workers/     # Celery worker testing
│       │   └── workers_test.py
│       │
│       └── websocket/        # WebSocket endpoints
│           └── laptop_price.py
│
├── services/
│   ├── Email/                 # Email service
│   │   ├── __init__.py
│   │   └── email_service.py  # Async email sending via SMTP
│   │
│   └── Server_Dir_check/      # Server directory integrity
│       └── server_file_integrety.py  # Creates required log directories
│
├── Elysium_Celery/            # Celery task configuration
│   ├── config.py              # Celery broker/backend setup
│   └── tasks.py               # Background tasks (email, test)
│
├── Elysium_Config/            # Configuration management
│   ├── Email/
│   │   └── email_config.py    # SMTP credentials from .env
│   └── Ai/
│       └── config_groq.py     # Groq API key configuration
│
├── AI/                        # AI integration
│   ├── Cloud/
│   │   └── Groq/
│   │       └── groq_ai.py     # LangChain Groq agent
│   └── Tools/
│       └── email.py           # AI tool for sending emails
│
├── Tools/                     # Utility tools
│   ├── Hyper/
│   │   ├── __init__.py
│   │   └── hyper_health.py    # Hyper server status checker
│   │
│   ├── Progress_bar/
│   │   └── smooth_bar.py      # Animated progress bar
│   │
│   └── elysium/
│       └── elysium.py         # Logging setup
│
├── Database/
│   └── Schema/
│       └── Email/
│           └── email_schema.py  # Pydantic email model
│
└── assets/
    └── Elysium/               # Server branding assets
        ├── __init__.py
        ├── start_up.py       # Startup/shutdown routines
        ├── branding.txt      # ASCII art logo
        ├── shutting.txt      # Shutdown message
        └── restarting.txt    # Restart message
```

---

## Directory & File Purpose

### Root Level

| File | Purpose |
|------|---------|
| `main.py` | FastAPI app initialization with CORS middleware, lifespan context manager, and router inclusion |
| `server_logging.py` | Global logger instance for the server |
| `pyproject.toml` | Project metadata (name: elysium, version: 0.1.0) |
| `requirements.txt` | All Python dependencies |

### `api/v1/` - API Endpoints

| File | Endpoint | Description |
|------|----------|-------------|
| `server_health.py` | `GET /api/v1/health` | Returns server health status |
| `hyper_stats.py` | `GET /api/v1/hyper/status/` | Checks if Hyper server is active |
| `email.py` | `POST /api/v1/send/email` | Queues email sending via Celery |
| `ai_chat.py` | `POST /api/v1/chat/Agent` | Chat with AI agent using Groq |
| `workers_test.py` | `POST /api/v1/start/test/worker` | Test Celery worker |
| `laptop_price.py` | WebSocket `/api/v1/ws/` | Real-time price updates (dummy) |

### `services/` - Core Services

| File | Purpose |
|------|---------|
| `email_service.py` | Async SMTP email sending using `aiosmtplib` |
| `server_file_integrety.py` | Checks/creates `Logs/Hyper` and `Logs/Elysium` directories on startup |

### `Elysium_Celery/` - Background Tasks

| File | Purpose |
|------|---------|
| `config.py` | Celery config with Redis broker/backend (localhost:6379) |
| `tasks.py` | Celery tasks: `idk_man` (test), `sending_mail` (async email) |

### `Elysium_Config/` - Configuration

| File | Purpose |
|------|---------|
| `email_config.py` | Loads SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS from `.env` |
| `config_groq.py` | Loads Groq API key from `.env` |

### `AI/` - Artificial Intelligence

| File | Purpose |
|------|---------|
| `groq_ai.py` | LangChain agent using ChatGroq with email tool |
| `email.py` | LangChain `@tool` decorator for AI-driven email sending |

### `Tools/` - Utilities

| File | Purpose |
|------|---------|
| `hyper_health.py` | Checks Hyper server status via HTTP request |
| `smooth_bar.py` | Animated console progress bar |
| `elysium.py` | Server logging configuration |

### `Database/Schema/` - Data Models

| File | Purpose |
|------|---------|
| `email_schema.py` | Pydantic model: `Email_Schema` with subject, receiver, content |

### `assets/Elysium/` - Branding

| File | Purpose |
|------|---------|
| `start_up.py` | `wakey_wakey()` prints logo on startup, `sleppy_sleppy()` on shutdown |
| `branding.txt` | Elysium ASCII art logo |
| `shutdown.txt` | Shutdown message |
| `restarting.txt` | Restart message |

---

## Code Flow

1. **Startup** (`main.py`):
   - `Lifespan` context manager runs `check_sys_dir()` then `wakey_wakey()`
   - Creates required log directories
   - Prints branding logo

2. **API Requests**:
   - All routes prefixed with `/api/v1`
   - CORS enabled for all origins

3. **Email Flow**:
   - POST to `/api/v1/send/email` → Celery task `sending_mail.delay()`
   - Celery worker executes `prepare_email()` via `aiosmtplib`

4. **AI Chat Flow**:
   - POST to `/api/v1/chat/Agent` → LangChain agent with Groq
   - Agent can use `send_email` tool to send emails

5. **WebSocket**:
   - `/api/v1/ws/` endpoint sends dummy laptop prices every 10 seconds

6. **Shutdown**:
   - `sleppy_sleppy()` prints shutdown message

---

## Running the Server

```bash
# Start Redis (required for Celery)
redis-server

# Start Celery worker
celery -A Elysium_Celery.config worker --loglevel=info

# Start FastAPI server
uvicorn main:elysium_server --reload
```

---

## Environment Variables (.env)

```
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=your_email@example.com
SMTP_PASS=your_password
GROQ=your_groq_api_key
```
