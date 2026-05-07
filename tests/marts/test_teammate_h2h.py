"""Tests for marts.teammate_h2h."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_in_range, assert_no_duplicate_keys, load


def test_h2h_primary_key_unique():
    df = load("marts", "teammate_h2h")
    assert_no_duplicate_keys(df, ["season", "constructor_id", "driver_a", "driver_b"])


def test_h2h_a_lt_b_enforced():
    df = load("marts", "teammate_h2h")
    assert df.filter(pl.col("driver_a") >= pl.col("driver_b")).height == 0


def test_h2h_win_rate_in_unit_interval():
    df = load("marts", "teammate_h2h")
    assert_in_range(df, "a_win_rate", 0.0, 1.0)


def test_h2h_wins_sum_le_compared():
    df = load("marts", "teammate_h2h")
    bad = df.filter((pl.col("a_wins") + pl.col("b_wins")) > pl.col("races_compared"))
    assert bad.height == 0
