"""Tests for silver.pit_stops."""
from __future__ import annotations

import polars as pl

from tests._helpers import (
    assert_columns_dtype,
    assert_in_range,
    assert_no_duplicate_keys,
    assert_no_nulls,
    load,
)


def test_pit_stops_min_rows():
    df = load("silver", "pit_stops")
    assert df.height >= 200


def test_pit_stops_primary_key_unique():
    df = load("silver", "pit_stops")
    assert_no_duplicate_keys(df, ["race_id", "driver_id", "stop_number"])


def test_pit_stops_dtypes():
    df = load("silver", "pit_stops")
    assert_columns_dtype(df, {
        "race_id":       pl.Utf8,
        "driver_id":     pl.Utf8,
        "stop_number":   pl.Int32,
        "lap":           pl.Int32,
        "stop_duration": pl.Duration("us"),
    })


def test_pit_stops_no_nulls_on_keys():
    # stop_duration is nullable: Ergast occasionally lacks the duration field.
    df = load("silver", "pit_stops")
    assert_no_nulls(df, ["race_id", "driver_id", "stop_number", "lap"])


def test_pit_stops_stop_number_starts_at_one():
    df = load("silver", "pit_stops")
    bad = df.filter(pl.col("stop_number") < 1)
    assert bad.height == 0


def test_pit_stops_per_driver_sequence_dense():
    """For every (race_id, driver_id), stop_number should be 1..N with no gaps."""
    df = load("silver", "pit_stops")
    grouped = df.group_by(["race_id", "driver_id"]).agg(
        pl.col("stop_number").max().alias("max_n"),
        pl.col("stop_number").n_unique().alias("n_unique"),
    )
    bad = grouped.filter(pl.col("max_n") != pl.col("n_unique"))
    assert bad.height == 0, f"{bad.height} drivers with non-dense stop sequences"


def test_pit_stops_lap_in_range():
    df = load("silver", "pit_stops")
    assert_in_range(df, "lap", 1, 100)


def test_pit_stops_duration_plausible():
    df = load("silver", "pit_stops").filter(pl.col("stop_duration").is_not_null())
    secs = df.with_columns(
        (pl.col("stop_duration").dt.total_milliseconds() / 1000.0).alias("s")
    )
    # Stationary time + drive-through varies a lot; cap generously.
    assert_in_range(secs, "s", 1.0, 120.0, allow_null=False)
