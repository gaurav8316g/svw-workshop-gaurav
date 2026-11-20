"""MCP server for the Alaska Department of Snow field systems.

    python ads_backend_server.py
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from ads_backend import dispatch_plow as _dispatch_plow
from ads_backend import get_road_status as _get_road_status
from ads_backend import list_plow_units as _list_plow_units
from ads_backend import record_public_alert as _record_public_alert
from ads_backend import set_road_closure as _set_road_closure

mcp = FastMCP("alaska-department-of-snow")


@mcp.tool()
def list_plow_units(depot: str = "") -> str:
    """List ADS plow units. Pass a depot such as Anchorage, or leave it blank."""
    return _list_plow_units(depot)


@mcp.tool()
def dispatch_plow(unit_id: str, route: str, milepost: str, reason: str) -> str:
    """Dispatch an available plow unit to a route and milepost."""
    return _dispatch_plow(unit_id, route, milepost, reason)


@mcp.tool()
def get_road_status(route: str) -> str:
    """Read the ADS status for Glenn Highway, Seward Highway, or Parks Highway."""
    return _get_road_status(route)


@mcp.tool()
def set_road_closure(
    route: str,
    milepost_from: str,
    milepost_to: str,
    reason: str,
    duty_officer: str,
) -> str:
    """Close a highway segment. duty_officer must be the officer who approved it."""
    return _set_road_closure(route, milepost_from, milepost_to, reason, duty_officer)


@mcp.tool()
def record_public_alert(route: str, message: str, channel: str = "public") -> str:
    """Record a public storm alert. The message cannot contain a phone number."""
    return _record_public_alert(route, message, channel)


if __name__ == "__main__":
    mcp.run()
