"""Shared helper for calling tools on the remote MCP server over SSE."""

import asyncio
import concurrent.futures
from typing import Any

from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

MCP_TIMEOUT_SECONDS = 60


class MCPToolError(RuntimeError):
    pass


async def _call_tool_async(server_url: str, tool_name: str, arguments: dict) -> Any:
    async with sse_client(server_url) as streams:
        async with ClientSession(streams[0], streams[1]) as session:
            await session.initialize()
            return await session.call_tool(tool_name, arguments)


def _result_text(result: Any) -> str:
    parts = [getattr(c, "text", "") for c in (getattr(result, "content", None) or [])]
    return "\n".join(p for p in parts if p).strip()


def _is_error(result: Any) -> bool:
    # mcp 1.x uses `isError`, mcp 2.x uses `is_error`
    return bool(getattr(result, "is_error", False) or getattr(result, "isError", False))


def _unwrap(exc: BaseException) -> BaseException:
    # anyio task groups wrap the real error in an ExceptionGroup
    while isinstance(exc, BaseExceptionGroup) and exc.exceptions:
        exc = exc.exceptions[0]
    return exc


def call_mcp_tool(server_url: str, tool_name: str, arguments: dict) -> str:
    """Call an MCP tool from sync code and return its text output.

    Works both from plain scripts and from inside a running event loop
    (e.g. a FastAPI async endpoint). Raises MCPToolError on any failure.
    """
    def run() -> Any:
        return asyncio.run(asyncio.wait_for(
            _call_tool_async(server_url, tool_name, arguments), MCP_TIMEOUT_SECONDS
        ))

    try:
        asyncio.get_running_loop()
        in_loop = True
    except RuntimeError:
        in_loop = False

    try:
        if in_loop:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
                result = pool.submit(run).result()
        else:
            result = run()
    except BaseException as e:  # noqa: BLE001 - ExceptionGroup is a BaseException
        if isinstance(e, (KeyboardInterrupt, SystemExit)):
            raise
        inner = _unwrap(e)
        raise MCPToolError(f"MCP tool '{tool_name}' failed: {type(inner).__name__}: {inner}") from inner

    text = _result_text(result)
    if _is_error(result):
        raise MCPToolError(f"MCP tool '{tool_name}' returned an error: {text or 'unknown error'}")
    return text
