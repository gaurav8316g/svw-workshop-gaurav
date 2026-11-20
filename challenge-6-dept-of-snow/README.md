# Challenge 6: Alaska Department of Snow field operations

`ads_field_ops` is the operator interface for storm response. It does not answer on its own. It routes each request to one specialist:

| Specialist | What it handles | Grounding |
| --- | --- | --- |
| `dispatch_specialist` | Plow units and assignments | ADS backend MCP server |
| `road_status_specialist` | Highway status, closures, and driving routes | ADS backend MCP server, Google Maps MCP, and Google Search for live conditions |
| `public_comms_specialist` | Public alert wording and recording | Discovery Engine search over the ADS storm procedures, then the ADS backend MCP server |

The sample fleet is unit 12 available in Anchorage, unit 7 on the Glenn Highway from Fairbanks, and unit 3 in maintenance in Juneau. Glenn Highway MP 40-55 starts open, Seward Highway MP 90-105 starts closed for avalanche risk, and Parks Highway MP 200-220 starts open with ice. A closure needs a named duty officer. A public alert cannot include a phone number.

## 1. Create the environment

From this challenge folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
cp .env ads_field_ops/.env
```

Keep the same values in both files. `adk web` reads `ads_field_ops/.env` first. `adk deploy` reads only `ads_field_ops/.env`, so a file that exists only in this challenge folder is not sent to Agent Platform.

Set `GOOGLE_CLOUD_PROJECT` to the lab project. Leave `GOOGLE_CLOUD_LOCATION=global`. Discovery Engine and `gemini-3.8-flash` are called on that global endpoint. The Agent Platform engine itself is still deployed to `us-central1` in step 7.

`pip install -e .` installs `google-adk`, the MCP client, Discovery Engine, and the Agent Platform client used by `adk deploy`.

Sign in before the first model call:

```bash
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
gcloud services enable aiplatform.googleapis.com discoveryengine.googleapis.com
```

The account that runs `adk web` needs Vertex AI User (`roles/aiplatform.user`) and, after the data store exists, Discovery Engine Viewer (`roles/discoveryengine.viewer`).

## 2. Load the storm procedures into Discovery Engine

The policy file to import is `ads_policies/ads_storm_procedures.txt`. Create the data store in the Google Cloud console. This project does not create it from a script.

1. Open **AI Applications** and create a data store in location `global`.
2. Choose **Cloud Storage**, **Unstructured documents**, and one file.
3. Upload `ads_policies/ads_storm_procedures.txt` to a bucket, select that object, and run a one-time import.
4. Wait until the import status is completed.
5. Open the data store and copy its resource name. The console URL uses `data-stores`. The resource name uses `dataStores`:

```text
projects/PROJECT_ID/locations/global/collections/default_collection/dataStores/DATA_STORE_ID
```

6. Paste that name into both `.env` files as `DISCOVERY_ENGINE_DATASTORE_FULL_NAME`.

`public_comms_specialist` calls `search_ads_policy` on that store. Until the name is set, the agent uses `dataStores/ads-storm-procedures` in the project from `.env`.

## 3. Add a Maps key

Road-status questions that ask for a place or a driving route call the Google Maps MCP server at `https://mapstools.googleapis.com/mcp`.

1. Enable **Maps Grounding Lite**. If the console has renamed it, enable **Maps Experience agent tools** (`mapstools.googleapis.com`).
2. In **APIs & Services**, **Credentials**, create an API key and restrict it to that API.
3. Put the key in both `.env` files as `GOOGLE_MAPS_API_KEY`.

Dispatch, stored highway status, closures, and public alerts run without this key.

## 4. Run the agent locally

From this challenge folder, with the virtual environment active:

```bash
adk web .
```

Open `ads_field_ops`. Try these prompts:

1. "Send an available Anchorage plow to Glenn Highway MP 40 for light snow."
2. "What is the current ADS status of the Seward Highway?"
3. "Close Parks Highway MP 200-220 for ice. No duty officer is available."
4. "Write and record a public alert for the Seward Highway closure. Review at 18:00."
5. "What is the live weather in Anchorage right now?"

The fleet and road file reset when the MCP server process stops.

## 5. Run the unit tests

From the workshop repository root:

```bash
PYTHONPATH=challenge-6-dept-of-snow python -m unittest discover -s challenge-6-dept-of-snow/tests -p "test_*.py" -v
```

## 6. Run the storm-response evaluation

The dataset is `tests/eval/datasets/storm-response-dataset.json`. `adk eval` writes a JSON result under `ads_field_ops/.adk/eval_history/` and does not edit `evaluation_report.md`.

From this challenge folder:

```bash
adk eval ads_field_ops tests/eval/datasets/storm-response-dataset.json
python scripts/write_evaluation_report.py
```

The script copies the newest result to `artifacts/storm_response_results.json` and rewrites `evaluation_report.md` with the scores and the agent's replies. Pass a result path when you want a specific run instead of the newest file.

## 7. Deploy to Agent Platform

`global` cannot host this container. Deploy the engine to `us-central1`. Model calls stay on `global` because `.env` sets `GOOGLE_CLOUD_LOCATION=global`, and `adk deploy` still forwards that variable when `--region` is set.

From this challenge folder:

```bash
adk deploy agent_engine \
  --project=YOUR_PROJECT_ID \
  --region=us-central1 \
  --display_name="ADS field operations" \
  ads_field_ops
```

Save the printed resource name, `projects/PROJECT_NUMBER/locations/us-central1/reasoningEngines/ENGINE_ID`. To update that same engine later, add `--agent_engine_id=ENGINE_ID`.

`ads_field_ops/requirements.txt` is the dependency list uploaded with the agent. The deploy command adds the Agent Platform package if it is missing. It reads `ads_field_ops/.env` for the project, the global model location, the data store name, and the Maps key.

## 8. Register in Gemini Enterprise

1. In the console, open **Gemini Enterprise** and create an app if you do not already have one.
2. Copy the app resource name. It uses `locations/global`:

```text
projects/PROJECT_NUMBER/locations/global/collections/default_collection/engines/APP_ID
```

3. Register the deployed engine:

```bash
agents-cli publish gemini-enterprise \
  --gemini-enterprise-app-id "projects/PROJECT_NUMBER/locations/global/collections/default_collection/engines/APP_ID"
```

`agents-cli publish gemini-enterprise --list` prints the apps in the current project. The registration steps are also at https://docs.cloud.google.com/gemini/enterprise/docs/register-and-manage-an-adk-agent.

## 9. Save the submission evidence

Ask the registered agent the five prompts from step 4 inside the Gemini Enterprise workspace. Save a screenshot of an answer and a screenshot of the console page that shows the engine registered to the app. Put both images in `screenshot/`.

Include `artifacts/storm_response_results.json` and the filled table in `evaluation_report.md` when you submit the repository.
