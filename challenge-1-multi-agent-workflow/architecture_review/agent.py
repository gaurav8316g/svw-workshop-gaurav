"""Iterative software-architecture review as an ADK 2 graph workflow.

Given a scenario, BasicArchagent writes a first-pass design. critique_agent
and refine_agent then repeat for at most three rounds. refine_agent either
rewrites the design or stops with "The design is good." A human reviews the
result every time the loop is ready to stop, and can send it back for another
round while iterations remain.

Graph (the back-edge is the ADK 2 form of LoopAgent(max_iterations=3)):

    START
      -> capture_scenario
      -> BasicArchagent
      -> critique_agent
      -> refine_agent
      -> after_refine
           |-- continue --> critique_agent
           +-- done ------> ask_human
                              -> route_human
                                   |-- revise --> critique_agent
                                   +-- done ---> finalize

This is a design-review demo. It does not draw diagrams, write ADRs, or
generate code.

Run from the repo root:

    adk web challenge-1-multi-agent-workflow
"""

from __future__ import annotations

import json
from typing import Any

from google.adk import Agent
from google.adk import Event
from google.adk import Workflow
from google.adk.agents.context import Context
from google.adk.apps import App
from google.adk.apps import ResumabilityConfig
from google.adk.events import RequestInput
from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Literal

MAX_ITERATIONS = 3
GOOD_DESIGN = "The design is good."
DEFAULT_SCENARIO = "design a food-delivery app"
MODEL_NAME = "gemini-3.8-flash"

_ADEQUATE_REPLIES = frozenset(
    {
        "yes",
        "y",
        "yeah",
        "yep",
        "adequate",
        "ok",
        "okay",
        "good",
        "lgtm",
        "approve",
        "approved",
    }
)


class Critique(BaseModel):
    """Structured review of one architecture draft."""

    verdict: Literal["good", "revise"] = Field(
        description="good only when another revision would not materially help."
    )
    scalability: str = Field(
        description="What holds up, and what will not, under load."
    )
    maintainability: str = Field(
        description="What will be hard to change, own, or test."
    )
    performance: str = Field(
        description="Latency, throughput, and cost hot spots."
    )
    required_changes: str = Field(
        description="Concrete changes for the next draft. Empty when verdict is good."
    )


def as_text(value: Any) -> str:
    """Normalize user content, model content, or a human reply to text."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    parts = getattr(value, "parts", None)
    if parts:
        joined = "".join(getattr(part, "text", "") or "" for part in parts).strip()
        if joined:
            return joined
    if isinstance(value, dict):
        for key in ("text", "message", "user_response", "response"):
            item = value.get(key)
            if isinstance(item, str) and item.strip():
                return item.strip()
    return str(value).strip()


def is_good_design(text: str) -> bool:
    """True when refine_agent stopped with the canonical sentence."""
    if not text.strip():
        return False
    first_line = text.strip().splitlines()[0].strip().strip("\"'")
    return first_line.rstrip(".").strip() == GOOD_DESIGN.rstrip(".")


def is_adequate(reply: str) -> bool:
    """True when the human accepts the design without further notes."""
    return reply.strip().lower().rstrip(".!") in _ADEQUATE_REPLIES


def _format_critique(critique: Any) -> str:
    if isinstance(critique, BaseModel):
        return json.dumps(critique.model_dump(), indent=2)
    if isinstance(critique, dict):
        return json.dumps(critique, indent=2)
    return as_text(critique)


def capture_scenario(node_input: Any) -> Event:
    """Store the scenario that every later agent reads from session state."""
    scenario = as_text(node_input) or DEFAULT_SCENARIO
    return Event(
        output=scenario,
        state={
            "scenario": scenario,
            "architecture_draft": "",
            "critique": "",
            "human_feedback": "",
            "human_verdict": "",
            "stop_reason": "",
            "review_round": 0,
        },
    )


basic_arch_agent = Agent(
    name="BasicArchagent",
    model=MODEL_NAME,
    description="Drafts a first-pass system architecture from a scenario.",
    instruction="""You are a software architect writing a first-pass system design.

Scenario:
{scenario}

Write a concise architecture in prose. Cover:
- major components and their responsibilities
- request and data flow
- storage, APIs, and how clients talk to the system
- the main scalability, maintainability, and performance tradeoffs

Do not draw diagrams, write an ADR, or generate code.
""",
    output_key="architecture_draft",
)

critique_agent = Agent(
    name="critique_agent",
    model=MODEL_NAME,
    description="Evaluates a draft for scalability, maintainability, and performance.",
    instruction="""You are an architecture reviewer.

Scenario:
{scenario}

Current design:
{architecture_draft}

Notes from the human reviewer (empty on the first pass):
{human_feedback?}

This is critique {review_round} of an at-most-3-round revise loop.
The first critique of the initial draft is round 0.

Judge scalability, maintainability, and performance.
Set verdict to good only when another revision would not materially improve those three.
Otherwise set verdict to revise and name the concrete changes the next draft must make.
""",
    output_schema=Critique,
    output_key="critique",
)

refine_agent = Agent(
    name="refine_agent",
    model=MODEL_NAME,
    description="Improves the architecture, or stops when the design is good.",
    instruction="""You are a software architect revising a system design.

Scenario:
{scenario}

Current design:
{architecture_draft}

Critique:
{critique}

Notes from the human reviewer (may be empty):
{human_feedback?}

If the critique verdict is good, respond with exactly this sentence and nothing else:
The design is good.

Otherwise rewrite the full architecture so it addresses the critique and any human notes.
Keep the same prose-only format. Do not add diagrams, an ADR, or code.
Do not include the sentence "The design is good." in a rewritten design.
""",
    output_key="refine_output",
)


def after_refine(ctx: Context, node_input: Any) -> Event:
    """Count the round and either loop back to critique or ask the human."""
    text = as_text(node_input)
    previous = as_text(ctx.state.get("architecture_draft"))
    review_round = int(ctx.state.get("review_round") or 0) + 1
    state: dict[str, Any] = {"review_round": review_round, "refine_output": text}

    if is_good_design(text):
        state["stop_reason"] = "design_is_good"
        state["architecture_draft"] = previous
        return Event(route="done", output=previous, state=state)

    draft = text or previous
    state["architecture_draft"] = draft
    if review_round >= MAX_ITERATIONS:
        state["stop_reason"] = "max_iterations"
        return Event(route="done", output=draft, state=state)

    state["stop_reason"] = ""
    return Event(route="continue", output=draft, state=state)


def ask_human(
    architecture_draft: str = "",
    critique: Any = "",
    review_round: int = 0,
    stop_reason: str = "",
):
    """Pause for a human review on every exit from the revise loop."""
    if stop_reason == "design_is_good":
        status = GOOD_DESIGN
    elif stop_reason == "max_iterations":
        status = f"Stopped after {MAX_ITERATIONS} critique and refine rounds."
    else:
        status = "Ready for review."
    message = (
        f"{status}\n"
        f"Human review after round {review_round} of {MAX_ITERATIONS}.\n\n"
        f"Architecture:\n{architecture_draft}\n\n"
        f"Latest critique:\n{_format_critique(critique)}\n\n"
        "Is this design adequate? Reply yes, or describe what must change."
    )
    yield RequestInput(
        interrupt_id=f"human_review_{review_round}",
        message=message,
        payload={
            "architecture_draft": architecture_draft,
            "review_round": review_round,
            "stop_reason": stop_reason,
        },
    )


def route_human(ctx: Context, node_input: Any) -> Event:
    """Accept the design, or send it back while rounds remain."""
    reply = as_text(node_input)
    review_round = int(ctx.state.get("review_round") or 0)
    if is_adequate(reply):
        return Event(
            route="done",
            state={"human_verdict": "adequate", "human_feedback": reply},
        )
    if review_round >= MAX_ITERATIONS:
        return Event(
            route="done",
            state={
                "human_verdict": "changes_requested_after_cap",
                "human_feedback": reply,
            },
        )
    return Event(
        route="revise",
        state={
            "human_verdict": "revise",
            "human_feedback": reply,
            "stop_reason": "",
        },
    )


def finalize(
    architecture_draft: str = "",
    review_round: int = 0,
    stop_reason: str = "",
    human_verdict: str = "",
    human_feedback: str = "",
) -> Event:
    """Publish the design that survived the review loop."""
    lines: list[str] = []
    if stop_reason == "design_is_good" and human_verdict == "adequate":
        lines.append(GOOD_DESIGN)
    elif stop_reason == "max_iterations":
        lines.append(f"Reached the {MAX_ITERATIONS}-round limit.")
    lines.extend(
        [
            architecture_draft,
            "",
            f"Rounds used: {review_round} of {MAX_ITERATIONS}.",
            f"Human verdict: {human_verdict or 'not recorded'}.",
        ]
    )
    if human_verdict == "changes_requested_after_cap" and human_feedback:
        lines.append(
            "Further changes were requested after the round limit: "
            f"{human_feedback}"
        )
    return Event(message="\n".join(lines), output=architecture_draft)


root_agent = Workflow(
    name="architecture_review",
    description=(
        "Drafts a system design, then critiques and refines it for "
        f"scalability, maintainability, and performance (max {MAX_ITERATIONS} rounds) "
        "and asks a human to accept it."
    ),
    edges=[
        (
            "START",
            capture_scenario,
            basic_arch_agent,
            critique_agent,
            refine_agent,
            after_refine,
        ),
        (after_refine, {"continue": critique_agent, "done": ask_human}),
        (ask_human, route_human),
        (route_human, {"revise": critique_agent, "done": finalize}),
    ],
)

app = App(
    name="architecture-review",
    root_agent=root_agent,
    resumability_config=ResumabilityConfig(is_resumable=True),
)
