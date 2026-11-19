# Challenge 3: Custom MCP and Google Maps MCP

`harbor_dispatcher` routes each question to one specialist and does not answer it.

- **harbor_ops** calls the local MCP server in `harbor_ops_server.py` over stdio. The playground starts that process.
- **google_maps_specialist** calls Google's Maps Grounding Lite MCP server at `https://mapstools.googleapis.com/mcp`.

Custom tools:

- `check_refund`: food-quality refunds inside 30 minutes. Marking the order delivered does not close that window.
- `lookup_allergen_rule`: nuts, shellfish, and gluten.
- `report_courier_noshow`: hold the bag for 5 minutes, then reassign and log the no-show.
- `request_shift_swap`: a request before noon waits for a manager. A later request is rejected.

## Run

Install `google-adk[mcp]`. From the workshop repository root:

```bash
cp challenge-3-mcp-integration/.env.example challenge-3-mcp-integration/.env
adk web challenge-3-mcp-integration
```

Set `GOOGLE_CLOUD_PROJECT` in `.env`. Maps calls also need `GOOGLE_MAPS_API_KEY`, with Maps Grounding Lite enabled on the project. Kitchen questions work without that key.

Open `harbor_dispatcher`.

Kitchen prompts, answered by the custom server:

- A customer got a cold burger 12 minutes after handoff and the courier has not marked it delivered. Can we refund?
- What is the kitchen rule for a shellfish allergy?
- Courier has not shown for order HB-1042 and we have waited 8 minutes.
- Can Priya swap her shift on 2026-11-20 if she asked before noon?

Maps prompt, answered by the Google MCP server:

- Find coffee shops near the Ferry Building in San Francisco.

## Tests

From the workshop repository root:

```bash
PYTHONPATH=challenge-3-mcp-integration python -m unittest discover -s challenge-3-mcp-integration/tests -p "test_*.py" -v
```

The tests call the custom server over stdio. They do not call Maps.
