"""Tests for intermediate.championship_state."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_no_duplicate_keys, load


def test_cs_primary_key_unique():
    df = load("intermediate", "championship_state")
    # One row per (season, race, driver).
    assert_no_duplicate_keys(df, ["season", "race_id", "driver_id"])


def test_cs_cumulative_points_monotonic():
    df = load("intermediate", "championship_state").sort(["season", "driver_id", "race_date"])
    diffs = df.with_columns(
        pl.col("cumulative_points").diff().over(["season", "driver_id"]).alias("d")
    )
    assert diffs.filter(pl.col("d") < 0).height == 0


def test_cs_standing_starts_at_one():
    df = load("intermediate", "championship_state")
    # Per (season, race) standings should be 1..N with no gaps.
    grp = df.group_by(["season", "race_id"]).agg(
        pl.col("standing_after_race").min().alias("min_s"),
        pl.col("standing_after_race").max().alias("max_s"),
        pl.col("standing_after_race").n_unique().alias("n_unique"),
        pl.len().alias("n"),
    )
    bad = grp.filter((pl.col("min_s") != 1) | (pl.col("max_s") != pl.col("n_unique")))
    assert bad.height == 0


def test_cs_gap_to_leader_non_negative():
    df = load("intermediate", "championship_state")
    assert df.filter(pl.col("gap_to_leader") < 0).height == 0
