"""Alaska Department of Snow field-operations router.

The root agent does not answer. It transfers each request to one specialist:

- dispatch_specialist calls the ADS MCP server for the plow fleet.
- road_status_specialist calls the ADS MCP server for highway status,
  Google Maps MCP for routes, and conditions_specialist for live search.
- public_comms_specialist searches the ADS storm procedures in Discovery
  Engine, then records an alert through the ADS MCP server.

Run from this challenge folder:

    adk web .
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

from google.adk.agents.llm_agent import Agent
from google.adk.apps import App
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.discovery_engine_search_tool import (
    DiscoveryEngineSearchTool,
)
from google.adk.tools.google_search_tool import google_search
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import (
    StreamableHTTPConnectionParams,
)
from mcp import StdioServerParameters

MODEL_NAME = os.getenv("CHALLENGE6_MODEL", "gemini-3.8-flash")
MAPS_MCP_URL = "https://mapstools.googleapis.com/mcp"
ADS_SERVER = Path(__file__).resolve().parents[1] / "ads_backend_server.py"

logger = logging.getLogger("ads_field_ops")

try:
    import google.auth

    _, _adc_project = google.auth.default()
except Exception:
    _adc_project = ""

if _adc_project:
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", _adc_project)
os.environ["GOOGLE_CLOUD_LOCATION"] = "global"
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"

_PROJECT = os.environ.get("GOOGLE_CLOUD_PROJECT", "your-project")
DISCOVERY_ENGINE_DATASTORE_FULL_NAME = os.getenv(
    "DISCOVERY_ENGINE_DATASTORE_FULL_NAME",
    (
        f"projects/{_PROJECT}/locations/global/collections/"
        "default_collection/dataStores/ads-storm-procedures"
    ),
)

if not os.getenv("DISCOVERY_ENGINE_DATASTORE_FULL_NAME"):
    logger.warning(
        "DISCOVERY_ENGINE_DATASTORE_FULL_NAME is not set. "
        "public_comms_specialist is using %s.",
        DISCOVERY_ENGINE_DATASTORE_FULL_NAME,
    )


def _ads_toolset(tool_filter: list[str]) -> McpToolset:
    return McpToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command=sys.executable,
                args=[str(ADS_SERVER)],
            ),
            timeout=20,
        ),
        tool_filter=tool_filter,
    )


def _maps_toolset() -> McpToolset:
    api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
    if not api_key:
        logger.warning(
            "GOOGLE_MAPS_API_KEY is not set. Maps routing is unavailable "
            "until that key is configured."
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


conditions_specialist = Agent(
    name="conditions_specialist",
    model=MODEL_NAME,
    description=(
        "Looks up live weather and traffic with Google Search. Use this for "
        "conditions that are not already in the ADS road file."
    ),
    instruction="""You look up live winter conditions with Google Search.

Search once, then answer from the results. Include the place and the
condition. If search returns nothing current, say that no live report was
found. Do not dispatch plows or close roads.
""",
    tools=[google_search],
)

dispatch_specialist = Agent(
    name="dispatch_specialist",
    model=MODEL_NAME,
    description="Assigns available Alaska Department of Snow plow units.",
    instruction="""You dispatch ADS plow units.

Call list_plow_units before you assign anyone. Anchorage covers the Glenn
Highway, and Fairbanks covers the Parks Highway. Dispatch only a unit whose
status is available. Repeat the tool result. Do not close a highway and do
not write a public alert.
""",
    tools=[
        _ads_toolset(["list_plow_units", "dispatch_plow"]),
    ],
)

road_status_specialist = Agent(
    name="road_status_specialist",
    model=MODEL_NAME,
    description=(
        "Reads and updates ADS highway status, looks up routes on Maps, "
        "and checks live conditions."
    ),
    instruction="""You handle ADS highway status.

Call get_road_status for a stored highway. Call set_road_closure only when
the user names the duty officer. A closure without that name is refused.
Use the Maps tools for places and driving routes. For live weather or a
traffic report that is not in the ADS file, call conditions_specialist.
Repeat the tool result. Do not dispatch a plow.
""",
    tools=[
        _ads_toolset(["get_road_status", "set_road_closure"]),
        _maps_toolset(),
        AgentTool(conditions_specialist),
    ],
)

public_comms_specialist = Agent(
    name="public_comms_specialist",
    model=MODEL_NAME,
    description=(
        "Drafts ADS public alerts from the storm procedures and records them."
    ),
    instruction="""You write ADS public alerts.

Call search_ads_policy once before you draft. Use only what the passages
allow. The alert must name the route, the mileposts, the condition, and a
review time. Do not include a phone number, a radio code, or a resident's
name. After the draft matches the passages, call record_public_alert.
If the passages do not cover the request, say the procedures do not cover it.
""",
    tools=[
        DiscoveryEngineSearchTool(
            data_store_id=DISCOVERY_ENGINE_DATASTORE_FULL_NAME,
            max_results=5,
            name="search_ads_policy",
            description=(
                "Search Alaska Department of Snow storm procedures for "
                "dispatch, closure, and public-alert rules."
            ),
        ),
        _ads_toolset(["record_public_alert"]),
    ],
)

root_agent = Agent(
    name="ads_field_ops",
    model=MODEL_NAME,
    description=(
        "Routes Alaska Department of Snow storm requests to dispatch, "
        "road status, or public communications."
    ),
    instruction="""You are the ADS field-operations router. Do not answer
the question yourself. Transfer it to exactly one specialist:

- dispatch_specialist: plow units and dispatch.
- road_status_specialist: highway status, closures, Maps routes, and live
  weather or traffic.
- public_comms_specialist: public alert wording and recording an alert.

If a request needs two specialists, transfer to the one that matches the
first action the operator asked for.
""",
    sub_agents=[
        dispatch_specialist,
        road_status_specialist,
        public_comms_specialist,
    ],
)

app = App(
    name="ads-field-ops",
    root_agent=root_agent,
)
