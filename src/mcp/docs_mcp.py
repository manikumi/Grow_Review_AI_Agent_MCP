from src.mcp.client import MCPToolError, call_mcp_tool
from src.utils.config import GOOGLE_DOC_ID, GOOGLE_DOC_URL, GOOGLE_DOCS_MCP_URL


def create_document(title: str, content: str) -> str:
    """Append the pulse to the configured Google Doc via MCP and return the Doc URL.

    The MCP server only supports appending to an existing doc
    (`append_to_google_doc`), so GOOGLE_DOC_ID or GOOGLE_DOC_URL must be set.
    Raises MCPToolError with a clear reason if the doc could not be updated.
    """
    if not GOOGLE_DOCS_MCP_URL:
        raise MCPToolError("GOOGLE_DOCS_MCP_URL is not set on this service.")
    if not GOOGLE_DOC_ID:
        raise MCPToolError(
            "GOOGLE_DOC_ID / GOOGLE_DOC_URL is not set (or invalid) on this service, "
            "so there is no Google Doc to append to."
        )

    formatted_text = f"\n\n=== {title} ===\n\n{content}\n"
    call_mcp_tool(
        GOOGLE_DOCS_MCP_URL,
        "append_to_google_doc",
        {"documentId": GOOGLE_DOC_ID, "text": formatted_text},
    )
    return GOOGLE_DOC_URL or f"https://docs.google.com/document/d/{GOOGLE_DOC_ID}/edit"


def append_text(doc_id: str, text: str) -> None:
    if not GOOGLE_DOCS_MCP_URL:
        raise MCPToolError("GOOGLE_DOCS_MCP_URL is not set on this service.")
    call_mcp_tool(GOOGLE_DOCS_MCP_URL, "append_to_google_doc", {"documentId": doc_id, "text": text})
