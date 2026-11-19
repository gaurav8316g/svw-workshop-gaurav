# Skills Validation Workshop

Harbor Bites is the running example: a food-delivery kitchen. Each challenge is an independent ADK 2 project.

## Goal
Show four agent patterns on the same kitchen policies:

- A multi-agent design review with a human decision
- Handbook search plus Google Search
- A custom MCP server plus Google's Maps MCP server
- A policy agent, an evaluation dataset, and a before-and-after prompt comparison

## Scope For This Lab
Keep each challenge self-contained and runnable on its own. Open a challenge from this repository root, or `cd` into that challenge folder.

## Status
Implemented with four challenges.

| Challenge | Folder | What it shows |
| --- | --- | --- |
| 1 | `challenge-1-multi-agent-workflow` | Propose, critique, and refine a design, then ask a person to accept it |
| 2 | `challenge-2-rag-and-search` | Handbook answers from a Discovery Engine data store, and Google Search for everything else |
| 3 | `challenge-3-mcp-integration` | A custom MCP server plus Google's Maps MCP server |
| 4 | `challenge-4-evaluation-api` | A policy agent, an evaluation dataset, and a before-and-after prompt comparison |

## Shared Setup
Each challenge that calls Vertex AI uses the same credentials. Copy that challenge's `.env.example` to `.env` and replace `your-project` with the real project ID. Leaving the placeholder makes Vertex return `PERMISSION_DENIED` for `projects/your-project`.

```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project
GOOGLE_CLOUD_LOCATION=us-central1
```

Sign in for local runs before starting the playground:

```bash
gcloud auth login
gcloud auth application-default login
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID
```

Challenge 2 sets `GOOGLE_CLOUD_LOCATION=global` so Gemini uses the same location as the data store.

## Run An Agent
From this repository root, enter the challenge and activate its virtual environment, then start the playground. Create the virtual environment once with the Setup steps in that challenge's README.

Challenge 1, then open `architecture_review`:

```bash
cd ./challenge-1-multi-agent-workflow
source .venv/bin/activate
adk web .
```

Challenge 2, then open `harbor_helpdesk`:

```bash
cd ./challenge-2-rag-and-search
source .venv/bin/activate
adk web .
```

Challenge 3, then open `harbor_dispatcher`:

```bash
cd ./challenge-3-mcp-integration
source .venv/bin/activate
adk web .
```

Challenge 4, then open `harbor_support_agent`:

```bash
cd ./challenge-4-evaluation-api
source .venv/bin/activate
adk web .
```

## Notes
- Challenge 2 does not create its data store from a script. The handbook file is uploaded in the Google Cloud console. The steps are in that challenge's README.
- Kitchen questions in Challenge 3 run without a Maps key. Maps questions need `GOOGLE_MAPS_API_KEY`.
