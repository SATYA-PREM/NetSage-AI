import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

ROOT_DIR = Path(__file__).resolve().parent.parent
if load_dotenv:
    load_dotenv(ROOT_DIR / ".env")
DATA_DIR = ROOT_DIR / "data"
HISTORY_DIR = DATA_DIR / "history"
REVIEWS_DIR = DATA_DIR / "reviews"
KNOWLEDGE_FILE = DATA_DIR / "knowledge" / "cases.json"
MODEL_PATH = Path(os.getenv("MODEL_PATH", str(ROOT_DIR / "models" / "base" / "Qwen3-4B-Q4_K_M.gguf")))
LLAMA_CLI_PATH = os.getenv("LLAMA_CLI_PATH", "llama-cli.exe")
LLAMA_SERVER_URL = os.getenv("LLAMA_SERVER_URL", "http://127.0.0.1:8080/v1/chat/completions")
LLAMA_SERVER_MODEL = os.getenv("LLAMA_SERVER_MODEL", "local-model")
LLAMA_CLI_FALLBACK = os.getenv("LLAMA_CLI_FALLBACK", "false").lower() == "true"
HOST = os.getenv("HOST", "127.0.0.1")
PORT = int(os.getenv("PORT", "5000"))
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemma-3-27b-it:free")
OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1/chat/completions")

for directory in (HISTORY_DIR, REVIEWS_DIR, KNOWLEDGE_FILE.parent):
    directory.mkdir(parents=True, exist_ok=True)
