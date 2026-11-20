"""Checks the ADS field-system rules the MCP server exposes."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ads_backend import dispatch_plow
from ads_backend import get_road_status
from ads_backend import list_plow_units
from ads_backend import record_public_alert
from ads_backend import reset_state
from ads_backend import set_road_closure


class AdsBackendTest(unittest.TestCase):
    def setUp(self):
        reset_state()

    def test_dispatch_uses_an_available_unit(self):
        self.assertIn("available", list_plow_units("Anchorage"))
        result = dispatch_plow("12", "Glenn Highway", "MP 40", "light snow")
        self.assertIn("Dispatched unit 12", result)
        self.assertIn("on route", dispatch_plow("7", "Parks Highway", "MP 200", "ice"))

    def test_closure_requires_a_duty_officer(self):
        refused = set_road_closure("Parks Highway", "200", "220", "ice", "")
        self.assertIn("Closure refused", refused)
        closed = set_road_closure(
            "Parks Highway", "200", "220", "ice", "Duty Officer Kim"
        )
        self.assertIn("Duty officer: Duty Officer Kim", closed)
        self.assertIn("closed", get_road_status("Parks Highway"))

    def test_public_alert_rejects_a_phone_number(self):
        refused = record_public_alert(
            "Seward Highway",
            "Closed. Call 907-555-0142.",
            "public",
        )
        self.assertIn("Alert refused", refused)
        stored = record_public_alert(
            "Seward Highway",
            "Seward Highway MP 90-105 is closed for avalanche risk. "
            "Review at 18:00.",
            "public",
        )
        self.assertIn("Recorded a public alert", stored)

    def test_policy_file_matches_the_field_rules(self):
        text = (PROJECT_ROOT / "ads_policies" / "ads_storm_procedures.md").read_text()
        self.assertIn("Only a named duty officer can close", text)
        self.assertIn("personal phone number", text)
        self.assertIn("Anchorage covers the Glenn Highway", text)
