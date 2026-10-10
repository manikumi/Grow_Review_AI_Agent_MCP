from src.mcp.docs_mcp import append_text, create_document
from src.mcp.gmail_mcp import create_draft


class MCPRouter:
    def create_doc(self, title: str, content: str) -> str:
        return create_document(title, content)

    def append_doc_text(self, doc_id: str, text: str) -> None:
        append_text(doc_id, text)

    def create_gmail_draft(self, to: str, doc_url: str) -> str:
        # Based on phase 5, we create a draft with a link to the doc.
        subject = "Weekly Pulse Report"
        body = f"Here is the weekly pulse report: {doc_url}"
        return create_draft(to, subject, body)

mcp_router = MCPRouter()
