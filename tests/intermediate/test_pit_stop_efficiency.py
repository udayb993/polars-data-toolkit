"""Tests for intermediate.pit_stop_efficiency."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_in_range, assert_no_duplicate_keys, load


def test_pse_row_count_matches_pit_stops():
    pse = load("intermediate", "pit_stop_efficiency")
    pits = load("silver", "pit_stops")
    assert pse.height == pits.height


def test_pse_primary_key_unique():
    df = load("intermediate", "pit_stop_efficiency")
    assert_no_duplicate_keys(df, ["race_id", "driver_id", "stop_number"])


def test_pse_circuit_percentile_in_unit_interval():
    df = load("intermediate", "pit_stop_efficiency").filter(pl.col("circuit_percentile").is_not_null())
    assert_in_range(df, "circuit_percentile", 0.0, 1.0, allow_null=False)


def test_pse_rank_in_race_starts_at_one():
    df = load("intermediate", "pit_stop_efficiency")
    assert df.filter(pl.col("rank_in_race") < 1).height == 0
