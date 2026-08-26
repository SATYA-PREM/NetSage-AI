# NetSage AI

NetSage AI is an AI-assisted network troubleshooting application. It combines deterministic network rules with Gemini-generated diagnosis reports and provides a React dashboard for cases, evidence, diagnosis, and reviews.

## Stack

- Backend: Python, FastAPI, Uvicorn, Pydantic Settings
- AI: Google Gemini through `google-genai`
- Frontend: React 18, Vite, React Router, Lucide React
- Data: CSV and JSON files in `data/`

## Project Structure

```text
backend/       FastAPI application, API routes, rules, and services
data/          Cases, diagnoses, reviews, and responsible-AI log files
frontend/      React and Vite web application
prompts/       Gemini diagnosis prompt
tests/         Test directory
```

## Prerequisites

Install the following before starting:

- Python 3.10 or newer
- Node.js 18 or newer and npm
- A Google Gemini API key

## Configuration

Create a `.env` file in the repository root:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.6-flash
HOST=127.0.0.1
PORT=8000
```

`GEMINI_API_KEY` is required when the backend starts. Never commit a real API key or share it in documentation. If a key has been exposed, revoke it and create a replacement.

## Backend Setup and Run

Open PowerShell at the repository root:

```powershell
cd D:\PROJECTS\NetSage-AI\ai\NetSage-AI

# Create a virtual environment (first setup only)
python -m venv .venv

# Activate it for the current PowerShell session
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1

# Install backend dependencies
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt

# Start the API with auto-reload
python -m uvicorn backend.main:app --reload
```

The backend is available at:

- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/health

To use a different host or port:

```powershell
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

Stop the backend with `Ctrl+C`.

## Frontend Setup and Run

Open a second PowerShell window at the repository root:

```powershell
cd D:\PROJECTS\NetSage-AI\ai\NetSage-AI\frontend

# Install frontend dependencies (first setup only)
npm install

# Start the Vite development server
npm run dev
```

Open the URL printed by Vite, normally http://localhost:5173.

Stop the frontend with `Ctrl+C`.

### Frontend Commands

Run these from `frontend/`:

```powershell
npm run dev       # Development server
npm run build     # Production build in frontend/dist
npm run preview   # Preview the production build locally
```

## API Endpoints

All API routes are defined in `backend/main.py` and are available under `/api`:

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | API status and version |
| `GET` | `/health` | Health check |
| `GET` | `/api/cases` | List troubleshooting cases from `data/cases.csv` |
| `POST` | `/api/diagnosis` | Generate a diagnosis for a network symptom |
| `GET` | `/api/reviews` | List saved reviews |
| `POST` | `/api/reviews` | Save a diagnosis review |
| `GET` | `/api/dashboard` | Return dashboard metrics |

The complete request and response schemas are available in Swagger UI at `/docs`.

### Diagnosis Request Example

```powershell
Invoke-RestMethod `
  -Uri http://127.0.0.1:8000/api/diagnosis `
  -Method Post `
  -ContentType "application/json" `
  -Body (@{
    case_id = "CUSTOM"
    symptom = "Users cannot reach the application server"
    topology = "Client -> access switch -> router -> server VLAN"
    command_output = "show ip route"
    device = "R1"
    device_type = "router"
    severity = "High"
  } | ConvertTo-Json)
```

A diagnosis request must include a non-empty `symptom`. The remaining fields are optional and default to empty strings or `Medium` severity.

## Data Files

- `data/cases.csv`: Troubleshooting cases shown in the frontend
- `data/diagnoses.json`: Stored diagnosis data
- `data/reviews.json`: User review data
- `data/responsible_ai_log.json`: Responsible-AI activity log
- `prompts/diagnose_prompt.md`: Prompt used to synthesize diagnosis reports

The backend resolves these paths relative to the repository root, so run it from the root directory when troubleshooting import or configuration issues.

## Verification

From the repository root, with the virtual environment activated:

```powershell
python -c "from backend.main import app; print(app.title)"
```

From `frontend/`:

```powershell
npm run build
```

You can also verify the running API:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "service": "netsage-ai-backend"
}
```

## Troubleshooting

### `GEMINI_API_KEY` validation error

Ensure `.env` exists at the repository root and contains a valid `GEMINI_API_KEY`. Restart Uvicorn after changing it.

### `ModuleNotFoundError: backend`

Run Uvicorn from the repository root and use:

```powershell
python -m uvicorn backend.main:app --reload
```

### Frontend cannot reach the API

Confirm that the backend is running on port `8000` and the frontend is running on port `5173` or `5174`. Those frontend origins are enabled by the backend CORS configuration.

### Port already in use

Start the backend on another port and update the frontend API configuration if needed:

```powershell
python -m uvicorn backend.main:app --port 8001 --reload
```

## Development Notes

- The rule engine runs before Gemini diagnosis synthesis.
- Changes to backend Python files reload the API when Uvicorn is started with `--reload`.
- Changes to frontend files are handled by Vite hot module replacement.
- There are currently no test files in `tests/`; add focused tests as backend behavior grows.
