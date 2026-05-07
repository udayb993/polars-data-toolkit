"""Silver-layer orchestration."""
from __future__ import annotations

from silver import (
    circuits,
    constructor_standings,
    constructors,
    drivers,
    driver_standings,
    lap_times,
    pit_stops,
    qualifying,
    races,
    results,
    seasons,
    sprint_results,
    status,
)

# ``races`` must come before any module that joins on race_id (results,
# qualifying, sprint, pit_stops, lap_times).
TASKS = [
    seasons,
    circuits,
    drivers,
    constructors,
    status,
    races,
    results,
    qualifying,
    sprint_results,
    driver_standings,
    constructor_standings,
    pit_stops,
    lap_times,
]


def run_all() -> None:
    for mod in TASKS:
        mod.build()
