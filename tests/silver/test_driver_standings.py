"""Tests for silver.driver_standings."""
from __future__ import annotations

import polars as pl

from tests._helpers import (
    assert_columns_dtype,
    assert_in_range,
    assert_no_duplicate_keys,
    assert_no_nulls,
    load,
)


def test_driver_standings_min_rows():
    df = load("silver", "driver_standings")
    assert df.height >= 20


def test_driver_standings_primary_key_unique():
    df = load("silver", "driver_standings")
    assert_no_duplicate_keys(df, ["season", "driver_id"])


def test_driver_standings_dtypes():
    df = load("silver", "driver_standings")
    assert_columns_dtype(df, {
        "season":         pl.Int32,
        "final_round":    pl.Int32,
        "driver_id":      pl.Utf8,
        "final_position": pl.Int32,
        "final_points":   pl.Float64,
        "season_wins":    pl.Int32,
    })


def test_driver_standings_no_nulls():
    df = load("silver", "driver_standings")
    assert_no_nulls(df, ["season", "driver_id", "final_position", "final_points"])


def test_driver_standings_position_unique_per_season():
    df = load("silver", "driver_standings")
    assert_no_duplicate_keys(df, ["season", "final_position"])


def test_driver_standings_points_non_negative():
    df = load("silver", "driver_standings")
    assert_in_range(df, "final_points", 0.0, 1000.0)


def test_driver_standings_wins_capped_by_round():
    df = load("silver", "driver_standings")
    bad = df.filter(pl.col("season_wins") > pl.col("final_round"))
    assert bad.height == 0, f"{bad.height} drivers with more wins than rounds"
