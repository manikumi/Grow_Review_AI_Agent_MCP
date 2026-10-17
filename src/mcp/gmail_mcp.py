from src.mcp.client import MCPToolError, call_mcp_tool
from src.utils.config import GMAIL_MCP_URL


def create_draft(to: str, subject: str, body: str) -> str:
    """Creates a Gmail draft or sends an email via MCP."""
    if not GMAIL_MCP_URL:
        print(f"Would have created a draft to {to} with subject '{subject}'")
        return "local_stub_draft_id"

    errors = []
    for tool_name in ["create_draft", "send_gmail"]:
        try:
            text = call_mcp_tool(GMAIL_MCP_URL, tool_name, {"to": to, "subject": subject, "body": body})
            return text or "sent"
        except MCPToolError as e:
            errors.append(str(e))

    print(f"Error calling MCP email tools on {GMAIL_MCP_URL}: {' | '.join(errors)}")
    return ""
