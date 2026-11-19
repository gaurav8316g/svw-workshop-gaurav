"""Harbor Bites staff helpdesk.

The root agent routes each question to one specialist tool:

- handbook_specialist calls search_employee_handbook, which queries the
  Discovery Engine data store and returns the passages.
- web_specialist uses Google Search for live weather, road closures, news,
  and anything the handbook does not cover.

The data store is in global, so this module calls Gemini in global too.
Vertex AI Search grounding does not run when the model location is a region
such as us-central1.

Run from the workshop repository root:

    adk web challenge-2-rag-and-search
"""

from __future__ import annotations

import logging
import os

from google.adk.agents.llm_agent import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.discovery_engine_search_tool import (
    DiscoveryEngineSearchTool,
)
from google.adk.tools.google_search_tool import google_search

MODEL_NAME = "gemini-3.8-flash"

logger = logging.getLogger("harbor_helpdesk")

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
    os.getenv(
        "DISCOVERY_ENGINE_DATASTORE",
        (
            f"projects/{_PROJECT}/locations/global/collections/"
            "default_collection/dataStores/harbor-bites-handbook"
        ),
    ),
)

HANDBOOK_TOPICS = (
    "refunds and the 30-minute food-quality window",
    "allergens (nuts, shellfish, gluten) and a missing allergy flag",
    "courier waits, reassignment, and no-shows",
    "shift swaps and the noon approval cutoff",
)

if not os.getenv("DISCOVERY_ENGINE_DATASTORE_FULL_NAME") and not os.getenv(
    "DISCOVERY_ENGINE_DATASTORE"
):
    logger.warning(
        "DISCOVERY_ENGINE_DATASTORE_FULL_NAME is not set. "
        "handbook_specialist is using %s.",
        DISCOVERY_ENGINE_DATASTORE_FULL_NAME,
    )


handbook_specialist = Agent(
    name="handbook_specialist",
    model=MODEL_NAME,
    description=(
        "Answers Harbor Bites staff questions from the employee handbook: "
        + "; ".join(HANDBOOK_TOPICS)
        + ". Use this for internal kitchen policy. Do not use it for live "
        "weather, road closures, or news."
    ),
    instruction="""
You answer Harbor Bites staff questions from the private handbook datastore.

Call search_employee_handbook once, then answer from its passages.
Do not call it again for the same question.
Do not add rules that are not in those passages.

If the datastore does not contain the answer, reply with exactly:
The handbook does not cover this.

Covered topics:
- refunds and the 30-minute food-quality window
- allergens (nuts, shellfish, gluten) and a missing allergy flag
- courier waits, reassignment, and no-shows
- shift swaps and the noon approval cutoff
""",
    tools=[
        DiscoveryEngineSearchTool(
            data_store_id=DISCOVERY_ENGINE_DATASTORE_FULL_NAME,
            max_results=5,
            name="search_employee_handbook",
            description=(
                "Search the Harbor Bites employee handbook for refund, "
                "allergen, courier, and shift-swap rules."
            ),
        )
    ],
)

web_specialist = Agent(
    name="web_specialist",
    model=MODEL_NAME,
    description=(
        "Answers with Google Search when the Harbor Bites handbook does not "
        "apply: live weather, road closures, news, and other public facts. "
        "Do not use this for refund, allergen, courier, or shift policy."
    ),
    instruction="""
You answer questions that the Harbor Bites handbook does not cover.

Use Google Search. Typical questions are live weather, road closures, and
news. Cite what the search found. Do not invent Harbor Bites policy.
""",
    tools=[google_search],
)

root_agent = Agent(
    name="harbor_helpdesk",
    model=MODEL_NAME,
    description=(
        "Harbor Bites staff helpdesk. Routes handbook questions to "
        "handbook_specialist and everything else to web_specialist."
    ),
    instruction="""
You are the Harbor Bites staff helpdesk. Do not answer the question yourself.
Call exactly one specialist, then give the user that specialist's answer.

Call handbook_specialist for internal policy:
- refunds and the 30-minute food-quality window
- allergens (nuts, shellfish, gluten) and a missing allergy flag
- courier waits, reassignment, and no-shows
- shift swaps and the noon approval cutoff

Call web_specialist for live weather, road closures, news, and any question
the handbook does not cover.

"What is our refund window?" goes to handbook_specialist.
"Is it raining in Austin right now?" goes to web_specialist.

If handbook_specialist replies "The handbook does not cover this.", call
web_specialist with the same question and return that answer.
If unsure, try handbook_specialist first, then web_specialist.
""",
    tools=[
        AgentTool(agent=handbook_specialist),
        AgentTool(agent=web_specialist),
    ],
)
