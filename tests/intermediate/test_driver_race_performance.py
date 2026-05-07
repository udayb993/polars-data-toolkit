"""Tests for intermediate.driver_race_performance."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_in_range, assert_no_duplicate_keys, load


def test_drp_primary_key_unique():
    df = load("intermediate", "driver_race_performance")
    assert_no_duplicate_keys(df, ["race_id", "driver_id"])


def test_drp_positions_gained_consistent():
    df = load("intermediate", "driver_race_performance").filter(
        pl.col("grid_position").is_not_null() & pl.col("finish_position").is_not_null()
    )
    bad = df.filter(pl.col("positions_gained") != (pl.col("grid_position") - pl.col("finish_position")))
    assert bad.height == 0


def test_drp_pace_vs_winner_in_range():
    df = load("intermediate", "driver_race_performance").filter(pl.col("pace_vs_winner_ratio").is_not_null())
    # A retiring driver who only ran fast stints can have ratio < 1; safety-car
    # backmarkers can exceed 1.5. Use loose bounds.
    assert_in_range(df, "pace_vs_winner_ratio", 0.5, 3.0)


def test_drp_avg_lap_seconds_plausible():
    df = load("intermediate", "driver_race_performance").filter(pl.col("avg_lap_seconds").is_not_null())
    # Outlier laps from incidents propagate into the per-driver average.
    assert_in_range(df, "avg_lap_seconds", 60.0, 800.0)
