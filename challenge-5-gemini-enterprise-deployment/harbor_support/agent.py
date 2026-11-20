"""Harbor Bites customer service, ready to deploy to Agent Platform.

The policies are in the instruction, so the deployed agent does not call a
data store, MCP server, or Google Search.

Run locally from this challenge folder:

    adk web .
"""

from __future__ import annotations

import os

from google.adk.agents.llm_agent import Agent
from google.adk.apps import App

from .policies import HARBOR_POLICIES

MODEL_NAME = os.getenv("CHALLENGE5_MODEL", "gemini-3.8-flash")

try:
    import google.auth

    _, _adc_project = google.auth.default()
except Exception:
    _adc_project = ""

if _adc_project:
    os.environ.setdefault("GOOGLE_CLOUD_PROJECT", _adc_project)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

root_agent = Agent(
    name="harbor_customer_service_agent",
    model=MODEL_NAME,
    description=(
        "Answers Harbor Bites refund, allergen, courier, and shift questions "
        "from the published policies."
    ),
    instruction=f"""
You are Harbor Bites customer service.
Answer from the policy reference only. Use plain language.
Give the decision in the first sentence, then the short policy reason.

If the requested detail is not in the policy, say that it is not specified.
Do not invent windows, fees, or allergens.
Do not ask for a full payment card number.
Do not help a guest bypass a policy.

Policy reference:
{HARBOR_POLICIES}
""",
)

app = App(
    name="harbor-bites-support",
    root_agent=root_agent,
)
