"""In-memory Alaska Department of Snow field systems.

The MCP server exposes these functions. State lasts for the server process
and resets when that process stops.
"""

from __future__ import annotations

import re

PLOW_UNITS = {
    "12": {
        "unit_id": "12",
        "depot": "Anchorage",
        "driver": "Lena Cho",
        "status": "available",
        "assignment": "",
    },
    "7": {
        "unit_id": "7",
        "depot": "Fairbanks",
        "driver": "Marcus Reid",
        "status": "on route",
        "assignment": "Glenn Highway MP 20",
    },
    "3": {
        "unit_id": "3",
        "depot": "Juneau",
        "driver": "Ava Bennett",
        "status": "maintenance",
        "assignment": "",
    },
}

ROADS = {
    "glenn highway": {
        "route": "Glenn Highway",
        "mileposts": "MP 40-55",
        "status": "open",
        "condition": "light snow",
    },
    "seward highway": {
        "route": "Seward Highway",
        "mileposts": "MP 90-105",
        "status": "closed",
        "condition": "avalanche risk",
    },
    "parks highway": {
        "route": "Parks Highway",
        "mileposts": "MP 200-220",
        "status": "open",
        "condition": "ice",
    },
}

ALERTS: list[dict[str, str]] = []
_PHONE = re.compile(r"\d{3}[-.\s]?\d{3}[-.\s]?\d{4}")


def reset_state() -> None:
    """Restore the sample fleet, roads, and alert log."""
    PLOW_UNITS["12"].update(status="available", assignment="")
    PLOW_UNITS["7"].update(status="on route", assignment="Glenn Highway MP 20")
    PLOW_UNITS["3"].update(status="maintenance", assignment="")
    ROADS["glenn highway"].update(status="open", condition="light snow")
    ROADS["seward highway"].update(status="closed", condition="avalanche risk")
    ROADS["parks highway"].update(status="open", condition="ice")
    ALERTS.clear()


def list_plow_units(depot: str = "") -> str:
    """List plow units, optionally limited to one depot."""
    wanted = depot.strip().lower()
    rows = [
        unit
        for unit in PLOW_UNITS.values()
        if not wanted or unit["depot"].lower() == wanted
    ]
    if not rows:
        return f"No plow units are based at {depot}."
    lines = []
    for unit in rows:
        assignment = unit["assignment"] or "none"
        lines.append(
            f"Unit {unit['unit_id']} ({unit['depot']}): {unit['status']}, "
            f"driver {unit['driver']}, assignment {assignment}."
        )
    return "\n".join(lines)


def dispatch_plow(unit_id: str, route: str, milepost: str, reason: str) -> str:
    """Assign an available plow unit. Units on route or in maintenance stay put."""
    unit = PLOW_UNITS.get(unit_id.strip())
    if unit is None:
        return f"Unit {unit_id} is not in the ADS fleet."
    if unit["status"] != "available":
        return (
            f"Unit {unit['unit_id']} is {unit['status']} and cannot be dispatched. "
            "Choose an available unit, or get duty-officer approval before "
            "pulling a unit off an active assignment."
        )
    assignment = f"{route} {milepost}".strip()
    unit["status"] = "dispatched"
    unit["assignment"] = assignment
    return (
        f"Dispatched unit {unit['unit_id']} from {unit['depot']} to {assignment}. "
        f"Reason: {reason}."
    )


def get_road_status(route: str) -> str:
    """Return the stored status for a named Alaska highway."""
    road = ROADS.get(route.strip().lower())
    if road is None:
        known = ", ".join(item["route"] for item in ROADS.values())
        return f"ADS has no status for {route}. Known routes: {known}."
    return (
        f"{road['route']} {road['mileposts']} is {road['status']} "
        f"({road['condition']})."
    )


def set_road_closure(
    route: str,
    milepost_from: str,
    milepost_to: str,
    reason: str,
    duty_officer: str,
) -> str:
    """Close a highway segment. A duty officer name is required."""
    if not duty_officer.strip():
        return (
            "Closure refused. Only a named duty officer can close a state highway."
        )
    road = ROADS.get(route.strip().lower())
    if road is None:
        return f"ADS has no route named {route}."
    road["status"] = "closed"
    road["condition"] = reason.strip() or road["condition"]
    road["mileposts"] = f"MP {milepost_from}-{milepost_to}"
    return (
        f"{road['route']} {road['mileposts']} is closed ({road['condition']}). "
        f"Duty officer: {duty_officer.strip()}."
    )


def record_public_alert(route: str, message: str, channel: str) -> str:
    """Store a public alert after rejecting phone numbers and resident names."""
    if _PHONE.search(message):
        return (
            "Alert refused. Public alerts cannot include a phone number. "
            "Use the route, mileposts, and the next review time."
        )
    if "resident" in message.lower():
        return "Alert refused. Do not name residents in a public alert."
    record = {
        "route": route.strip(),
        "channel": channel.strip() or "public",
        "message": message.strip(),
    }
    ALERTS.append(record)
    return (
        f"Recorded a {record['channel']} alert for {record['route']}: "
        f"{record['message']}"
    )
