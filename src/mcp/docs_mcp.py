import asyncio
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

from src.utils.config import GOOGLE_DOCS_MCP_URL


async def _call_mcp_tool(server_url: str, tool_name: str, arguments: dict) -> Any:
    """Helper to call an MCP tool over SSE."""
    async with sse_client(server_url) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result

def create_document(title: str, content: str) -> str:
    """Creates a Google Doc and returns its URL via MCP."""
    if not GOOGLE_DOCS_MCP_URL:
        # Fallback to local stub if URL not configured
        import os
        from datetime import date
        today = date.today().isoformat()
        filepath = os.path.join("output", f"pulse_{today}.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"file://{os.path.abspath(filepath)}"
        
    try:
        result = asyncio.run(_call_mcp_tool(
            GOOGLE_DOCS_MCP_URL, 
            "create_document", 
            {"title": title, "content": content}
        ))
        
        # Depending on the MCP server implementation, it returns either the URL or a struct
        if result and result.content:
            return result.content[0].text
        return str(result)
    except Exception as e:
        print(f"Error calling MCP create_document: {e}")
        return ""

def append_text(doc_id: str, text: str) -> None:
    if not GOOGLE_DOCS_MCP_URL:
        return
    try:
        asyncio.run(_call_mcp_tool(
            GOOGLE_DOCS_MCP_URL,
            "append_text",
            {"doc_id": doc_id, "text": text}
        ))
    except Exception as e:
        print(f"Error calling MCP append_text: {e}")
