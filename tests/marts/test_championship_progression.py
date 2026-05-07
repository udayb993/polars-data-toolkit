"""Tests for marts.championship_progression."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_no_duplicate_keys, load


def test_progression_primary_key_unique():
    df = load("marts", "championship_progression")
    assert_no_duplicate_keys(df, ["season", "race_id", "driver_id"])


def test_progression_eliminated_only_when_gap_too_large():
    df = load("marts", "championship_progression")
    # If marked eliminated, gap must exceed remaining-rounds × max_per_round (34).
    bad = df.filter(
        pl.col("mathematically_eliminated")
        & (pl.col("gap_to_leader") <= pl.col("rounds_remaining").cast(pl.Float64) * 34.0)
    )
    assert bad.height == 0


def test_progression_champion_never_eliminated():
    df = load("marts", "championship_progression")
    leaders = df.filter(pl.col("standing_after_race") == 1)
    assert leaders.filter(pl.col("mathematically_eliminated")).height == 0


def test_progression_position_change_consistency():
    df = load("marts", "championship_progression").sort(["season", "driver_id", "race_date"])
    # First race per driver should have null position_change_vs_prev_race.
    firsts = df.group_by(["season", "driver_id"]).agg(pl.col("race_date").min().alias("first_date"))
    df2 = df.join(firsts, on=["season", "driver_id"])
    bad = df2.filter(
        (pl.col("race_date") == pl.col("first_date"))
        & pl.col("position_change_vs_prev_race").is_not_null()
    )
    assert bad.height == 0
