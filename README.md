# NetSage AI

NetSage AI is a local-first Cisco troubleshooting assistant. React sends evidence to Flask, which runs deterministic checks, retrieves verified cases, asks a local Qwen GGUF model through `llama-cli`, validates the JSON response, and stores the complete investigation in `data/history/`. Every recommendation requires human review and no Cisco command is executed automatically.

## Setup

From PowerShell at the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python training\prepare_dataset.py
cd frontend
npm install
```

Copy `.env.example` to `.env` and set `LLAMA_CLI_PATH` if `llama-cli.exe` is not on PATH. `MODEL_PATH` defaults to `models/base/Qwen3-4B-Q4_K_M.gguf`. The llama.cpp path uses CPU-compatible flags and does not assume CUDA; AMD GPU acceleration can be configured separately in the llama.cpp build. Local Qwen is attempted first. When it is unavailable, set `OPENROUTER_API_KEY` to use the configured free OpenRouter model. Network evidence is sent to OpenRouter only when this key is explicitly configured.

## Run

Terminal 1:

```powershell
.\.venv\Scripts\Activate.ps1
python backend\app.py
```

Terminal 2:

```powershell
cd frontend
npm run dev
```

Open `http://localhost:5173`. Test the backend with `Invoke-RestMethod http://127.0.0.1:5000/api/health`.

## API

`GET /api/health`, `POST /api/diagnose`, `GET /api/history`, `GET /api/history/<case_id>`, `GET /api/roadmap/<case_id>`, `POST /api/step/<case_id>`, `POST /api/review/<case_id>`, `GET /api/cases`, and `POST /api/cases` are implemented in `backend/app.py`.

## Data and roadmap

`training/prepare_dataset.py` merges CSV cases into JSON by `case_id`. Diagnoses are immutable history records; reviews are also copied to `data/reviews/`. Reviewed corrections can later be converted into JSONL chat records. Do not fine-tune until at least 30-40 high-quality reviewed cases exist. The current system is retrieval plus deterministic validation and structured prompting, not fine-tuning.

The initial LLM integration starts `llama-cli` per request, which is simple but slower. A persistent llama.cpp server can replace `backend/llm.py` later without changing the API. All user-provided command output is treated as untrusted text.
