import asyncio
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

from src.utils.config import GMAIL_MCP_URL


async def _call_mcp_tool(server_url: str, tool_name: str, arguments: dict) -> Any:
    """Helper to call an MCP tool over SSE."""
    async with sse_client(server_url) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result

def create_draft(to: str, subject: str, body: str) -> str:
    """Creates a Gmail draft and returns its draft ID via MCP."""
    if not GMAIL_MCP_URL:
        print(f"Would have created a draft to {to} with subject '{subject}'")
        return "local_stub_draft_id"
        
    try:
        result = asyncio.run(_call_mcp_tool(
            GMAIL_MCP_URL, 
            "create_draft", 
            {"to": to, "subject": subject, "body": body}
        ))
        if result and result.content:
            return result.content[0].text
        return str(result)
    except Exception as e:
        print(f"Error calling MCP create_draft: {e}")
        return ""
