# Implementation Plan — Grow Review AI Agent (MCP)

> **Model:** `openai/gpt-oss-120b` on **Groq** (via `LLM_MODEL` env var)
> **Integration:** Model Context Protocol (MCP) over SSE for Google Docs & Gmail
> **Frontend:** Stitch Dark Dashboard (`frontend/index.html`) with dynamic clustering & SSE log stream
> **API Server:** FastAPI (`src/api.py`) with REST & SSE endpoints
> **Language:** Python 3.11+

---

## Overview

| Phase | Name | Goal | Status |
|-------|------|------|--------|
| 1 | Project Bootstrap | Scaffold repo, config, and dev environment | ✅ Completed |
| 2 | Review Ingestion | Fetch & normalise public Groww Play Store reviews | ✅ Completed |
| 3 | Processing Pipeline | PII scrubbing → theme clustering → pulse generation | ✅ Completed |
| 4 | Local Output (Dry Run) | Save pulse locally in Markdown & JSON format | ✅ Completed |
| 5 | MCP Integration | Wire Google Docs + Gmail MCP servers over SSE | ✅ Completed |
| 6 | Hardening & Tests | Unit tests, error handling, PII checks (18/18 passing) | ✅ Completed |
| 7 | Documentation & Wrap-up | Architecture, implementation plan, and README | ✅ Completed |
| 8 | Web Dashboard & Cloud Deploy | FastAPI SSE server, Stitch UI, Railway & Vercel deployment | ✅ Completed |

---

## Phase 1 — Project Bootstrap

**Goal:** Establish the full repository structure, configuration, and a working Python environment.

### Tasks
- [x] **1.1** Create the directory structure as defined in `architecture.md`:
  `src/ingestion/`, `src/processing/`, `src/mcp/`, `src/utils/`, `tests/`, `config/`, `docs/`, `frontend/`, `output/`
- [x] **1.2** Create `.env.example` with all required environment variables:
  `LLM_MODEL`, `GROQ_API_KEY`, `GROWW_APP_ID`, `REVIEW_LOOKBACK_WEEKS`, `REVIEW_MAX_COUNT`, `PULSE_RECIPIENT_EMAIL`, `GOOGLE_DOCS_MCP_URL`, `GMAIL_MCP_URL`
- [x] **1.3** Create `requirements.txt` with modern dependencies (`groq`, `fastapi`, `uvicorn`, `mcp`, `google-play-scraper`, `pydantic`, `pytest`)
- [x] **1.4** Create `src/utils/config.py` — centralized configuration loader using `python-dotenv`
- [x] **1.5** Create all `__init__.py` module files
- [x] **1.6** Set up Python virtual environment and install dependencies
- [x] **1.7** Create `.gitignore` to prevent secret and cache leaks

### Exit Criteria
- `src/utils/config.py` loads environment variables correctly
- Virtual environment active with all core dependencies installed

---

## Phase 2 — Review Ingestion

**Goal:** Pull public Groww Play Store reviews and normalise them into a typed schema — with no PII stored.

### Files
| File | Purpose |
|------|---------|
| `src/ingestion/models.py` | `Review` and `CleanReview` Pydantic models |
| `src/ingestion/fetcher.py` | Fetches reviews via `google-play-scraper` |

### Tasks
- [x] **2.1** Define the `Review` Pydantic model in `models.py` with anonymized SHA-256 IDs
- [x] **2.2** Implement `fetcher.py` → `fetch_reviews(app_id, lookback_weeks, max_count) -> list[Review]`
  - Use `google_play_scraper.reviews()` with `lang="en"`, `country="in"`
  - Filter reviews within dynamic lookback window
  - Exclude reviewer names at ingest time (never store user profile data)
  - Deduplicate by text hash `id`
- [x] **2.3** Add logging for fetch progress and count statistics
- [x] **2.4** Manual smoke testing against live Groww store reviews

### Exit Criteria
- `fetch_reviews()` returns structured `Review` list from public listing
- Zero reviewer usernames, emails, or personal identifiers captured

---

## Phase 3 — Processing Pipeline

**Goal:** Transform raw reviews into an executive weekly pulse using `openai/gpt-oss-120b` on Groq.

### 3A — PII Scrubber
| File | Purpose |
|------|---------|
| `src/processing/scrubber.py` | Strips PII from review text before LLM processing |

- [x] **3A.1** Define `CleanReview` model
- [x] **3A.2** Implement `scrub(reviews: list[Review]) -> list[CleanReview]`:
  - Regex patterns for email addresses, phone numbers, UPI handles (`@okhdfcbank`, `@ybl`, etc.), device identifiers
  - Replace matches with `[REDACTED]`
  - Discard reviews where >50% of content is redacted
- [x] **3A.3** Unit tests verifying email, phone, and UPI ID redaction

### 3B — Theme Clustering Engine
| File | Purpose |
|------|---------|
| `src/processing/clusterer.py` | Groups reviews into ≤5 strategic themes via Groq LLM |
| `src/utils/prompts.py` | Prompt templates |

- [x] **3B.1** Define `ThemeCluster` model (`name`, `review_ids`, `count`, `summary`)
- [x] **3B.2** Write clustering prompt in `prompts.py` enforcing strict JSON output and max 5 themes
- [x] **3B.3** Implement `cluster_themes(reviews: list[CleanReview]) -> list[ThemeCluster]`:
  - Batch reviews to respect Groq context limits
  - Call `groq_client.chat.completions.create(model=config.LLM_MODEL)`
  - Enforce ≤5 themes post-parse (aggregate any excess into nearest bucket)
- [x] **3B.4** Unit test with mock LLM responses and fallback logic

### 3C — Pulse Generator
| File | Purpose |
|------|---------|
| `src/processing/pulse_generator.py` | Builds the final executive pulse |

- [x] **3C.1** Define `WeeklyPulse` model (`week_ending`, `top_themes`, `user_quotes`, `action_ideas`, `word_count`)
- [x] **3C.2** Implement `generate_pulse(clusters, clean_reviews) -> WeeklyPulse`:
  - Select top 3 clusters by volume
  - Select 3 representative verbatim quotes directly from `clean_reviews` (no LLM generation)
  - Generate 3 prioritized action ideas with Groq LLM
  - Enforce word count limit (≤250 words) on rendered pulse
- [x] **3C.3** Implement `render_pulse(pulse: WeeklyPulse) -> str` to produce Markdown
- [x] **3C.4** Unit tests validating exactly 3 quotes, 3 action ideas, and word-count threshold

### Exit Criteria
- End-to-end processing pipeline runs and validates output models
- Word count strictly ≤ 250 words; quotes are authentic review snippets

---

## Phase 4 — Local Dry-Run Output

**Goal:** Validate pipeline locally and generate local artifacts before remote dispatch.

### Files
| File | Purpose |
|------|---------|
| `src/agent.py` | Orchestrator wiring ingestion, processing, and output |

- [x] **4.1** Implement `agent.py` with `run_pipeline(lookback_weeks, max_count, step_callback)`
- [x] **4.2** Save rendered pulse to `output/pulse_YYYY-MM-DD.md`
- [x] **4.3** Output structured JSON files:
  - `output/latest_pulse.json`: Typed pulse object for UI rendering
  - `output/latest_reviews.json`: Recent cleaned reviews with assigned theme labels
- [x] **4.4** Add standalone CLI support (`python -m src.agent`)

### Exit Criteria
- CLI executes smoothly and outputs local Markdown and JSON artifacts

---

## Phase 5 — MCP Integration (Railway Server over SSE)

**Goal:** Deliver executive pulse via real Model Context Protocol (MCP) server on Railway.

### Files
| File | Purpose |
|------|---------|
| `config/mcp_servers.json` | MCP configuration definition |
| `src/mcp/router.py` | Dispatches to MCP server over SSE |
| `src/mcp/docs_mcp.py` | Google Docs tool invocations (`google_docs_create_document`, `append_text`) |
| `src/mcp/gmail_mcp.py` | Gmail tool invocations (`gmail_create_draft`, `gmail_send_message`) |

- [x] **5.1** Integrated live Railway Google Workspace MCP Server:
  `https://gmailgoogledocmcpserver-production.up.railway.app/sse`
- [x] **5.2** Implemented asynchronous SSE transport using `mcp.client.sse.sse_client` and `ClientSession`
- [x] **5.3** Implemented Google Docs tool calls: created real Google Docs with rendered Markdown pulse
- [x] **5.4** Implemented Gmail tool calls: created real Gmail draft and delivery messages addressed to `PULSE_RECIPIENT_EMAIL`
- [x] **5.5** Built graceful error handling and local fallback if remote MCP server is unreachable

### Exit Criteria
- Real Google Doc created and Gmail message drafted through live MCP server
- Zero proprietary Google API code in the core agent; 100% MCP compliant

---

## Phase 6 — Hardening & Automated Testing

**Goal:** Solidify error handling, test coverage, and pipeline reliability.

### Files
| Test File | Description |
|-----------|-------------|
| `tests/test_scrubber.py` | Verifies PII redaction (email, phone, UPI handles) |
| `tests/test_clusterer.py` | Tests theme parsing, max-5 enforcement, JSON error recovery |
| `tests/test_pulse_generator.py` | Validates verbatim quotes, word count (≤250 words), and action ideas |
| `tests/test_fetcher.py` | Verifies date filtering, deduplication, PII exclusion |
| `tests/test_api.py` | Validates FastAPI endpoints (`/api/health`, `/api/connectors`, `/api/pulse/latest`, `/api/reviews`) |

- [x] **6.1** Error handling in `fetcher.py` for network timeouts and edge cases
- [x] **6.2** Fallback retry logic for Groq JSON responses
- [x] **6.3** Word count enforcement (≤250 words) in pulse generator
- [x] **6.4** Graceful fallback to local Markdown/JSON when MCP server is offline
- [x] **6.5** Run full test suite: **18 tests passing** (`pytest`)

### Exit Criteria
- 100% pass rate across all 18 unit and API integration tests

---

## Phase 7 — Documentation & Wrap-up

**Goal:** Ensure comprehensive, up-to-date documentation.

- [x] **7.1** Update `docs/architecture.md` to reflect FastAPI, Web Dashboard, SSE streaming, and Railway MCP architecture
- [x] **7.2** Update `docs/implementation-plan.md` (this file) with all phases complete
- [x] **7.3** Overhaul `README.md` with complete setup instructions, API reference, and deployment guide

---

## Phase 8 — Web Dashboard & Cloud Deployment

**Goal:** Deliver an interactive executive dashboard and cloud deployment configuration for Railway and Vercel.

### Files
| File | Purpose |
|------|---------|
| `src/api.py` | FastAPI application exposing REST and SSE streaming endpoints |
| `frontend/index.html` | Modern dark-themed dashboard inspired by Google Stitch UI |
| `Dockerfile` | Multi-stage production container for Railway deployment |
| `Procfile` | Web process declaration for Railway |
| `railway.json` | Railway build and start configuration |
| `vercel.json` | Vercel static routing configuration |

- [x] **8.1** Built FastAPI backend service:
  - `POST /api/run-agent/stream`: Streams live pipeline steps over Server-Sent Events (SSE)
  - `GET /api/pulse/latest`: Serves current `WeeklyPulse` JSON
  - `GET /api/reviews`: Returns filtered cleaned reviews
  - `GET /api/connectors`: Real-time health status for Groq, Google Docs MCP, Gmail MCP, Jira
  - `POST /api/mcp/sync-docs` & `POST /api/mcp/draft-gmail`: On-demand delivery triggers
  - `POST /api/jira/create`: Interactive Jira ticket dispatch
  - Static mount serving `frontend/` at `/`
- [x] **8.2** Built Interactive Web Dashboard (`frontend/index.html`):
  - **Review Theme Clustering Tabs**: Filter verbatim reviews across *All clusters*, *KYC & Onboarding*, *UPI & Payments*, *Statements & Tax*, *Withdrawals*, and *App Performance*
  - **Date Lookback Synchronizer**: Interactive native date picker with rolling week calculation
  - **Live Terminal Console**: Streams SSE logs from agent pipeline with step status indicators
  - **Executive Metric Cards**: CSAT rating, positive/negative review volume, and lookback indicator
  - **Jira Dispatch Modal**: Pre-fills issue description from pulse action items and submits ticket
  - **Dynamic API Connection Modal**: Allows switching between local backend (`http://localhost:8000`) and deployed Railway backend
- [x] **8.3** Configured deployment scaffolding:
  - [Dockerfile](file:///d:/Grow_Review_AI_Agent_MCP/Dockerfile) with Python 3.11-slim
  - [railway.json](file:///d:/Grow_Review_AI_Agent_MCP/railway.json) with health check path `/api/health`
  - [vercel.json](file:///d:/Grow_Review_AI_Agent_MCP/vercel.json) for static hosting
- [x] **8.4** Automated API test coverage in `tests/test_api.py`

### Exit Criteria
- User can trigger runs from browser, see live terminal logs, filter by theme, create Jira tickets, and deploy seamlessly to Railway and Vercel.

---

## Dependency Graph

```mermaid
flowchart TD
    P1[Phase 1: Bootstrap] --> P2[Phase 2: Ingestion]
    P2 --> P3A[Phase 3A: PII Scrubber]
    P3A --> P3B[Phase 3B: Theme Clustering]
    P3B --> P3C[Phase 3C: Pulse Generator]
    P3C --> P4[Phase 4: Local Dry Run]
    P4 --> P5[Phase 5: MCP Integration (SSE)]
    P5 --> P6[Phase 6: Hardening & Tests]
    P6 --> P8[Phase 8: Web Dashboard & Deployment]
    P8 --> P7[Phase 7: Documentation & Wrap-up]

    style P1 fill:#1E293B,stroke:#38BDF8,color:#fff
    style P2 fill:#1E293B,stroke:#38BDF8,color:#fff
    style P3A fill:#1E293B,stroke:#38BDF8,color:#fff
    style P3B fill:#1E293B,stroke:#38BDF8,color:#fff
    style P3C fill:#1E293B,stroke:#38BDF8,color:#fff
    style P4 fill:#1E293B,stroke:#38BDF8,color:#fff
    style P5 fill:#14532D,stroke:#22C55E,color:#fff
    style P6 fill:#14532D,stroke:#22C55E,color:#fff
    style P8 fill:#431407,stroke:#F97316,color:#fff
    style P7 fill:#14532D,stroke:#22C55E,color:#fff
```
