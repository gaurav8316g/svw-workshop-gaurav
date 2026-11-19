# Challenge 1: Multi-agent workflow

An ADK 2 graph reviews a software design, then asks a person whether the result is adequate. The default scenario is "design a food-delivery app". The graph does not draw diagrams, write ADRs, or generate code.

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

## Run

From the workshop repository root:

```bash
adk web challenge-1-multi-agent-workflow
```

Open `architecture_review`. Ask it to design a food-delivery app. When it asks if the design is adequate, reply `yes` to accept it, or describe a change to send it back.

Screenshots from a completed review are in `screenshots/`.

## Tests

From the workshop repository root:

```bash
PYTHONPATH=challenge-1-multi-agent-workflow python -m unittest discover -s challenge-1-multi-agent-workflow/tests -p "test_*.py" -v
```

The tests check routing only. They do not call Gemini.
