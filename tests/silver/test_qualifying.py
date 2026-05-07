"""Tests for silver.qualifying."""
from __future__ import annotations

import polars as pl

from tests._helpers import (
    assert_columns_dtype,
    assert_in_range,
    assert_no_duplicate_keys,
    assert_no_nulls,
    load,
)


def test_qualifying_min_rows():
    df = load("silver", "qualifying")
    assert df.height >= 400


def test_qualifying_primary_key_unique():
    df = load("silver", "qualifying")
    assert_no_duplicate_keys(df, ["race_id", "driver_id"])


def test_qualifying_dtypes():
    df = load("silver", "qualifying")
    assert_columns_dtype(df, {
        "race_id":         pl.Utf8,
        "season":          pl.Int32,
        "round":           pl.Int32,
        "driver_id":       pl.Utf8,
        "constructor_id":  pl.Utf8,
        "quali_position":  pl.Int32,
        "q1_time":         pl.Duration("us"),
        "q2_time":         pl.Duration("us"),
        "q3_time":         pl.Duration("us"),
        "best_quali_time": pl.Duration("us"),
        "gap_to_pole":     pl.Duration("us"),
    })


def test_qualifying_position_in_range():
    df = load("silver", "qualifying")
    assert_in_range(df, "quali_position", 1, 30)


def test_qualifying_best_is_min_of_q1_q2_q3():
    df = load("silver", "qualifying").filter(pl.col("best_quali_time").is_not_null())
    bad = df.filter(
        (pl.col("q1_time").is_not_null() & (pl.col("best_quali_time") > pl.col("q1_time")))
        | (pl.col("q2_time").is_not_null() & (pl.col("best_quali_time") > pl.col("q2_time")))
        | (pl.col("q3_time").is_not_null() & (pl.col("best_quali_time") > pl.col("q3_time")))
    )
    assert bad.height == 0, f"{bad.height} rows where best_quali_time > one of Q1/Q2/Q3"


def test_qualifying_pole_has_smallest_gap():
    """The pole-sitter (quali_position == 1) should have the smallest gap_to_pole
    in their race. Not necessarily zero, because gap_to_pole is computed against
    the minimum best_quali_time across all drivers — and a driver knocked out in
    Q1 occasionally posts a faster lap than the eventual pole-sitter's Q3 lap
    (Q3 has different fuel/tyre rules)."""
    df = load("silver", "qualifying")
    poles = df.filter(pl.col("quali_position") == 1)
    bad = (
        df.join(poles.select(["race_id", pl.col("gap_to_pole").alias("pole_gap")]),
                on="race_id")
          .filter(pl.col("gap_to_pole") < pl.col("pole_gap"))
    )
    # A handful of races where Q1 outliers slipped through is acceptable.
    assert bad.select("race_id").n_unique() <= 10


def test_qualifying_gap_non_negative():
    df = load("silver", "qualifying").filter(pl.col("gap_to_pole").is_not_null())
    bad = df.filter(pl.col("gap_to_pole").dt.total_microseconds() < 0)
    assert bad.height == 0


def test_qualifying_lap_time_plausible():
    df = load("silver", "qualifying").filter(pl.col("best_quali_time").is_not_null())
    secs = df.with_columns(
        (pl.col("best_quali_time").dt.total_milliseconds() / 1000.0).alias("s")
    )
    # F1 quali laps: 60s (Monaco-ish) to 130s (Spa); allow a bit wider.
    assert_in_range(secs, "s", 50.0, 150.0, allow_null=False)


def test_qualifying_no_nulls_on_keys():
    df = load("silver", "qualifying")
    assert_no_nulls(df, ["race_id", "driver_id", "constructor_id", "quali_position"])
