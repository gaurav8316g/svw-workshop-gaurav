# Challenge 5: Deploy Harbor Bites support to Gemini Enterprise

`harbor_customer_service_agent` answers staff and guest questions from the Harbor Bites policies: the 30-minute food-quality refund window, nuts, shellfish, and gluten, the 5-minute courier wait, and shift swaps before noon. The policies are in the agent instruction. The agent has no tools, data store, or Google Search.

The package is `harbor_support`. The ADK app name is `harbor-bites-support`. The model is `gemini-3.8-flash`.

## Local run

From this challenge folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example harbor_support/.env
adk web .
```

`pip install -e .` installs `google-adk` and `google-cloud-agentplatform`. The Agent Platform package is what `adk deploy` imports. Open `harbor_support` and try "The noodles were cold and the courier handed them over 12 minutes ago. Can I get a refund?"

`harbor_support/.env` is the file both the local server and the deploy command read. `adk web` starts in this folder and finds that file inside the agent package. Set the project to the real project ID. `GOOGLE_CLOUD_LOCATION=global` is the Gemini endpoint. `gemini-3.8-flash` is called on that global endpoint.

## Tests

From the workshop repository root:

```bash
PYTHONPATH=challenge-5-gemini-enterprise-deployment python -m unittest discover -s challenge-5-gemini-enterprise-deployment/tests -p "test_*.py" -v
```

`tests/eval/datasets/basic-dataset.json` is the customer-service evaluation set for this agent.

## Deployed agent

The running Agent Platform instance is:

```text
projects/764705858145/locations/us-central1/reasoningEngines/3112538472716435456
```

| Setting | Value |
| --- | --- |
| Project ID | `gemini-enterprise-demo-487120` |
| Project number | `764705858145` |
| Engine region | `us-central1` |
| Display name | Harbor Bites support |
| Model endpoint | `global`, from `harbor_support/.env` |

Playground:

https://console.cloud.google.com/vertex-ai/agents/agent-engines/locations/us-central1/agent-engines/3112538472716435456/playground?project=764705858145

The engine region has to be a regional location. `global` accepts only an empty lightweight runtime, and this deploy uploads a container spec. A deploy with `--region=global` is rejected with `FAILED_PRECONDITION` and the empty engine is deleted.

`adk deploy` reads `harbor_support/.env`. `--project` and `--region` choose the engine, so the command prints that it is ignoring `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` from that file. Those flags do not remove the variables from the runtime environment. `GOOGLE_CLOUD_LOCATION=global` is still sent to the agent, which is why model calls stay on the global endpoint while the engine stays in `us-central1`.

`harbor_support/requirements.txt` lists `google-adk`. The deploy command adds the Agent Platform dependency to the staged requirements before upload.

## Update the same instance

From this challenge folder, with the virtual environment active:

```bash
gcloud config set project gemini-enterprise-demo-487120
gcloud services enable aiplatform.googleapis.com discoveryengine.googleapis.com
adk deploy agent_engine \
  --project=gemini-enterprise-demo-487120 \
  --region=us-central1 \
  --agent_engine_id=3112538472716435456 \
  --display_name="Harbor Bites support" \
  harbor_support
```

Omit `--agent_engine_id` only when creating a new engine. After a deploy that includes `harbor_support/.env`, the instance log says it loaded that file for `harbor_support`.

## Register in Gemini Enterprise

The engine is deployed. Register it with a Gemini Enterprise app so the workspace can call it. The app resource uses `locations/global` even though the engine is in `us-central1`.

1. In the console, open **Gemini Enterprise** and create an app if you do not already have one.
2. Copy the app resource name. It looks like `projects/764705858145/locations/global/collections/default_collection/engines/APP_ID`.
3. Register the deployed agent:

```bash
agents-cli publish gemini-enterprise \
  --gemini-enterprise-app-id "projects/764705858145/locations/global/collections/default_collection/engines/APP_ID"
```

`agents-cli publish gemini-enterprise --list` prints the apps in the current project. Registration is also described at https://docs.cloud.google.com/gemini/enterprise/docs/register-and-manage-an-adk-agent.

Open the Gemini Enterprise workspace, select the app, and ask a policy question. Save a screenshot of the answer and a screenshot of the console page that shows this engine registered to the app. The deployment, registration, and workspace screenshots are in `screenshot/`.
