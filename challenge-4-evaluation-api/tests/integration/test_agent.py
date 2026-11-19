"""Checks that the loaded agent carries the selected Harbor Bites instructions."""

from __future__ import annotations

import importlib
import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _load_agent(prompt_style: str):
    os.environ["HARBOR_PROMPT_STYLE"] = prompt_style
    name = "harbor_support_agent.agent"
    if name in sys.modules:
        return importlib.reload(sys.modules[name])
    return importlib.import_module(name)


class AgentInstructionTest(unittest.TestCase):
    def test_simple_style_stays_friendly_and_omits_negative_rules(self):
        agent = _load_agent("simple")
        self.assertIn(
            "friendly, practical, and customer-focused",
            agent.ACTIVE_INSTRUCTIONS,
        )
        self.assertNotIn("What not to do:", agent.ACTIVE_INSTRUCTIONS)
        self.assertEqual(agent.root_agent.instruction, agent.SIMPLE_INSTRUCTIONS)

    def test_detailed_style_embeds_the_kitchen_policies(self):
        agent = _load_agent("detailed")
        self.assertIn("Policy 1. Refund window", agent.ACTIVE_INSTRUCTIONS)
        self.assertIn("Policy 11. Shift swaps", agent.ACTIVE_INSTRUCTIONS)
        self.assertIn("Policy 12. Payment data", agent.ACTIVE_INSTRUCTIONS)
        self.assertEqual(agent.root_agent.name, "harbor_customer_service_agent")
        self.assertEqual(agent.app.name, "harbor_support_agent")
        self.assertEqual(agent.root_agent.model, agent.MODEL_NAME)
        self.assertEqual(agent.root_agent.tools, [])
