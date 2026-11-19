"""Run the Harbor Bites eval for both prompt styles and write the result files.

Writes:

- artifacts/results_simple.evalset_result.json
- artifacts/results_detailed.evalset_result.json
- artifacts/evaluation_comparison.json
- reports/evaluation_comparison.md (score table filled from those files)

From the challenge directory:

    python scripts/generate_eval_results.py

Requires google-adk[eval] and Vertex or Gemini credentials in the environment
or in challenge-4-evaluation-api/.env.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

CHALLENGE_ROOT = Path(__file__).resolve().parents[1]
WORKSHOP_ROOT = CHALLENGE_ROOT.parent
AGENT_DIR = CHALLENGE_ROOT / "harbor_support_agent"
EVALSET = CHALLENGE_ROOT / "tests" / "eval" / "datasets" / "harbor_policies.evalset.json"
CONFIG = CHALLENGE_ROOT / "tests" / "eval" / "test_config.json"
ARTIFACTS = CHALLENGE_ROOT / "artifacts"
REPORT = CHALLENGE_ROOT / "reports" / "evaluation_comparison.md"
STYLES = ("simple", "detailed")


def _adk_command() -> list[str]:
    adk = shutil.which("adk")
    if adk:
        return [adk]
    return [sys.executable, "-m", "google.adk.cli"]


def _latest_result(storage_dir: Path) -> Path:
    history = storage_dir / "harbor_support_agent" / ".adk" / "eval_history"
    results = sorted(history.glob("*.evalset_result.json"), key=lambda path: path.stat().st_mtime)
    if not results:
        raise FileNotFoundError(f"No eval result was written under {history}")
    return results[-1]


def _run_style(style: str) -> Path:
    storage_dir = ARTIFACTS / style
    storage_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["HARBOR_PROMPT_STYLE"] = style
    command = [
        *_adk_command(),
        "eval",
        str(AGENT_DIR),
        str(EVALSET),
        f"--config_file_path={CONFIG}",
        f"--eval_storage_uri={storage_dir.resolve().as_uri()}",
        "--print_detailed_results",
    ]
    log_path = ARTIFACTS / f"{style}.log"
    print(f"Running {style} eval. Log: {log_path}")
    with log_path.open("w", encoding="utf-8") as log:
        completed = subprocess.run(
            command,
            cwd=WORKSHOP_ROOT,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            check=False,
        )
    try:
        source = _latest_result(storage_dir)
    except FileNotFoundError:
        tail = log_path.read_text(encoding="utf-8")[-2000:]
        raise SystemExit(
            f"{style} eval produced no result file (exit {completed.returncode}).\n{tail}"
        ) from None
    destination = ARTIFACTS / f"results_{style}.evalset_result.json"
    shutil.copyfile(source, destination)
    print(f"Wrote {destination}")
    return destination


def _metric_scores(result_path: Path) -> dict[str, list[float]]:
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    scores: dict[str, list[float]] = {}
    cases = payload.get("eval_case_results") or payload.get("evalCaseResults") or []
    for case in cases:
        metrics = case.get("overall_eval_metric_results") or case.get("overallEvalMetricResults") or []
        for metric in metrics:
            name = metric.get("metric_name") or metric.get("metricName")
            score = metric.get("score")
            if name and isinstance(score, (int, float)):
                scores.setdefault(name, []).append(float(score))
    return scores


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / len(values)


def _write_comparison(simple_path: Path, detailed_path: Path) -> None:
    simple_scores = _metric_scores(simple_path)
    detailed_scores = _metric_scores(detailed_path)
    names = sorted(set(simple_scores) | set(detailed_scores))
    rows = []
    for name in names:
        simple_mean = _mean(simple_scores.get(name, []))
        detailed_mean = _mean(detailed_scores.get(name, []))
        change = None
        if simple_mean is not None and detailed_mean is not None:
            change = detailed_mean - simple_mean
        rows.append(
            {
                "metric": name,
                "simple": simple_mean,
                "detailed": detailed_mean,
                "change": change,
            }
        )
    summary = {
        "simple_result": str(simple_path),
        "detailed_result": str(detailed_path),
        "metrics": rows,
    }
    summary_path = ARTIFACTS / "evaluation_comparison.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    def cell(value: float | None) -> str:
        return "" if value is None else f"{value:.3f}"

    table = [
        "| Metric | Simple | Detailed | Change |",
        "| --- | --- | --- | --- |",
    ]
    for row in rows:
        table.append(
            f"| {row['metric']} | {cell(row['simple'])} | {cell(row['detailed'])} | {cell(row['change'])} |"
        )
    generated = "\n".join(
        [
            "## Results",
            "",
            "Generated by `scripts/generate_eval_results.py`.",
            "",
            f"- Simple: `{simple_path.name}`",
            f"- Detailed: `{detailed_path.name}`",
            "",
            *table,
            "",
        ]
    )
    existing = REPORT.read_text(encoding="utf-8") if REPORT.exists() else ""
    marker = "## Results"
    if marker in existing:
        existing = existing[: existing.index(marker)].rstrip() + "\n\n"
    REPORT.write_text(existing + generated, encoding="utf-8")
    print(f"Wrote {summary_path}")
    print(f"Updated {REPORT}")


def main() -> None:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    simple_path = _run_style("simple")
    detailed_path = _run_style("detailed")
    _write_comparison(simple_path, detailed_path)


if __name__ == "__main__":
    main()
