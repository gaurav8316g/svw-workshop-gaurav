# Challenge 4 Solution: Agent Evaluation API

This folder contains an independent solution project for Challenge 4.

## Goal
Use evaluation to:

- Author an evaluation dataset
- Run evaluations for response quality, safety, and policy-grounded factuality
- Improve the prompt and re-run to verify the change

## Scope For This Lab
Keep this project self-contained and runnable on its own.

## Status
Implemented with:

- A Harbor Bites customer-service agent with no tools
- A 16-question evaluation dataset
- Two prompt modes for a before-and-after comparison
- A result script that writes both runs and fills the comparison report

## Use Case
`harbor_customer_service_agent` answers Harbor Bites policy questions from the same rules as the handbook: the 30-minute food-quality refund window, nuts, shellfish, and gluten, the 5-minute courier wait, and shift swaps that need manager approval before noon.

This challenge is intentionally simple:

- No external tools
- No complex orchestration
- Focus on the evaluation loop

## Files You Will Use
- `harbor_support_agent/agent.py` loads the selected instructions
- `harbor_support_agent/policies.py` is the policy list
- `tests/eval/datasets/basic-dataset.json` is the 16-question set for `agents-cli eval`
- `tests/eval/eval_config.yaml` scores response quality, safety, and policy-grounded factuality
- `tests/eval/datasets/harbor_policies.evalset.json` and `tests/eval/test_config.json` are the same questions for `adk eval`, with one rubric per case
- `reports/evaluation_comparison.md` compares the two instruction sets. The score table is filled by the result script
- `scripts/generate_eval_results.py` runs both styles and writes the result files

## Prompt Modes
The agent reads `HARBOR_PROMPT_STYLE`:

- `simple` is the baseline. It is friendly and includes the policy list.
- `detailed` is the revision. It answers first, and it refuses invented rules, a refund after the courier marks the order delivered, a full card number, and help bypassing policy.

Default is `simple`.

## Prerequisites
- Python 3.10+
- A virtual environment
- `google-adk` installed
- `google-adk[eval]` for the result script
- Application Default Credentials for Vertex AI
- `GOOGLE_CLOUD_PROJECT` set to a real project, with the Vertex AI API enabled

## Environment Variables
```bash
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project
GOOGLE_CLOUD_LOCATION=us-central1
HARBOR_PROMPT_STYLE=simple
```

Replace `your-project` with the real project ID.

## Setup
From the workshop repository root:

```bash
cd ./challenge-4-evaluation-api
python -m venv .venv
source .venv/bin/activate
pip install -e ".[eval]"
cp .env.example .env
```

## Running Tests
From the workshop repository root. These tests check the prompt switch and the dataset. They do not call the model.

```bash
cd ./challenge-4-evaluation-api
source .venv/bin/activate
PYTHONPATH=. python -m unittest discover -s tests/unit -p "test_*.py" -v
PYTHONPATH=. python -m unittest discover -s tests/integration -p "test_*.py" -v
```

## Evaluation Workflow
Copy `.env.example` to `.env` and set the project. Then, from the workshop repository root:

```bash
cd ./challenge-4-evaluation-api
source .venv/bin/activate
python scripts/generate_eval_results.py
```

The script writes:

- `artifacts/results_simple.evalset_result.json`
- `artifacts/results_detailed.evalset_result.json`
- `artifacts/evaluation_comparison.json`

It also fills the score table in `reports/evaluation_comparison.md`. A case that misses its threshold still leaves the result file. Logs are `artifacts/simple.log` and `artifacts/detailed.log`.

### 1) Baseline Run (Simple Instructions)
From the workshop repository root:

```bash
cd ./challenge-4-evaluation-api
source .venv/bin/activate
HARBOR_PROMPT_STYLE=simple adk eval \
  harbor_support_agent \
  tests/eval/datasets/harbor_policies.evalset.json \
  --config_file_path=tests/eval/test_config.json \
  --print_detailed_results
```

### 2) Improved Run (Detailed Instructions)
```bash
cd ./challenge-4-evaluation-api
source .venv/bin/activate
HARBOR_PROMPT_STYLE=detailed adk eval \
  harbor_support_agent \
  tests/eval/datasets/harbor_policies.evalset.json \
  --config_file_path=tests/eval/test_config.json \
  --print_detailed_results
```

`agents-cli eval` can grade the same questions from `tests/eval/datasets/basic-dataset.json` with `tests/eval/eval_config.yaml`. If that service requires a full judge model name, set `judge_model` in the yaml to:

```text
projects/PROJECT_ID/locations/global/publishers/google/models/gemini-3.8-flash
```

The three judges are `FINAL_RESPONSE_QUALITY`, `SAFETY`, and `policy_grounded_factuality`. The config supplies its own judge prompts so the judge model stays `gemini-3.8-flash`.

## Playground
From the workshop repository root:

```bash
cd ./challenge-4-evaluation-api
source .venv/bin/activate
adk web .
```

Open `harbor_support_agent`. "The noodles were cold and the courier handed them over 12 minutes ago" stays inside the refund window. "Can I paste my full credit card number?" should be refused.

## Notes
- Responses should stay in plain language.
- The detailed prompt includes explicit negative instructions for what not to do.
- No human escalation path is used in this scenario.
