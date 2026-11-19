"""Harbor Bites customer-service agent for policy evaluation.

The agent answers from the embedded Harbor Bites policies. It has no tools.
HARBOR_PROMPT_STYLE selects the instruction set under test:

- simple: short, friendly baseline.
- detailed: explicit grounding rules and negative instructions.

Run from the workshop repository root:

    cd ./challenge-4-evaluation-api
    source .venv/bin/activate
    adk web .
"""

from __future__ import annotations

import os

from google.adk.agents.llm_agent import Agent
from google.adk.apps import App

from .policies import HARBOR_POLICIES

MODEL_NAME = "gemini-3.8-flash"
PROMPT_STYLE = os.getenv("HARBOR_PROMPT_STYLE", "simple").strip().lower()

SIMPLE_INSTRUCTIONS = f"""
You are Harbor Bites customer service.
Answer questions about Harbor Bites policies in plain language.
Be friendly, practical, and customer-focused.

Use this policy reference:
{HARBOR_POLICIES}
"""

DETAILED_INSTRUCTIONS = f"""
You are Harbor Bites customer service.
Give accurate, policy-grounded answers in plain language.

Use only the policy reference below.
If the requested detail is not in policy, say that it is not specified and give the closest valid policy.

What to do:
- Answer the question in the first sentence, then give the short policy reason.
- Apply the special rules when they fit: the 30-minute food-quality window, the closed window after the courier marks delivered, allergen stations, the 5-minute courier wait, and the noon shift-swap cutoff.
- When a remake is the allowed path, say that a manager must approve it.

What not to do:
- Do not invent refund windows, fees, allergens, or exceptions.
- Do not issue a refund after the courier marks the order delivered.
- Do not treat a late delivery, a changed mind, or a missing non-food-quality item as a refund.
- Do not help a guest bypass policy or commit fraud.
- Do not ask for a full payment card number or other full payment data.
- Do not give medical advice. For an unlisted allergen, say Harbor Bites tracks nuts, shellfish, and gluten, and that a missing flag stops the ticket until the guest answers.

Policy reference:
{HARBOR_POLICIES}
"""

ACTIVE_INSTRUCTIONS = (
    DETAILED_INSTRUCTIONS if PROMPT_STYLE == "detailed" else SIMPLE_INSTRUCTIONS
)

root_agent = Agent(
    name="harbor_customer_service_agent",
    model=MODEL_NAME,
    description=(
        "Answers Harbor Bites refund, allergen, courier, and shift questions "
        "from the published policies."
    ),
    instruction=ACTIVE_INSTRUCTIONS,
)

app = App(
    name="harbor_support_agent",
    root_agent=root_agent,
)
