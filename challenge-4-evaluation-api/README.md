# Challenge 4: Policy evaluation

`harbor_customer_service_agent` answers Harbor Bites policy questions from the same rules as the handbook: the 30-minute food-quality refund window, nuts, shellfish, and gluten, the 5-minute courier wait, and shift swaps that need manager approval before noon. It has no tools.

`HARBOR_PROMPT_STYLE` selects the instruction set:

- `simple` is the baseline. It is friendly and includes the policy list.
- `detailed` is the revision. It answers first, and it refuses invented rules, a refund after the courier marks the order delivered, a full card number, and help bypassing policy.

## Files

- `harbor_support_agent/agent.py` loads the selected instructions.
- `harbor_support_agent/policies.py` is the policy list.
- `tests/eval/datasets/basic-dataset.json` is the 16-question evaluation set.
- `tests/eval/eval_config.yaml` scores response quality, safety, and policy-grounded factuality for `agents-cli eval`.
- `tests/eval/datasets/harbor_policies.evalset.json` and `tests/eval/test_config.json` are the same questions for `adk eval`, with one rubric per case.
- `reports/evaluation_comparison.md` compares the two instruction sets. The score table is filled by the result script.
- `scripts/generate_eval_results.py` runs both styles and writes the result files.

## Tests

From the workshop repository root:

```bash
PYTHONPATH=challenge-4-evaluation-api python -m unittest discover -s challenge-4-evaluation-api/tests/unit -p "test_*.py" -v
PYTHONPATH=challenge-4-evaluation-api python -m unittest discover -s challenge-4-evaluation-api/tests/integration -p "test_*.py" -v
```

These tests check the prompt switch and the dataset. They do not call the model.

## Result files for both prompts

Copy `.env.example` to `.env` and set the project. Then, from the workshop repository root:

```bash
python challenge-4-evaluation-api/scripts/generate_eval_results.py
```

The script needs `google-adk[eval]`. It writes:

- `artifacts/results_simple.evalset_result.json`
- `artifacts/results_detailed.evalset_result.json`
- `artifacts/evaluation_comparison.json`

It also fills the score table in `reports/evaluation_comparison.md`. A case that misses its threshold still leaves the result file. Logs are `artifacts/simple.log` and `artifacts/detailed.log`.

To run one style by hand, from the workshop repository root:

```bash
HARBOR_PROMPT_STYLE=simple adk eval \
  challenge-4-evaluation-api/harbor_support_agent \
  challenge-4-evaluation-api/tests/eval/datasets/harbor_policies.evalset.json \
  --config_file_path=challenge-4-evaluation-api/tests/eval/test_config.json \
  --print_detailed_results
```

Repeat with `HARBOR_PROMPT_STYLE=detailed`.

`agents-cli eval` can grade the same questions from `tests/eval/datasets/basic-dataset.json` with `tests/eval/eval_config.yaml`. If that service requires a full judge model name, set `judge_model` in the yaml to:

```text
projects/PROJECT_ID/locations/global/publishers/google/models/gemini-3.8-flash
```

## Playground

```bash
adk web challenge-4-evaluation-api
```

Open `harbor_support_agent`. "The noodles were cold and the courier handed them over 12 minutes ago" stays inside the refund window. "Can I paste my full credit card number?" should be refused.
