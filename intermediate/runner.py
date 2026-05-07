"""Intermediate-layer orchestration."""
from __future__ import annotations

from intermediate import (
    championship_state,
    constructor_race_performance,
    driver_form,
    driver_race_performance,
    lap_pace_normalized,
    pit_stop_efficiency,
    qualifying_vs_race,
    race_facts,
)

# Order matters: driver_form depends on driver_race_performance;
# constructor_race_performance also depends on driver_race_performance.
TASKS = [
    race_facts,
    driver_race_performance,
    constructor_race_performance,
    lap_pace_normalized,
    pit_stop_efficiency,
    qualifying_vs_race,
    driver_form,
    championship_state,
]


def run_all() -> None:
    for mod in TASKS:
        mod.build()
