"""
src/utils/config.py
Central configuration loader.
All settings are read from environment variables (via .env file).
Import `config` anywhere in the project to access settings.
"""

import os

from dotenv import load_dotenv

# Load .env file from the project root (one level up from src/)
_env_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path=_env_path, override=False)


def _require(key: str) -> str:
    """Return the env var value or raise a clear error if missing."""
    value = os.getenv(key)
    if not value:
        raise OSError(
            f"Required environment variable '{key}' is not set. "
            f"Copy .env.example to .env and fill in the values."
        )
    return value


def _optional(key: str, default: str = "") -> str:
    return os.getenv(key, default)


# ── LLM (Groq) ────────────────────────────────────────────────────────────────
LLM_MODEL: str = _optional("LLM_MODEL", "openai/gpt-oss-120b")
GROQ_API_KEY: str = _require("GROQ_API_KEY")

# ── Review Ingestion ──────────────────────────────────────────────────────────
GROWW_APP_ID: str = _optional("GROWW_APP_ID", "com.nextbillion.groww")
REVIEW_LOOKBACK_WEEKS: int = int(_optional("REVIEW_LOOKBACK_WEEKS", "10"))
REVIEW_MAX_COUNT: int = int(_optional("REVIEW_MAX_COUNT", "500"))

# ── Output / Delivery ─────────────────────────────────────────────────────────
PULSE_RECIPIENT_EMAIL: str = _optional("PULSE_RECIPIENT_EMAIL", "")

# ── MCP Servers (optional until Phase 5) ─────────────────────────────────────
GOOGLE_DOCS_MCP_URL: str = _optional("GOOGLE_DOCS_MCP_URL", "")
GMAIL_MCP_URL: str = _optional("GMAIL_MCP_URL", "")
GOOGLE_CLIENT_ID: str = _optional("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET: str = _optional("GOOGLE_CLIENT_SECRET", "")
