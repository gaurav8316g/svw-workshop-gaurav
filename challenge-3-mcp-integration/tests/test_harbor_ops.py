"""Checks the custom MCP tools and that the dispatcher wires both servers."""

from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from harbor_ops_server import check_refund
from harbor_ops_server import lookup_allergen_rule
from harbor_ops_server import report_courier_noshow
from harbor_ops_server import request_shift_swap
from mcp import ClientSession
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client


class HarborToolTest(unittest.TestCase):
    def test_refund_rules(self):
        self.assertIn(
            "Refund approved",
            check_refund(12, False, True),
        )
        self.assertIn(
            "window is closed",
            check_refund(12, True, True),
        )
        self.assertIn(
            "30-minute",
            check_refund(45, False, True),
        )
        self.assertIn(
            "only food-quality",
            check_refund(5, False, False),
        )

    def test_allergen_courier_and_shift_rules(self):
        self.assertIn("shellfish station", lookup_allergen_rule("Shellfish"))
        self.assertIn(
            "nuts, shellfish, and gluten",
            lookup_allergen_rule("sesame"),
        )
        self.assertIn("Hold the bag", report_courier_noshow("HB-1042", 3))
        self.assertIn("no-show", report_courier_noshow("HB-1042", 8))
        self.assertIn(
            "pending manager approval",
            request_shift_swap("Priya", "2026-11-20", True),
        )
        self.assertIn(
            "rejected",
            request_shift_swap("Priya", "2026-11-20", False),
        )


class HarborMcpServerTest(unittest.TestCase):
    def test_server_lists_and_calls_tools(self):
        tools, refund = asyncio.run(_list_and_call())
        self.assertEqual(
            tools,
            {
                "check_refund",
                "lookup_allergen_rule",
                "report_courier_noshow",
                "request_shift_swap",
            },
        )
        self.assertIn("Refund approved", refund)


class DispatcherTest(unittest.TestCase):
    def test_root_routes_to_both_mcp_sub_agents(self):
        from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
        from harbor_dispatcher.agent import google_maps_specialist
        from harbor_dispatcher.agent import harbor_ops
        from harbor_dispatcher.agent import root_agent

        self.assertEqual(root_agent.name, "harbor_dispatcher")
        self.assertEqual(
            [agent.name for agent in root_agent.sub_agents],
            ["harbor_ops", "google_maps_specialist"],
        )
        self.assertIsInstance(harbor_ops.tools[0], McpToolset)
        self.assertIsInstance(google_maps_specialist.tools[0], McpToolset)
        self.assertEqual(
            harbor_ops.tools[0].tool_filter,
            [
                "check_refund",
                "lookup_allergen_rule",
                "report_courier_noshow",
                "request_shift_swap",
            ],
        )


async def _list_and_call() -> tuple[set[str], str]:
    server = PROJECT_ROOT / "harbor_ops_server.py"
    params = StdioServerParameters(
        command=sys.executable,
        args=[str(server)],
    )
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            listed = await session.list_tools()
            names = {tool.name for tool in listed.tools}
            result = await session.call_tool(
                "check_refund",
                {
                    "minutes_since_delivery": 12,
                    "courier_marked_delivered": False,
                    "food_quality_issue": True,
                },
            )
    text = " ".join(
        block.text for block in result.content if hasattr(block, "text")
    )
    return names, text


if __name__ == "__main__":
    unittest.main()
