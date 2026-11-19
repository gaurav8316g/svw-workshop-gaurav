# Challenge 2: Handbook search and Google Search

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

## Data store, created in the Cloud console

The data store was created in the Google Cloud console. No script created it.

1. Open **Cloud Storage**, then **Buckets**, and create a bucket in the workshop project.
2. Upload `harbor_bites_employee_handbook.txt`.
3. Open **AI Applications**, then **Data Stores**, and click **Create data store**.
4. Choose **Cloud Storage**, then **Unstructured documents**.
5. Choose **File**, select the uploaded text file, and set synchronization to **One-time**.
6. Set the data store location to **global**. Name it `harbor-bites-handbook`.
7. Click **Create**. On the data store page, wait on **Activity** until the status is **Import completed**, then confirm the file is listed under **Documents**.

Set `GOOGLE_CLOUD_LOCATION=global` in `.env`. Vertex AI Search only grounds the model when the Gemini call uses the same location as the data store.

Copy the data store ID from the details page into `.env`:

```bash
cp challenge-2-rag-and-search/.env.example challenge-2-rag-and-search/.env
```

```text
DISCOVERY_ENGINE_DATASTORE_FULL_NAME=projects/PROJECT_ID/locations/global/collections/default_collection/dataStores/DATA_STORE_ID
```

`handbook_specialist` calls `search_employee_handbook`, a Discovery Engine function, with that data store name. The built-in Vertex AI Search tool makes `gemini-3.8-flash` emit a tool call that nothing answers, and the specialist repeats that call. The root agent calls the specialist with `AgentTool`. The account running the agent needs **Discovery Engine Viewer** on the project. Install `google-cloud-discoveryengine` before starting the playground. If Documents stays empty after import, give **Storage Object Viewer** on the bucket to `service-PROJECT_NUMBER@gcp-sa-discoveryengine.iam.gserviceaccount.com` and import the file again from the data store page.

## Run

From the workshop repository root:

```bash
adk web challenge-2-rag-and-search
```

Open `harbor_helpdesk`.

## Tests

From the workshop repository root:

```bash
PYTHONPATH=challenge-2-rag-and-search python -m unittest discover -s challenge-2-rag-and-search/tests -p "test_*.py" -v
```

The tests check the handbook text and that the root delegates to both specialists. They do not call Discovery Engine or Google Search.
