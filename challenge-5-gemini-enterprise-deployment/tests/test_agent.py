"""Checks that the deployed agent carries the Harbor Bites policies."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class HarborSupportTest(unittest.TestCase):
    def test_agent_answers_from_embedded_policies(self):
        from harbor_support.agent import app
        from harbor_support.agent import root_agent

        self.assertEqual(root_agent.name, "harbor_customer_service_agent")
        self.assertEqual(app.name, "harbor-bites-support")
        self.assertEqual(app.root_agent, root_agent)
        self.assertEqual(root_agent.tools, [])
        self.assertIn("30 minutes", root_agent.instruction)
        self.assertIn("before noon", root_agent.instruction)
        self.assertIn("full payment card number", root_agent.instruction)
