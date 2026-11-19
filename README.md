# Skills Validation Workshop

Harbor Bites is the running example: a food-delivery kitchen. Each challenge is an ADK 2 project that can be opened from this repository root.

Shared credentials go in each challenge `.env`, copied from that challenge's `.env.example`:

```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project
GOOGLE_CLOUD_LOCATION=us-central1
```

| Challenge | Folder | What it shows |
| --- | --- | --- |
| 1 | `challenge-1-multi-agent-workflow` | Propose, critique, and refine a design, then ask a person to accept it |
| 2 | `challenge-2-rag-and-search` | Handbook answers from a Discovery Engine data store created in the Cloud console, and Google Search for everything else |
| 3 | `challenge-3-mcp-integration` | A custom MCP server plus Google's Maps MCP server |
| 4 | `challenge-4-evaluation-api` | A policy agent, an evaluation dataset, and a before-and-after prompt comparison |

Challenge 2 does not create its data store from a script. The handbook file was uploaded in the Google Cloud console. The steps are in that challenge's README.
