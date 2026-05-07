"""Tests for silver.constructor_standings."""
from __future__ import annotations

import polars as pl

from tests._helpers import (
    assert_columns_dtype,
    assert_in_range,
    assert_no_duplicate_keys,
    assert_no_nulls,
    load,
)


def test_constructor_standings_min_rows():
    df = load("silver", "constructor_standings")
    assert df.height >= 10


def test_constructor_standings_primary_key_unique():
    df = load("silver", "constructor_standings")
    assert_no_duplicate_keys(df, ["season", "constructor_id"])


def test_constructor_standings_dtypes():
    df = load("silver", "constructor_standings")
    assert_columns_dtype(df, {
        "season":         pl.Int32,
        "constructor_id": pl.Utf8,
        "final_position": pl.Int32,
        "final_points":   pl.Float64,
        "season_wins":    pl.Int32,
    })


def test_constructor_standings_position_unique_per_season():
    df = load("silver", "constructor_standings")
    assert_no_duplicate_keys(df, ["season", "final_position"])


def test_constructor_standings_no_nulls():
    df = load("silver", "constructor_standings")
    assert_no_nulls(df, ["season", "constructor_id", "final_position", "final_points"])


def test_constructor_standings_points_in_range():
    df = load("silver", "constructor_standings")
    # Two cars × ~26 max per race × 24 races ≈ ~1250 absolute ceiling.
    assert_in_range(df, "final_points", 0.0, 1500.0)
