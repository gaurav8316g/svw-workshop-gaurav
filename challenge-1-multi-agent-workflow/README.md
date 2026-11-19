# Challenge 1 Solution: Multi-Agent Workflow with ADK

This folder contains an independent solution project for Challenge 1.

## Goal
Build an ADK 2 graph that reviews a software design, then asks a person whether the result is adequate.

- A root graph, not a single answering agent
- Shared draft state across critique and refine
- A human decision that can accept the design or send it back

## Scope For This Lab
Keep this project self-contained and runnable on its own.

The default scenario is "design a food-delivery app". The graph does not draw diagrams, write ADRs, or generate code.

## Status
Implemented with one runnable app, `architecture_review`.

## Graph

```
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
```

1. **capture_scenario** stores the scenario. If the user does not give one, it uses "design a food-delivery app".
2. **BasicArchagent** writes the first design into `architecture_draft`.
3. **critique_agent** scores scalability, maintainability, and performance.
4. **refine_agent** rewrites the design, or stops with exactly `The design is good.`
5. **after_refine** sends the draft back to critique, or stops. The loop stops when the design is good or after 3 critique-and-refine rounds.
6. **ask_human** shows the draft and asks if it is adequate.
7. **route_human** accepts `yes`, `y`, `yeah`, `yep`, `adequate`, `ok`, `okay`, `good`, `lgtm`, `approve`, or `approved`. Any other reply sends the draft back to critique while rounds remain.
8. **finalize** publishes the surviving draft, the rounds used, and the human verdict.

## Files You Will Use
- `architecture_review/agent.py`

## Prerequisites
- Python 3.10+
- A virtual environment
- `google-adk` installed
- Application Default Credentials for Vertex AI
- `GOOGLE_CLOUD_PROJECT` set to a real project, with the Vertex AI API enabled

## Setup
From the workshop repository root:

```bash
cd ./challenge-1-multi-agent-workflow
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Running Tests
From the workshop repository root. The tests check routing only. They do not call Gemini.

```bash
cd ./challenge-1-multi-agent-workflow
source .venv/bin/activate
PYTHONPATH=. python -m unittest discover -s tests -p "test_*.py" -v
```

## Playground
From the workshop repository root:

```bash
cd ./challenge-1-multi-agent-workflow
source .venv/bin/activate
adk web .
```

Open `architecture_review`. Ask it to design a food-delivery app. When it asks if the design is adequate, reply `yes` to accept it, or describe a change to send it back.

Screenshots from a completed review are in `screenshots/`.

## Notes
- Reply `yes` (or another accepted word above) to finish the review.
- Any other reply at the human step is revision feedback, while critique rounds remain.
