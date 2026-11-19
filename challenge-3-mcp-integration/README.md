# Challenge 3 Solution: Custom MCP and Google Maps MCP

This folder contains an independent solution project for Challenge 3.

## Goal
Connect an ADK 2 agent to MCP servers so it can:

- Answer kitchen questions through a custom local MCP server
- Answer place questions through Google's hosted Maps MCP server
- Keep the root agent as a router that does not answer on its own

## Scope For This Lab
Keep this project self-contained and runnable on its own.

## Status
Implemented with:

- Root agent `harbor_dispatcher`
- Custom MCP server in `harbor_ops_server.py`
- Google Maps Grounding Lite MCP server at `https://mapstools.googleapis.com/mcp`

## Architecture
- **harbor_ops** calls the local MCP server over stdio. The playground starts that process.
- **google_maps_specialist** calls Google's Maps MCP server and sends `GOOGLE_MAPS_API_KEY` as the `X-Goog-Api-Key` header.

`harbor_dispatcher` routes each question to one specialist and does not answer it.

Custom tools:

- `check_refund`: food-quality refunds inside 30 minutes of handoff. Marking the order delivered closes that window.
- `lookup_allergen_rule`: nuts, shellfish, and gluten.
- `report_courier_noshow`: hold the bag for 5 minutes, then reassign and log the no-show.
- `request_shift_swap`: a request before noon waits for a manager. A later request is rejected.

## Files You Will Use
- `harbor_dispatcher/agent.py`
- `harbor_ops_server.py`
- `.env.example`

## Prerequisites
- Python 3.10+
- A virtual environment
- `google-adk[mcp]` installed
- Application Default Credentials for Vertex AI
- `GOOGLE_CLOUD_PROJECT` set to a real project, with the Vertex AI API enabled
- For Maps questions: Maps Grounding Lite (Maps Experience agent tools) enabled on that project, billing enabled, and an API key restricted to that API

## Environment Variables
```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_MAPS_API_KEY=
```

Replace `your-project` with the real project ID. Kitchen questions work without `GOOGLE_MAPS_API_KEY`. Maps calls do not.

Sign in before the first playground run:

```bash
gcloud auth application-default login
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
```

## Setup
From the workshop repository root:

```bash
cd ./challenge-3-mcp-integration
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Edit `.env` with the project ID and, for Maps, the API key.

## Running Tests
From the workshop repository root. The tests call the custom server over stdio. They do not call Maps.

```bash
cd ./challenge-3-mcp-integration
source .venv/bin/activate
PYTHONPATH=. python -m unittest discover -s tests -p "test_*.py" -v
```

## Playground
From the workshop repository root:

```bash
cd ./challenge-3-mcp-integration
source .venv/bin/activate
adk web .
```

Open `harbor_dispatcher`.

Kitchen prompts, answered by the custom server:

- A customer got a cold burger 12 minutes after handoff and the courier has not marked it delivered. Can we refund?
- What is the kitchen rule for a shellfish allergy?
- Courier has not shown for order HB-1042 and we have waited 8 minutes.
- Can Priya swap her shift on 2026-11-20 if she asked before noon?

Maps prompt, answered by the Google MCP server:

- Find coffee shops near the Ferry Building in San Francisco.

## Notes
- Restart `adk web` after changing `.env`. A running process keeps the project ID it loaded at startup.
- Create the Maps key under APIs & Services → Credentials for the same project, after enabling Maps Grounding Lite.
