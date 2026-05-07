"""Tests for intermediate.lap_pace_normalized."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_in_range, assert_no_duplicate_keys, load


def test_lpn_primary_key_unique():
    df = load("intermediate", "lap_pace_normalized")
    assert_no_duplicate_keys(df, ["race_id", "driver_id", "lap"])


def test_lpn_row_count_matches_lap_times():
    lpn = load("intermediate", "lap_pace_normalized")
    laps = load("silver", "lap_times")
    assert lpn.height == laps.height


def test_lpn_baseline_present_per_race():
    df = load("intermediate", "lap_pace_normalized")
    null_baseline = df.filter(pl.col("baseline_lap_time").is_null())
    assert null_baseline.height == 0, "every lap should have a baseline"


def test_lpn_ratio_positive():
    df = load("intermediate", "lap_pace_normalized").filter(pl.col("lap_time_ratio").is_not_null())
    # Outlier raw lap_times (red flags / safety car restarts) inflate the ratio.
    assert_in_range(df, "lap_time_ratio", 0.5, 50.0)
