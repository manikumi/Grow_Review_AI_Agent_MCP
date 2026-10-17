from src.mcp.docs_mcp import append_text, create_document
from src.mcp.gmail_mcp import create_draft


class MCPRouter:
    def create_doc(self, title: str, content: str) -> str:
        return create_document(title, content)

    def append_doc_text(self, doc_id: str, text: str) -> None:
        append_text(doc_id, text)

    def create_gmail_draft(self, to: str, doc_url: str, pulse_content: str = "") -> str:
        # Create an email with the pulse note content and doc link
        subject = "Groww Weekly Review Pulse"
        doc_line = f"Google Doc: {doc_url}" if doc_url.startswith("http") else ""
        if pulse_content:
            body = f"Here is the weekly pulse report:\n\n{pulse_content}"
            if doc_line:
                body += f"\n\n{doc_line}"
        else:
            body = f"Here is the weekly pulse report. {doc_line}".strip()
        return create_draft(to, subject, body)


mcp_router = MCPRouter()
