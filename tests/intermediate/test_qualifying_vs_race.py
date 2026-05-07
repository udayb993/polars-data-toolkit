"""Tests for intermediate.qualifying_vs_race."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_in_range, assert_no_duplicate_keys, load


def test_qvr_primary_key_unique():
    df = load("intermediate", "qualifying_vs_race")
    assert_no_duplicate_keys(df, ["race_id", "driver_id"])


def test_qvr_expected_points_non_negative():
    df = load("intermediate", "qualifying_vs_race")
    assert_in_range(df, "expected_points", 0.0, 30.0, allow_null=False)


def test_qvr_overperformance_arithmetic():
    df = load("intermediate", "qualifying_vs_race").filter(pl.col("points").is_not_null())
    bad = df.filter(pl.col("points_overperformance") != (pl.col("points") - pl.col("expected_points")))
    assert bad.height == 0
