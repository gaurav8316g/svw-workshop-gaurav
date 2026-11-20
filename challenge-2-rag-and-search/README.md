# Challenge 2 Solution: RAG + Google Search with ADK

This folder contains an independent solution project for Challenge 2.

## Goal
Extend an ADK 2 agent with grounding tools:

- A private handbook searched through Discovery Engine
- Google Search for live information the handbook does not cover

## Scope For This Lab
Keep this project self-contained and runnable on its own.

## Status
Implemented with one runnable app, `harbor_helpdesk`. The handbook data store is created in the Cloud console. No script creates it.

## Use Case
Staff ask `harbor_helpdesk`. It does not answer on its own.

- **handbook_specialist** searches the private handbook. Topics: refunds, allergens, courier no-shows, and shift swaps.
- **web_specialist** uses Google Search for live weather, road closures, news, and anything the handbook does not cover.

Both specialists are `mode="single_turn"`, so the root calls them as tools. Each specialist has one built-in tool.

"What is our refund window?" stays with the handbook. "Is it raining in Austin right now?" goes to Google Search. If the handbook specialist says `The handbook does not cover this.`, the root asks Google Search.

## Handbook
`harbor_bites_employee_handbook.md` is the source. `harbor_bites_employee_handbook.txt` is the same text, saved as a text file so the console importer accepts it.

- Refunds: 30-minute food-quality window. No refund after the courier marks the order delivered.
- Allergens: nuts, shellfish, and gluten. Stop and ask if the allergy flag is missing.
- Couriers: wait 5 minutes, then reassign and log the no-show.
- Shifts: a swap needs manager approval and must be requested before noon.

## Files You Will Use
- `harbor_helpdesk/agent.py`
- `harbor_bites_employee_handbook.txt`
- `.env.example`

## Data Store, Created In The Cloud Console
1. Open **Cloud Storage**, then **Buckets**, and create a bucket in the workshop project.
2. Upload `harbor_bites_employee_handbook.txt`.
3. Open **AI Applications**, then **Data Stores**, and click **Create data store**.
4. Choose **Cloud Storage**, then **Unstructured documents**.
5. Choose **File**, select the uploaded text file, and set synchronization to **One-time**.
6. Set the data store location to **global**. Name it `harbor-bites-handbook`.
7. Click **Create**. On the data store page, wait on **Activity** until the status is **Import completed**, then confirm the file is listed under **Documents**.

Set `GOOGLE_CLOUD_LOCATION=global` in `.env`. Vertex AI Search only grounds the model when the Gemini call uses the same location as the data store.

Copy the data store ID from the details page into `.env`:

```text
DISCOVERY_ENGINE_DATASTORE_FULL_NAME=projects/PROJECT_ID/locations/global/collections/default_collection/dataStores/DATA_STORE_ID
```

`handbook_specialist` calls `search_employee_handbook`, a Discovery Engine function, with that data store name. The built-in Vertex AI Search tool makes `gemini-3.8-flash` emit a tool call that nothing answers, and the specialist repeats that call. The root agent calls the specialist with `AgentTool`.

## Prerequisites
- Python 3.10+
- A virtual environment
- `google-adk` and `google-cloud-discoveryengine` installed
- Application Default Credentials for Vertex AI
- A Discovery Engine data store in `global`, populated from the handbook text file
- **Discovery Engine Viewer** on the project for the account running the agent

## Environment Variables
```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project
GOOGLE_CLOUD_LOCATION=global
DISCOVERY_ENGINE_DATASTORE_FULL_NAME=projects/PROJECT_ID/locations/global/collections/default_collection/dataStores/DATA_STORE_ID
```

Replace `your-project` with the real project ID.

## Setup
From the workshop repository root:

```bash
cd ./challenge-2-rag-and-search
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Edit `.env` with the project ID and the full data store name.

## Running Tests
From the workshop repository root. The tests check the handbook text and that the root delegates to both specialists. They do not call Discovery Engine or Google Search.

```bash
cd ./challenge-2-rag-and-search
source .venv/bin/activate
PYTHONPATH=. python -m unittest discover -s tests -p "test_*.py" -v
```

## Playground
From the workshop repository root:

```bash
cd ./challenge-2-rag-and-search
source .venv/bin/activate
adk web .
```

Open `harbor_helpdesk`.

## Fill the Challenge 6 evaluation report

`adk eval` writes only a JSON file under the agent folder. It does not update `evaluation_report.md`. After a storm-response run in Challenge 6, generate the report from this workshop repository:

```bash
cd ./challenge-6-dept-of-snow
source .venv/bin/activate
adk eval ads_field_ops tests/eval/datasets/storm-response-dataset.json
python scripts/write_evaluation_report.py
```

`scripts/write_evaluation_report.py` uses the newest `ads_field_ops/.adk/eval_history/*.evalset_result.json`. It copies that file to `artifacts/storm_response_results.json` and rewrites `evaluation_report.md` with the tool-trajectory score, the response-match score, and the reply text for each case. To use one result file instead of the newest, pass its path:

```bash
python scripts/write_evaluation_report.py ads_field_ops/.adk/eval_history/RESULT.evalset_result.json
```

## Notes
- If Documents stays empty after import, give **Storage Object Viewer** on the bucket to `service-PROJECT_NUMBER@gcp-sa-discoveryengine.iam.gserviceaccount.com` and import the file again from the data store page.
