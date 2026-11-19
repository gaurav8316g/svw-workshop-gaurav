"""Checks the handbook file and that the root agent routes to both specialists."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

HANDBOOK = PROJECT_ROOT / "harbor_bites_employee_handbook.md"


class HandbookFileTest(unittest.TestCase):
    def test_handbook_covers_the_four_staff_topics(self):
        text = HANDBOOK.read_text(encoding="utf-8")
        self.assertIn("30 minutes", text)
        self.assertIn("Once the courier marks the order delivered", text)
        self.assertIn("nuts", text.lower())
        self.assertIn("shellfish", text.lower())
        self.assertIn("gluten", text.lower())
        self.assertIn("missing an allergy flag", text)
        self.assertIn("5 minutes", text)
        self.assertIn("no-show", text)
        self.assertIn("before noon", text)


class HelpdeskRoutingTest(unittest.TestCase):
    def test_root_delegates_to_handbook_and_web_specialists(self):
        from google.adk.tools.google_search_tool import GoogleSearchTool
        from google.adk.tools.vertex_ai_search_tool import VertexAiSearchTool
        from harbor_helpdesk.agent import handbook_specialist
        from harbor_helpdesk.agent import root_agent
        from harbor_helpdesk.agent import web_specialist

        self.assertEqual(root_agent.name, "harbor_helpdesk")
        self.assertEqual(
            [agent.name for agent in root_agent.sub_agents],
            ["handbook_specialist", "web_specialist"],
        )
        self.assertEqual(handbook_specialist.mode, "single_turn")
        self.assertEqual(web_specialist.mode, "single_turn")
        self.assertIsInstance(
            handbook_specialist.tools[0], VertexAiSearchTool
        )
        self.assertIsInstance(web_specialist.tools[0], GoogleSearchTool)
        delegated = {tool.name for tool in root_agent.tools}
        self.assertEqual(
            delegated, {"handbook_specialist", "web_specialist"}
        )
        self.assertIn("handbook_specialist", root_agent.instruction)
        self.assertIn("web_specialist", root_agent.instruction)
        self.assertIn("refund window", root_agent.instruction)
        self.assertIn("raining in Austin", root_agent.instruction)
