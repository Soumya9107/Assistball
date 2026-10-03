# AssistBall Backend & AI Vision Layer

AssistBall is a floating desktop assistant backend built with **FastAPI**, **Python 3.11+**, and **Pydantic v2**. It processes screenshots taken from an Electron desktop frontend alongside user queries, passing them to vision-capable LLMs (**Claude**, **OpenAI**, or **Gemini**) and returning concise, step-by-step help.

---

## Features

- **Multi-Provider Vision AI**: Built-in support for Anthropic Claude, OpenAI, and Google Gemini vision models.
- **Dynamic Provider Factory**: Easily switch active provider and model via environment variables (`PROVIDER`, `MODEL_NAME`).
- **Streaming Support**: Server-Sent Events (SSE) streaming for real-time token delivery via `POST /ask/stream`.
- **Image Optimization & Safety**: Automatic resize (max width 1568px), JPEG re-encoding (~75% quality), small PNG preservation, base64 validation, and 5 MB payload limit.
- **Security & Rate Limiting**: Header-based API Key authentication (`X-API-Key`) and extensible in-memory sliding-window rate limiting.
- **Cost & Latency Optimization**: Only attaches screenshots to the latest turn; history is strictly text-only (max 10 turns).
- **Structured JSON Logging**: Audit logs record metadata (timestamp, session_id, image size, latency, status) without ever leaking screenshot data or raw prompt text.

---

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application, CORS, routes, exception handlers
│   ├── config.py            # Environment configuration settings (pydantic-settings)
│   ├── schemas.py           # Request & response Pydantic schemas
│   ├── prompts.py           # System prompts for vision assistant
│   ├── security.py          # API key authentication & rate limiting
│   ├── providers/
│   │   ├── base.py          # VisionProvider abstract base class & ProviderError
│   │   ├── claude.py        # Anthropic Claude provider
│   │   ├── openai_provider.py # OpenAI GPT vision provider
│   │   ├── gemini.py        # Google Gemini vision provider
│   │   └── factory.py       # Provider factory (get_provider)
│   └── services/
│       ├── assistant.py     # Orchestration layer for ask & streaming
│       └── image_utils.py   # Base64 validation, resize, compress
├── tests/
│   ├── conftest.py          # Pytest fixtures & async HTTP test client
│   ├── test_endpoints.py    # /health, /ask, /ask/stream tests
│   ├── test_image_utils.py  # Image resize, compression, rejection tests
│   ├── test_providers.py    # Factory & provider error mapping tests
│   └── test_security.py     # Authentication & rate limiting tests
├── .env.example             # Template for environment variables
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

---

## Setup & Running Locally

### 1. Prerequisites

- Python 3.11+
- Virtual environment (recommended)

### 2. Installation

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# On Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and set your API keys:

```bash
cp .env.example .env
```

Example `.env`:
```env
APP_API_KEY=assistball-secret-api-key
ALLOWED_ORIGINS=file://*,app://*,http://localhost:3000
RATE_LIMIT_PER_MIN=20

PROVIDER=claude
MODEL_NAME=claude-sonnet-5-5

ANTHROPIC_API_KEY=your-anthropic-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
```

### 4. Run Dev Server

```bash
uvicorn app.main:app --reload --port 8000
```

The server will start at `http://localhost:8000`. API documentation is available at `http://localhost:8000/docs`.

---

## Testing

Run the test suite with `pytest`:

```bash
pytest -v
```

---

## API Endpoints & cURL Examples

### 1. Health Check (`GET /health`)

Unauthenticated endpoint to check system status and active provider.

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "ok",
  "provider": "claude"
}
```

---

### 2. Vision Assistant (`POST /ask`)

Processes screenshot and query, returning complete answer.

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: assistball-secret-api-key" \
  -d '{
    "query": "Where do I click to save this file?",
    "image_b64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "media_type": "image/png",
    "history": [
      {"role": "user", "content": "How do I open preferences?"},
      {"role": "assistant", "content": "Click the gear icon in the top right."}
    ],
    "session_id": "sess_12345"
  }'
```

**Response:**
```json
{
  "answer": "Step 1: Look at the top left menu bar and click on 'File'.\nStep 2: Select 'Save As...' from the drop-down menu.",
  "provider": "claude",
  "latency_ms": 680
}
```

---

### 3. Vision Assistant SSE Stream (`POST /ask/stream`)

Streams response tokens in real-time using Server-Sent Events (SSE).

```bash
curl -X POST "http://localhost:8000/ask/stream" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: assistball-secret-api-key" \
  -d '{
    "query": "What does this error message mean?",
    "image_b64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==",
    "media_type": "image/png",
    "session_id": "sess_stream_99"
  }'
```

**Streaming Output:**
```
event: token
data: {"token": "Step "}

event: token
data: {"token": "1: "}

event: token
data: {"token": "Check your internet connection."}

event: done
data: {"answer": "Step 1: Check your internet connection.", "provider": "claude", "latency_ms": 450}
```
