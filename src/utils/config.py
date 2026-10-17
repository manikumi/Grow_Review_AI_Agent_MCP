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
# gpt-oss models reason before answering; keep reasoning short so it does not
# use up max_tokens and leave an empty (invalid) JSON response.
LLM_EXTRA_PARAMS: dict = {"reasoning_effort": "low"} if "gpt-oss" in LLM_MODEL else {}

# ── Review Ingestion ──────────────────────────────────────────────────────────
GROWW_APP_ID: str = _optional("GROWW_APP_ID", "com.nextbillion.groww")
REVIEW_LOOKBACK_WEEKS: int = int(_optional("REVIEW_LOOKBACK_WEEKS", "10"))
REVIEW_MAX_COUNT: int = int(_optional("REVIEW_MAX_COUNT", "500"))

# ── Output / Delivery ─────────────────────────────────────────────────────────
PULSE_RECIPIENT_EMAIL: str = _optional("PULSE_RECIPIENT_EMAIL", "")

# ── MCP Servers (optional until Phase 5) ─────────────────────────────────────
def _clean(key: str) -> str:
    """Read an env var and strip whitespace and wrapping quotes (common when pasted into a dashboard)."""
    return _optional(key, "").strip().strip("'\"").strip()


GOOGLE_DOCS_MCP_URL: str = _clean("GOOGLE_DOCS_MCP_URL")
GMAIL_MCP_URL: str = _clean("GMAIL_MCP_URL")
GOOGLE_DOC_URL: str = _clean("GOOGLE_DOC_URL")
GOOGLE_DOC_ID: str = _clean("GOOGLE_DOC_ID")

import re as _re

# Accept a full Doc URL pasted into GOOGLE_DOC_ID, or derive the ID from GOOGLE_DOC_URL
for _source in (GOOGLE_DOC_ID, GOOGLE_DOC_URL):
    _match = _re.search(r"/document/d/([a-zA-Z0-9_-]+)", _source)
    if _match:
        GOOGLE_DOC_ID = _match.group(1)
        break
if GOOGLE_DOC_ID.startswith("your_"):
    GOOGLE_DOC_ID = ""

GOOGLE_CLIENT_ID: str = _optional("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET: str = _optional("GOOGLE_CLIENT_SECRET", "")

