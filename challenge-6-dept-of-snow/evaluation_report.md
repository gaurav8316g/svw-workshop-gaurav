# ADS storm-response evaluation

Dataset: `tests/eval/datasets/storm-response-dataset.json`

Result file: `artifacts/storm_response_results.json`

Source run: `ads_field_ops/.adk/eval_history/ads_field_ops_storm-response_1795189190.413891.evalset_result.json`

This file is rewritten by `scripts/write_evaluation_report.py`. `adk eval` writes the JSON result only.

Automatic result: 0 passed, 6 failed.

## Automatic scores

| Case | Tool trajectory | Response match | Automatic result |
| --- | --- | --- | --- |
| closure-without-officer | 0 / 1 | 0 / 0.8 | Failed |
| seward-status | 0 / 1 | 0 / 0.8 | Failed |
| live-anchorage-weather | 0 / 1 | 0 / 0.8 | Failed |
| dispatch-glenn | 0 / 1 | 0 / 0.8 | Failed |
| public-alert | 0 / 1 | 0 / 0.8 | Failed |
| unit-already-assigned | 0 / 1 | 0 / 0.8 | Failed |

## What the agent answered

| Case | Expected decision | Agent reply |
| --- | --- | --- |
| closure-without-officer | Closure is refused until a duty officer is named | A highway closure cannot be set without the name of an approving duty officer. The request to close Parks Highway MP 200–220 is therefore refused until an authorizing duty officer is provided. |
| seward-status | Seward Highway MP 90-105 is closed for avalanche risk | The current ADS status of the Seward Highway is: Seward Highway MP 90-105 is closed (avalanche risk). |
| live-anchorage-weather | Answer uses a current weather report | In **Anchorage, Alaska**, current conditions are **partly cloudy / fair** with a temperature of **32°F (0°C)**, a wind chill of 24°F, and south winds at around 9 mph. |
| dispatch-glenn | Unit 12 is dispatched to Glenn Highway MP 40 | Dispatched unit 12 from Anchorage to Glenn Highway MP 40. Reason: light snow. |
| public-alert | Alert names the route, mileposts, condition, and 18:00 review | The public alert for the Seward Highway closure has been drafted and recorded: - **Route:** Seward Highway - **Mileposts:** MP 90–105 - **Condition:** Closed due to avalanche risk - **Review Time:** 18:00 **Alert Message:** *"Seward Highway is closed between Mileposts 90 and 105 due to avalanche risk. Next review is scheduled for 18:00."* |
| unit-already-assigned | Unit 7 stays on its current assignment | Unit 7 cannot be dispatched because its status is currently "on route" (driver Marcus Reid, assigned to Glenn Highway MP 20). Only units with an "available" status can be dispatched. **Plow unit status:** Unit 12 (Anchorage): available, driver Lena Cho, assignment none. Unit 7 (Fairbanks): on route, driver Marcus Reid, assignment Glenn Highway MP 20. Unit 3 (Juneau): maintenance, driver Ava Bennett, assignment none. |
