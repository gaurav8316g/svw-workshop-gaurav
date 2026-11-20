"""Fill evaluation_report.md from the newest adk eval result.

adk eval writes a JSON file under ads_field_ops/.adk/eval_history/.
This script copies that file to artifacts/storm_response_results.json and
rewrites evaluation_report.md from its scores and final replies.

From the challenge-6-dept-of-snow folder:

    python scripts/write_evaluation_report.py
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

CHALLENGE_ROOT = Path(__file__).resolve().parents[1]
HISTORY_DIR = CHALLENGE_ROOT / "ads_field_ops" / ".adk" / "eval_history"
ARTIFACT = CHALLENGE_ROOT / "artifacts" / "storm_response_results.json"
REPORT = CHALLENGE_ROOT / "evaluation_report.md"

EXPECTED = {
    "dispatch-glenn": "Unit 12 is dispatched to Glenn Highway MP 40",
    "unit-already-assigned": "Unit 7 stays on its current assignment",
    "seward-status": "Seward Highway MP 90-105 is closed for avalanche risk",
    "closure-without-officer": "Closure is refused until a duty officer is named",
    "public-alert": "Alert names the route, mileposts, condition, and 18:00 review",
    "live-anchorage-weather": "Answer uses a current weather report",
}

STATUS = {1: "Passed", 2: "Failed", 3: "Not evaluated", 4: "Informational"}


def newest_result(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.is_file():
            raise SystemExit(f"Result file not found: {path}")
        return path
    matches = sorted(HISTORY_DIR.glob("*.evalset_result.json"), key=lambda item: item.stat().st_mtime)
    if not matches:
        raise SystemExit(f"No eval result in {HISTORY_DIR}. Run adk eval first.")
    return matches[-1]


def metric(case: dict, name: str) -> dict | None:
    for item in case.get("overall_eval_metric_results") or []:
        if item.get("metric_name") == name:
            return item
    return None


def score_cell(item: dict | None) -> str:
    if not item:
        return ""
    score = item.get("score")
    threshold = item.get("threshold")
    if score is None:
        return ""
    if threshold is None:
        return f"{score:g}"
    return f"{score:g} / {threshold:g}"


def reply_text(case: dict) -> str:
    per_invocation = case.get("eval_metric_result_per_invocation") or []
    if not per_invocation:
        return ""
    response = (per_invocation[0].get("actual_invocation") or {}).get("final_response") or {}
    parts = response.get("parts") or []
    text = " ".join(part.get("text") or "" for part in parts)
    return " ".join(text.split())


def render(result_path: Path, payload: dict) -> str:
    cases = payload.get("eval_case_results") or []
    passed = sum(1 for case in cases if case.get("final_eval_status") == 1)
    failed = sum(1 for case in cases if case.get("final_eval_status") == 2)
    score_rows = []
    answer_rows = []
    for case in cases:
        eval_id = case.get("eval_id", "")
        trajectory = score_cell(metric(case, "tool_trajectory_avg_score"))
        match = score_cell(metric(case, "response_match_score"))
        automatic = STATUS.get(case.get("final_eval_status"), str(case.get("final_eval_status")))
        score_rows.append(f"| {eval_id} | {trajectory} | {match} | {automatic} |")
        answer_rows.append(
            f"| {eval_id} | {EXPECTED.get(eval_id, '')} | {reply_text(case)} |"
        )
    scores = "\n".join(score_rows)
    answers = "\n".join(answer_rows)
    return f"""# ADS storm-response evaluation

Dataset: `tests/eval/datasets/storm-response-dataset.json`

Result file: `artifacts/storm_response_results.json`

Source run: `{result_path.relative_to(CHALLENGE_ROOT)}`

This file is rewritten by `scripts/write_evaluation_report.py`. `adk eval` writes the JSON result only.

Automatic result: {passed} passed, {failed} failed.

## Automatic scores

| Case | Tool trajectory | Response match | Automatic result |
| --- | --- | --- | --- |
{scores}

## What the agent answered

| Case | Expected decision | Agent reply |
| --- | --- | --- |
{answers}
"""


def main() -> None:
    source = newest_result(sys.argv[1] if len(sys.argv) > 1 else None)
    payload = json.loads(source.read_text())
    ARTIFACT.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, ARTIFACT)
    REPORT.write_text(render(source, payload))
    print(f"Wrote {REPORT}")
    print(f"Copied result to {ARTIFACT}")


if __name__ == "__main__":
    main()
