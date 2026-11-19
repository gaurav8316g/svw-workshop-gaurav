"""Harbor Bites dispatcher: custom MCP plus Google Maps MCP.

The root agent routes each question to one specialist:

- harbor_ops uses the local Harbor Bites MCP server (refunds, allergens,
  courier no-shows, shift swaps).
- google_maps_specialist uses Google's Maps Grounding Lite MCP server
  (places, addresses, and directions).

Run from the workshop repository root:

    adk web challenge-3-mcp
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from google.adk.agents.llm_agent import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)
from mcp import StdioServerParameters

MODEL_NAME = "gemini-3.8-flash"
MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp"
HARBOR_SERVER = Path(__file__).resolve().parents[1] / "harbor_ops_server.py"

logger = logging.getLogger("harbor_dispatcher")


def _harbor_ops_toolset() -> McpToolset:
    """Connect to the custom Harbor Bites MCP server over stdio."""
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[str(HARBOR_SERVER)],
            ),
            timeout=20,
        ),
        tool_filter=[
            "check_refund",
            "lookup_allergen_rule",
            "report_courier_noshow",
            "request_shift_swap",
        ],
    )


def _maps_toolset() -> McpToolset:
    """Connect to the Google-provided Maps Grounding Lite MCP server."""
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        logger.warning(
            "GOOGLE_MAPS_API_KEY is not set. google_maps_specialist cannot "
            "call the Maps MCP server until that key is configured."
        )
    return McpToolset(
        connection_params=StreamableHTTPConnectionParams(
            url=MAPS_MCP_URL,
            headers={
                "X-Goog-Api-Key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            timeout=30,
            sse_read_timeout=300,
        ),
    )


harbor_ops = Agent(
    name="harbor_ops",
    model=MODEL_NAME,
    description=(
        "Answers Harbor Bites kitchen questions about refunds, allergens, "
        "courier no-shows, and shift swaps by calling the custom Harbor "
        "Bites MCP tools."
    ),
    instruction="""You handle Harbor Bites kitchen operations.

Use the Harbor Bites MCP tools for every answer:
- check_refund for refund eligibility
- lookup_allergen_rule for nuts, shellfish, and gluten
- report_courier_noshow when a courier is late or missing
- request_shift_swap for shift-change requests

Call the matching tool before you answer. Repeat the tool result in plain
language. If the question is about places, addresses, or directions, say it
belongs to the maps specialist.
""",
    tools=[_harbor_ops_toolset()],
)

google_maps_specialist = Agent(
    name="google_maps_specialist",
    model=MODEL_NAME,
    description=(
        "Looks up places, addresses, and directions with the Google Maps "
        "MCP server."
    ),
    instruction="""You are the Google Maps specialist for Harbor Bites.

Use the Google Maps MCP tools for geocoding, place lookup, nearby search,
and routing. Base the answer on the tool result. If the question is about
refunds, allergens, couriers, or shift swaps, say it belongs to harbor_ops.
""",
    tools=[_maps_toolset()],
)

root_agent = Agent(
    name="harbor_dispatcher",
    model=MODEL_NAME,
    description=(
        "Routes Harbor Bites questions to kitchen operations or Google Maps."
    ),
    instruction="""You are the Harbor Bites dispatcher. Do not answer the
question yourself. Transfer it to exactly one specialist:

- harbor_ops: refunds, allergens, courier no-shows, and shift swaps.
- google_maps_specialist: places, addresses, nearby search, and directions.

If a question needs both, transfer to the specialist for the part the user
asked about first, then say which other specialist covers the rest.
""",
    sub_agents=[harbor_ops, google_maps_specialist],
)
