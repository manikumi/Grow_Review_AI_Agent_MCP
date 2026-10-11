import asyncio
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

from src.utils.config import GOOGLE_DOCS_MCP_URL, GOOGLE_DOC_ID, GOOGLE_DOC_URL


async def _call_mcp_tool(server_url: str, tool_name: str, arguments: dict) -> Any:
    """Helper to call an MCP tool over SSE."""
    async with sse_client(server_url) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result

def create_document(title: str, content: str) -> str:
    """Creates or appends content to a Google Doc and returns its URL via MCP."""
    if GOOGLE_DOCS_MCP_URL and GOOGLE_DOC_ID:
        try:
            formatted_text = f"\n\n=== {title} ===\n\n{content}\n"
            result = asyncio.run(_call_mcp_tool(
                GOOGLE_DOCS_MCP_URL, 
                "append_to_google_doc", 
                {"documentId": GOOGLE_DOC_ID, "text": formatted_text}
            ))
            if result and not getattr(result, "is_error", False):
                return GOOGLE_DOC_URL or f"https://docs.google.com/document/d/{GOOGLE_DOC_ID}/edit"
        except Exception as e:
            print(f"Error appending to Google Doc via MCP: {e}")

    if GOOGLE_DOCS_MCP_URL:
        try:
            result = asyncio.run(_call_mcp_tool(
                GOOGLE_DOCS_MCP_URL, 
                "create_document", 
                {"title": title, "content": content}
            ))
            if result and not getattr(result, "is_error", False) and result.content:
                return result.content[0].text
        except Exception as e:
            print(f"Error calling MCP create_document: {e}")

    # Fallback to saving local markdown if MCP server tool does not support doc creation
    import os
    from datetime import date
    os.makedirs("output", exist_ok=True)
    today = date.today().isoformat()
    filepath = os.path.join("output", f"pulse_{today}.md")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    return f"file://{os.path.abspath(filepath)}"


def append_text(doc_id: str, text: str) -> None:
    if not GOOGLE_DOCS_MCP_URL:
        return
    for tool_name, args in [
        ("append_to_google_doc", {"documentId": doc_id, "text": text}),
        ("append_text", {"doc_id": doc_id, "text": text})
    ]:
        try:
            asyncio.run(_call_mcp_tool(GOOGLE_DOCS_MCP_URL, tool_name, args))
            return
        except Exception:
            continue

