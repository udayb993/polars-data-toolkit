"""Tests for silver.lap_times."""
from __future__ import annotations

import polars as pl

from tests._helpers import (
    assert_columns_dtype,
    assert_in_range,
    assert_no_duplicate_keys,
    assert_no_nulls,
    load,
)


def test_lap_times_min_rows():
    df = load("silver", "lap_times")
    assert df.height >= 5_000


def test_lap_times_primary_key_unique():
    df = load("silver", "lap_times")
    assert_no_duplicate_keys(df, ["race_id", "driver_id", "lap"])


def test_lap_times_dtypes():
    df = load("silver", "lap_times")
    assert_columns_dtype(df, {
        "race_id":         pl.Utf8,
        "driver_id":       pl.Utf8,
        "lap":             pl.Int32,
        "position_at_lap": pl.Int32,
        "lap_time":        pl.Duration("us"),
    })


def test_lap_times_no_nulls():
    df = load("silver", "lap_times")
    assert_no_nulls(df, ["race_id", "driver_id", "lap", "lap_time"])


def test_lap_times_lap_in_range():
    df = load("silver", "lap_times")
    assert_in_range(df, "lap", 1, 100)


def test_lap_times_position_in_range():
    df = load("silver", "lap_times")
    assert_in_range(df, "position_at_lap", 1, 30)


def test_lap_times_median_duration_plausible():
    """Median lap should land in the typical F1 range — outliers (red flags,
    safety cars, very long Spa laps) are expected at the tails."""
    df = load("silver", "lap_times")
    median_s = df.select(
        (pl.col("lap_time").dt.total_milliseconds().median() / 1000.0).alias("m")
    ).item()
    assert 60.0 <= median_s <= 130.0, f"median lap {median_s:.1f}s outside [60, 130]"


def test_lap_times_p99_duration_bounded():
    df = load("silver", "lap_times")
    p99 = df.select(
        (pl.col("lap_time").dt.total_milliseconds().quantile(0.99) / 1000.0).alias("p")
    ).item()
    # Even with safety-car restarts and red flags, 99th percentile should be < 6 min.
    assert p99 <= 360.0, f"p99 lap_time {p99:.1f}s exceeds 360s"


def test_lap_times_starts_at_one_per_driver():
    """Per (race_id, driver_id), the lap numbers begin at 1.
    Note: contiguity is NOT guaranteed — Ergast occasionally drops laps when
    timing data is corrupt during incidents."""
    df = load("silver", "lap_times")
    grouped = df.group_by(["race_id", "driver_id"]).agg(
        pl.col("lap").min().alias("min_lap"),
    )
    bad = grouped.filter(pl.col("min_lap") != 1)
    # A small number of drivers may legitimately miss lap 1 if data was lost.
    assert bad.height < 5, f"too many drivers without lap 1: {bad.height}"
