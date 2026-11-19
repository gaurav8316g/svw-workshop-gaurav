# Challenge 1: Multi-Agent Workflow (Architecture Review)

An ADK 2 graph-based multi-agent workflow for iterative software architecture design reviews.

## Architecture

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

### Agent Roles:
1. **capture_scenario**: Initializes session state with the scenario (defaults to "design a food-delivery app") and tracking variables.
2. **BasicArchagent**: Writes a first-pass architectural design in prose and stores it in session state (`architecture_draft`).
3. **critique_agent**: Evaluates the draft for scalability, maintainability, and performance using structured output (`Critique`).
4. **refine_agent**: Rewrites the design to address critique and human feedback, or responds with exactly `"The design is good."`.
5. **after_refine**: Evaluates the refiner's output:
   - If `"The design is good."`, stops the loop with `stop_reason="design_is_good"`.
   - If iterations reach the cap (`MAX_ITERATIONS = 3`), stops the loop with `stop_reason="max_iterations"`.
   - Otherwise, routes back to `critique_agent`.
6. **ask_human**: Prompts the human reviewer with the current draft, critique, and round status (`RequestInput`).
7. **route_human**:
   - If the human responds `"yes"`, accepts the design and routes to `finalize`.
   - If changes are requested and rounds remain (< 3), routes back to `critique_agent`.
   - If rounds are exhausted (>= 3), records the feedback and routes to `finalize`.
8. **finalize**: Publishes the surviving architecture draft, rounds used, and human verdict.

## Running Tests

Run unit tests covering all graph routing paths:

```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```

## Running the Web UI

From the workshop repository root:

```bash
adk web challenge-1-multi-agent-workflow
```
