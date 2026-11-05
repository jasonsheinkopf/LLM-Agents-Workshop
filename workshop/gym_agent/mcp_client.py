"""Connect to the MCP server like any MCP client would: list its tools, then call some.

    uv run python -m gym_agent.mcp_client
"""

from __future__ import annotations

import asyncio
import json
import sys

from mcp import Client, StdioServerParameters

from .config import REPO_ROOT


async def demo() -> None:
    server = StdioServerParameters(
        command=sys.executable, args=["-m", "gym_agent.mcp_server"], cwd=str(REPO_ROOT / _impl_dir())
    )
    async with Client(server) as client:
        tools = await client.list_tools()
        print("Tools the server offers:")
        for t in tools.tools:
            print(f"  - {t.name}: {(t.description or '').splitlines()[0]}")

        print("\ncheck_schedule(day='Saturday', age=8):")
        r = await client.call_tool("check_schedule", {"day": "Saturday", "age": 8})
        print(_text(r)[:900])

        print("\nbook_class(...) without a code -> needs confirmation:")
        r = await client.call_tool("book_class", {"class_id": "youth-sat-1000",
                                                  "participant_name": "Sam", "participant_age": 8})
        print(_text(r))


def _text(result) -> str:
    """Tool results arrive as content blocks; ours hold one JSON text block."""
    text = "".join(getattr(block, "text", "") for block in result.content)
    try:
        return json.dumps(json.loads(text), indent=2)
    except json.JSONDecodeError:
        return text


def _impl_dir() -> str:
    # run the server from the same folder this client lives in (workshop/ or solution/)
    from pathlib import Path

    return Path(__file__).resolve().parents[1].name


if __name__ == "__main__":
    asyncio.run(demo())
