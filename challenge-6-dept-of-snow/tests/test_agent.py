"""Checks the ADS router and the tools each specialist is allowed to call."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class AdsFieldOpsTest(unittest.TestCase):
    def test_root_routes_to_three_specialists(self):
        from ads_field_ops.agent import app
        from ads_field_ops.agent import root_agent

        names = [agent.name for agent in root_agent.sub_agents]
        self.assertEqual(
            names,
            [
                "dispatch_specialist",
                "road_status_specialist",
                "public_comms_specialist",
            ],
        )
        self.assertEqual(root_agent.tools, [])
        self.assertEqual(app.name, "ads-field-ops")
        self.assertEqual(app.root_agent, root_agent)

    def test_specialists_keep_search_off_the_mcp_agents(self):
        from ads_field_ops.agent import conditions_specialist
        from ads_field_ops.agent import dispatch_specialist
        from ads_field_ops.agent import public_comms_specialist
        from ads_field_ops.agent import road_status_specialist

        self.assertEqual(conditions_specialist.tools[0].name, "google_search")
        self.assertEqual(len(dispatch_specialist.tools), 1)
        road_tool_types = [type(tool).__name__ for tool in road_status_specialist.tools]
        self.assertIn("AgentTool", road_tool_types)
        from ads_field_ops.agent import DISCOVERY_ENGINE_DATASTORE_FULL_NAME

        policy_tool = public_comms_specialist.tools[0]
        self.assertEqual(policy_tool.name, "search_ads_policy")
        self.assertTrue(
            policy_tool._serving_config.startswith(DISCOVERY_ENGINE_DATASTORE_FULL_NAME)
        )
