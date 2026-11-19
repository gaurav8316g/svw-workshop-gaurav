# Evaluation Dataset

This folder holds the Harbor Bites cases used by Challenge 4.

## Goal
Give both evaluation runners the same 16 customer and staff questions about refunds, allergens, couriers, and shift swaps.

## Files
- `basic-dataset.json` is the set used by `agents-cli eval`.
- `harbor_policies.evalset.json` is the same questions in the ADK eval-set shape, with one rubric per case, for `adk eval`.

## Run
From the workshop repository root, enter Challenge 4 and activate its virtual environment before any command that reads these files:

```bash
cd ./challenge-4-evaluation-api
source .venv/bin/activate
```

The result script and the Challenge 4 README run these files. They do not call the model by themselves.
