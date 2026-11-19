"""Checks that the prompt switch and the policy text stay aligned."""

from __future__ import annotations

import importlib
import json
import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATASET = PROJECT_ROOT / "tests" / "eval" / "datasets" / "basic-dataset.json"
EVALSET = PROJECT_ROOT / "tests" / "eval" / "datasets" / "harbor_policies.evalset.json"
CONFIG = PROJECT_ROOT / "tests" / "eval" / "eval_config.yaml"


def _load_agent(prompt_style: str | None):
    if prompt_style is None:
        os.environ.pop("HARBOR_PROMPT_STYLE", None)
    else:
        os.environ["HARBOR_PROMPT_STYLE"] = prompt_style
    name = "harbor_support_agent.agent"
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


class PromptStyleTest(unittest.TestCase):
    def test_prompt_style_defaults_to_simple(self):
        agent = _load_agent(None)
        self.assertEqual(agent.PROMPT_STYLE, "simple")
        self.assertEqual(agent.ACTIVE_INSTRUCTIONS, agent.SIMPLE_INSTRUCTIONS)
        self.assertNotIn("What not to do:", agent.ACTIVE_INSTRUCTIONS)

    def test_detailed_prompt_adds_negative_rules(self):
        agent = _load_agent("detailed")
        self.assertEqual(agent.PROMPT_STYLE, "detailed")
        self.assertIn("What to do:", agent.ACTIVE_INSTRUCTIONS)
        self.assertIn("What not to do:", agent.ACTIVE_INSTRUCTIONS)
        self.assertIn("Do not invent refund windows", agent.ACTIVE_INSTRUCTIONS)
        self.assertIn(
            "Do not ask for a full payment card number",
            agent.ACTIVE_INSTRUCTIONS,
        )
        self.assertIn("30 minutes", agent.ACTIVE_INSTRUCTIONS)
        self.assertIn("before noon", agent.ACTIVE_INSTRUCTIONS)


class EvalDatasetTest(unittest.TestCase):
    def test_dataset_matches_the_adk_eval_set(self):
        dataset = json.loads(DATASET.read_text())
        evalset = json.loads(EVALSET.read_text())
        dataset_ids = [case["eval_case_id"] for case in dataset["eval_cases"]]
        eval_ids = [case["eval_id"] for case in evalset["eval_cases"]]
        self.assertEqual(len(dataset_ids), len(set(dataset_ids)))
        self.assertEqual(dataset_ids, eval_ids)
        for case in dataset["eval_cases"]:
            self.assertTrue(case["prompt"]["parts"][0]["text"].strip())
        config = CONFIG.read_text()
        self.assertIn("FINAL_RESPONSE_QUALITY", config)
        self.assertIn("SAFETY", config)
        self.assertIn("policy_grounded_factuality", config)
        self.assertIn("30 minutes", config)
