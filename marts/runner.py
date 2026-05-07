"""Marts orchestration."""
from __future__ import annotations

from marts import (
    championship_progression,
    circuit_difficulty_index,
    dnf_analysis,
    driver_overperformance,
    pace_evolution,
    pit_crew_ranking,
    race_narrative,
    season_summary,
    teammate_h2h,
)

TASKS = [
    championship_progression,
    teammate_h2h,
    circuit_difficulty_index,
    pit_crew_ranking,
    driver_overperformance,
    dnf_analysis,
    pace_evolution,
    race_narrative,
    season_summary,
]


def run_all() -> None:
    for mod in TASKS:
        mod.build()
