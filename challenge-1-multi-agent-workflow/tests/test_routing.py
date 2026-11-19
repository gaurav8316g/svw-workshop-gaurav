"""Unit tests for architecture review routing logic."""

import unittest
from unittest.mock import MagicMock

from architecture_review.agent import (
    DEFAULT_SCENARIO,
    GOOD_DESIGN,
    MAX_ITERATIONS,
    after_refine,
    as_text,
    capture_scenario,
    finalize,
    is_adequate,
    is_good_design,
    root_agent,
    route_human,
)


class TestArchitectureReviewRouting(unittest.TestCase):
    def test_capture_scenario(self):
        scenario_text = "design a food-delivery app"
        event = capture_scenario(scenario_text)
        self.assertEqual(event.output, scenario_text)
        self.assertEqual(event.actions.state_delta["scenario"], scenario_text)
        self.assertEqual(event.actions.state_delta["review_round"], 0)

    def test_capture_scenario_default(self):
        event = capture_scenario("")
        self.assertEqual(event.output, DEFAULT_SCENARIO)
        self.assertEqual(event.actions.state_delta["scenario"], DEFAULT_SCENARIO)

    def test_is_good_design(self):
        self.assertTrue(is_good_design("The design is good."))
        self.assertTrue(is_good_design("The design is good"))
        self.assertTrue(is_good_design('"The design is good."'))
        self.assertFalse(is_good_design("The design needs work."))
        self.assertFalse(is_good_design(""))

    def test_is_adequate(self):
        self.assertTrue(is_adequate("yes"))
        self.assertTrue(is_adequate("Yes"))
        self.assertTrue(is_adequate("lgtm"))
        self.assertTrue(is_adequate("approved"))
        self.assertFalse(is_adequate("no, fix caching"))

    def test_after_refine_good_design(self):
        ctx = MagicMock()
        ctx.state = {
            "review_round": 1,
            "architecture_draft": "Draft v1",
        }
        event = after_refine(ctx, "The design is good.")
        self.assertEqual(event.actions.route, "done")
        self.assertEqual(event.actions.state_delta["stop_reason"], "design_is_good")
        self.assertEqual(event.actions.state_delta["architecture_draft"], "Draft v1")

    def test_after_refine_continue_loop(self):
        ctx = MagicMock()
        ctx.state = {
            "review_round": 0,
            "architecture_draft": "Draft v0",
        }
        event = after_refine(ctx, "Draft v1 with improved caching")
        self.assertEqual(event.actions.route, "continue")
        self.assertEqual(event.actions.state_delta["review_round"], 1)
        self.assertEqual(
            event.actions.state_delta["architecture_draft"], "Draft v1 with improved caching"
        )
        self.assertEqual(event.actions.state_delta["stop_reason"], "")

    def test_after_refine_max_iterations(self):
        ctx = MagicMock()
        ctx.state = {
            "review_round": 2,
            "architecture_draft": "Draft v2",
        }
        event = after_refine(ctx, "Draft v3 with final tweaks")
        self.assertEqual(event.actions.route, "done")
        self.assertEqual(event.actions.state_delta["review_round"], MAX_ITERATIONS)
        self.assertEqual(event.actions.state_delta["stop_reason"], "max_iterations")

    def test_route_human_adequate(self):
        ctx = MagicMock()
        ctx.state = {"review_round": 1}
        event = route_human(ctx, "yes")
        self.assertEqual(event.actions.route, "done")
        self.assertEqual(event.actions.state_delta["human_verdict"], "adequate")

    def test_route_human_revise_under_cap(self):
        ctx = MagicMock()
        ctx.state = {"review_round": 1}
        event = route_human(ctx, "Needs Redis for session management")
        self.assertEqual(event.actions.route, "revise")
        self.assertEqual(event.actions.state_delta["human_verdict"], "revise")
        self.assertEqual(
            event.actions.state_delta["human_feedback"], "Needs Redis for session management"
        )

    def test_route_human_changes_requested_after_cap(self):
        ctx = MagicMock()
        ctx.state = {"review_round": 3}
        event = route_human(ctx, "Needs more database indexing")
        self.assertEqual(event.actions.route, "done")
        self.assertEqual(
            event.actions.state_delta["human_verdict"], "changes_requested_after_cap"
        )
        self.assertEqual(
            event.actions.state_delta["human_feedback"], "Needs more database indexing"
        )

    def test_finalize_good_design(self):
        event = finalize(
            architecture_draft="Final Draft",
            review_round=2,
            stop_reason="design_is_good",
            human_verdict="adequate",
        )
        msg_text = as_text(event.content)
        self.assertIn(GOOD_DESIGN, msg_text)
        self.assertIn("Final Draft", msg_text)

    def test_workflow_structure(self):
        self.assertEqual(root_agent.name, "architecture_review")
        self.assertIsNotNone(root_agent)


if __name__ == "__main__":
    unittest.main()
