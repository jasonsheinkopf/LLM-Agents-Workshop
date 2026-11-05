"""Lab 6: the same tools over MCP. Connects to the server in-process, no subprocess needed."""

import asyncio


def test_mcp_server_lists_and_runs_tools():
    from mcp import Client

    from gym_agent.mcp_server import mcp

    async def go():
        async with Client(mcp) as client:
            names = {t.name for t in (await client.list_tools()).tools}
            assert {"check_schedule", "book_class", "search_handbook"} <= names
            r = await client.call_tool("check_schedule", {"day": "Saturday", "age": 8})
            assert not r.is_error
            assert "youth-sat-1000" in str(r.structured_content or r.content)
            r = await client.call_tool("book_class", {"class_id": "youth-sat-1000",
                                                      "participant_name": "Sam", "participant_age": 8})
            assert "needs_confirmation" in str(r.structured_content or r.content)

    asyncio.run(go())
