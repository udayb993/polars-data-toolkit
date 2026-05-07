"""Tests for marts.pace_evolution."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_in_range, load


def test_pace_evolution_n_laps_positive():
    df = load("marts", "pace_evolution")
    assert df.filter(pl.col("n_laps") <= 0).height == 0


def test_pace_evolution_ratios_positive():
    df = load("marts", "pace_evolution")
    assert_in_range(df, "avg_lap_ratio", 0.7, 3.0)
    assert_in_range(df, "median_lap_ratio", 0.7, 3.0)


def test_pace_evolution_sorted_per_driver():
    df = load("marts", "pace_evolution").sort(["season", "driver_id", "race_date"])
    diffs = df.with_columns(pl.col("race_date").diff().over(["season", "driver_id"]).alias("d"))
    bad = diffs.filter(pl.col("d").dt.total_days() < 0)
    assert bad.height == 0
