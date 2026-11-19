"""Harbor Bites staff helpdesk.

The root agent routes each question to one single-turn specialist:

- handbook_specialist searches the Discovery Engine data store created in
  the Google Cloud console from the employee handbook.
- web_specialist uses Google Search for live weather, road closures, news,
  and anything the handbook does not cover.

Run from the workshop repository root:

    adk web challenge-2-rag-and-search
"""

from __future__ import annotations

import logging
import os

from google.adk.agents.llm_agent import Agent
from google.adk.tools.google_search_tool import google_search
from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool

MODEL_NAME = "gemini-3.8-flash"
DISCOVERY_ENGINE_DATASTORE = os.getenv("DISCOVERY_ENGINE_DATASTORE", "")

logger = logging.getLogger("harbor_helpdesk")

HANDBOOK_TOPICS = (
    "refunds and the 30-minute food-quality window",
    "allergens (nuts, shellfish, gluten) and a missing allergy flag",
    "courier waits, reassignment, and no-shows",
    "shift swaps and the noon approval cutoff",
)


def _handbook_tool() -> VertexAiSearchTool:
    """Search the Discovery Engine data store created in the Cloud console."""
    datastore = DISCOVERY_ENGINE_DATASTORE
    if not datastore:
        logger.warning(
            "DISCOVERY_ENGINE_DATASTORE is not set. handbook_specialist "
            "cannot search the handbook until that data store resource "
            "name is configured."
        )
        datastore = (
            "projects/unset/locations/global/collections/"
            "default_collection/dataStores/harbor-bites-handbook"
        )
    return VertexAiSearchTool(
        data_store_id=datastore,
        max_results=5,
    )


handbook_specialist = Agent(
    name="handbook_specialist",
    model=MODEL_NAME,
    mode="single_turn",
    description=(
        "Answers Harbor Bites staff questions from the employee handbook: "
        + "; ".join(HANDBOOK_TOPICS)
        + ". Use this for internal kitchen policy. Do not use it for live "
        "weather, road closures, or news."
    ),
    instruction="""
You answer Harbor Bites staff questions from the employee handbook only.

Use the handbook data store before you answer. Use the retrieved text as
the policy. Do not add rules that are not in the retrieved text.

If the retrieval result does not cover the question, reply with exactly:
The handbook does not cover this.

Covered topics:
- refunds and the 30-minute food-quality window
- allergens (nuts, shellfish, gluten) and a missing allergy flag
- courier waits, reassignment, and no-shows
- shift swaps and the noon approval cutoff
""",
    tools=[_handbook_tool()],
)

web_specialist = Agent(
    name="web_specialist",
    model=MODEL_NAME,
    mode="single_turn",
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
""",
    sub_agents=[handbook_specialist, web_specialist],
)
