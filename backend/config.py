from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root
ROOT_DIR = Path(__file__).resolve().parent.parent

# Directories
DATA_DIR = ROOT_DIR / "data"
PROMPTS_DIR = ROOT_DIR / "prompts"


class Settings(BaseSettings):

    # Application
    APP_NAME: str = "NetSage AI"
    APP_VERSION: str = "1.0.0"

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Gemini
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-3.6-flash"

    # LLM configuration
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 1500

    # Data files
    CASES_FILE: Path = DATA_DIR / "cases.csv"
    DIAGNOSES_FILE: Path = DATA_DIR / "diagnoses.json"
    REVIEWS_FILE: Path = DATA_DIR / "reviews.json"
    RESPONSIBLE_AI_FILE: Path = (
        DATA_DIR / "responsible_ai_log.json"
    )

    # Prompt
    PROMPT_FILE: Path = (
        PROMPTS_DIR / "diagnose_prompt.md"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# IMPORTANT:
# main.py imports this object.
settings = Settings()