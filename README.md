# Grow Review AI Agent (MCP)

This is a pipeline-style AI agent that ingests public Groww app reviews, clusters them into themes using an LLM, produces a structured weekly pulse, and delivers it via Google Docs and Gmail—entirely through MCP (Model Context Protocol) servers.

## Prerequisites

- **Python 3.11+**
- **Groq API Key** (for `openai/gpt-oss-120b` via the Groq SDK)
- **MCP Servers Configuration** (Google Docs & Gmail MCP Servers)

## Setup Steps

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd grow-review-ai-agent-mcp
   ```

2. **Configure Environment Variables:**
   Copy the example environment file and fill in your details:
   ```bash
   cp .env.example .env
   ```
   *Make sure to add your `GROQ_API_KEY` and Google MCP credentials in `.env`.*

3. **Install Dependencies:**
   Set up a Python virtual environment and install the required packages:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   
   pip install -r requirements.txt
   ```

## How to Run

To run the full agent pipeline (Fetch -> Scrub -> Cluster -> Generate Pulse -> Deliver via MCP):

```bash
python -m src.agent
```

If the MCP servers are configured correctly, a new Google Doc will be created with the weekly pulse, and a Gmail draft will be prepared. If MCP delivery fails, it gracefully falls back to saving a local Markdown file in the `output/` directory.

## How to Run Tests

To run the test suite and view coverage:

```bash
pytest --cov=src.processing --cov-report=term-missing tests/
```

We aim for >80% code coverage on all processing modules.

## MCP Server Integration

This agent interacts with external APIs entirely through MCP servers defined in `config/mcp_servers.json`.
- [Google Docs MCP Server Documentation](https://github.com/modelcontextprotocol/server-google-docs) (or relevant documentation)
- [Gmail MCP Server Documentation](https://github.com/modelcontextprotocol/server-gmail)

Ensure you have initialized the respective MCP servers and provided valid `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` environment variables.
