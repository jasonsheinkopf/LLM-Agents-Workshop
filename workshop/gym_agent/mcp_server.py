"""The same tools, served over MCP (Lab 6).

MCP (Model Context Protocol) is a standard plug between agents and tools. Write the server once,
and any MCP client can use it: Claude Desktop, Claude Code, Cursor, the MCP Inspector, or your own
agent. This server exposes Ridgeline's schedule, handbook search and booking tools.

    uv run python -m gym_agent.mcp_server                       # stdio (what desktop apps launch)
    uv run python -m gym_agent.mcp_server --http                # http://127.0.0.1:8000/mcp
    uv run python -m gym_agent.mcp_client                       # list + call the tools from Python

Least privilege still applies: the caller identity is fixed when the server starts
(`RIDGELINE_CALLER_ID`, default `dana`). A client can't pass someone else's id.
"""

from __future__ import annotations

import os
import sys

from mcp.server.mcpserver import MCPServer

from .config import has
from .guardrails import Day
from .gym import BookingStore
from .tools import CallContext, run_tool

ALLOWED = {"check_schedule", "book_class", "search_handbook"}


def _handbook():
    if not has("PINECONE_API_KEY", "OPENAI_API_KEY"):
        return None
    from .llm import get_client
    from .memory import Handbook, PineconeStore

    try:
        store = PineconeStore.try_connect()
    except Exception as e:  # a bad key shouldn't stop the other tools from working
        print(f"ridgeline-gym: handbook search disabled ({type(e).__name__}: {e})", file=sys.stderr)
        return None
    return Handbook(get_client(), store) if store else None


CTX = CallContext(caller_id=os.getenv("RIDGELINE_CALLER_ID", "dana"), bookings=BookingStore(),
                  handbook=_handbook())

mcp = MCPServer(
    "ridgeline-gym",
    instructions="Tools for Ridgeline Climbing Gym (fictional): class schedule, handbook search and bookings.",
)


def _call(name: str, **args) -> dict:
    import json

    return run_tool(CTX, name, json.dumps({k: v for k, v in args.items() if v is not None}), ALLOWED)


@mcp.tool()
def check_schedule(day: Day | None = None, age: int | None = None) -> dict:
    """List Ridgeline's weekly classes (day, time, ages, price, seats left). Filter by day and/or age."""
    return _call("check_schedule", day=day, age=age)


# TODO(lab6): expose two more tools the same way as check_schedule above:
#   search_handbook(query: str) -> dict
#   book_class(class_id: str, participant_name: str, participant_age: int,
#              confirmation_code: str | None = None) -> dict
#     (in book_class, do CTX.turn += 1 first: each MCP request counts as a new step)
# The docstring becomes the tool description that MCP clients show to their model, so write it well.


def main() -> None:
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http")
    else:
        mcp.run()


if __name__ == "__main__":
    main()
