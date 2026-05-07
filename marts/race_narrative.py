"""marts.race_narrative — one row per race summarising the story.

Joins ``race_facts`` with ``driver_race_performance`` aggregates to find the
biggest position-mover, biggest faller, and so on.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write


def build() -> pl.DataFrame:
    rf = scan("intermediate", "race_facts")
    drp = scan("intermediate", "driver_race_performance")

    movers = (
        drp.filter(pl.col("positions_gained").is_not_null())
        .sort(["race_id", "positions_gained"], descending=[False, True])
        .group_by("race_id")
        .agg(
            pl.col("driver_id").first().alias("biggest_mover_driver"),
            pl.col("positions_gained").first().alias("biggest_mover_positions"),
        )
    )
    fallers = (
        drp.filter(pl.col("positions_gained").is_not_null())
        .sort(["race_id", "positions_gained"], descending=[False, False])
        .group_by("race_id")
        .agg(
            pl.col("driver_id").first().alias("biggest_faller_driver"),
            pl.col("positions_gained").first().alias("biggest_faller_positions"),
        )
    )

    df = (
        rf.join(movers, on="race_id", how="left")
        .join(fallers, on="race_id", how="left")
        .select(
            "race_id", "season", "round", "race_date", "race_name", "circuit_id",
            "pole_driver_id", "winner_driver_id", "winner_constructor_id",
            "fastest_lap_driver_id", "fastest_lap_time",
            "n_starters", "n_dnfs", "n_pit_stops", "total_laps",
            "biggest_mover_driver", "biggest_mover_positions",
            "biggest_faller_driver", "biggest_faller_positions",
        )
        .sort(["season", "round"])
        .collect()
    )
    write(df, "marts", "race_narrative")
    return df


if __name__ == "__main__":
    build()
