"""Custom MCP server for Harbor Bites kitchen operations.

Exposes a few Python functions over stdio. The Harbor ops sub-agent connects
to this process with McpToolset.

    python harbor_ops_server.py
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

REFUND_WINDOW_MINUTES = 30
COURIER_WAIT_MINUTES = 5

ALLERGEN_RULES = {
    "nuts": (
        "Stop the ticket. Remake the order away from shared equipment and "
        "flag the bag in red."
    ),
    "shellfish": (
        "Cook only at the shellfish station. Do not plate this order on the "
        "grill line."
    ),
    "gluten": "Use the gluten-free prep board and a clean pan.",
}

mcp = FastMCP("harbor-bites-ops")


@mcp.tool()
def check_refund(
    minutes_since_delivery: int,
    courier_marked_delivered: bool,
    food_quality_issue: bool,
) -> str:
    """Decide whether a Harbor Bites order qualifies for a refund.

    Refunds are only for food-quality issues reported within 30 minutes.
    After the courier marks the order delivered, that same 30-minute window
    still applies.
    """
    if not food_quality_issue:
        return "No refund. Harbor Bites refunds only food-quality issues."
    if minutes_since_delivery > REFUND_WINDOW_MINUTES:
        delivered = (
            " The courier already marked the order delivered."
            if courier_marked_delivered
            else ""
        )
        return (
            "No refund. The 30-minute food-quality window has passed."
            + delivered
        )
    return "Refund approved. Issue a full refund for the food-quality problem."


@mcp.tool()
def lookup_allergen_rule(allergen: str) -> str:
    """Return the Harbor Bites kitchen rule for nuts, shellfish, or gluten."""
    rule = ALLERGEN_RULES.get(allergen.strip().lower())
    if rule is None:
        return (
            f"No Harbor Bites rule for {allergen}. Ask a manager before cooking."
        )
    return rule


@mcp.tool()
def report_courier_noshow(order_id: str, minutes_waiting: int) -> str:
    """Hold a bag for 5 minutes, then reassign the courier and log a no-show."""
    if minutes_waiting < COURIER_WAIT_MINUTES:
        return (
            f"Order {order_id} is still inside the 5-minute wait. Hold the bag."
        )
    return (
        f"Order {order_id} waited {minutes_waiting} minutes. "
        "Reassign the courier and log a no-show."
    )


@mcp.tool()
def request_shift_swap(
    employee: str,
    shift_date: str,
    requested_before_noon: bool,
) -> str:
    """Record a shift swap. Requests after noon are rejected."""
    if requested_before_noon:
        return (
            f"Shift swap for {employee} on {shift_date} is pending manager "
            "approval."
        )
    return (
        f"Shift swap for {employee} on {shift_date} was rejected. "
        "Requests must be submitted before noon."
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
