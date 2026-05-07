"""Tests for silver.seasons."""
from __future__ import annotations

import polars as pl

from tests._helpers import (
    assert_columns_dtype,
    assert_no_duplicate_keys,
    assert_no_nulls,
    load,
)


def test_seasons_at_least_one_row():
    df = load("silver", "seasons")
    assert df.height >= 1


def test_seasons_primary_key_unique():
    df = load("silver", "seasons")
    assert_no_duplicate_keys(df, ["season"])


def test_seasons_dtypes():
    df = load("silver", "seasons")
    assert_columns_dtype(df, {"season": pl.Int32, "url": pl.Utf8})


def test_seasons_values_plausible():
    df = load("silver", "seasons")
    seasons = df["season"].to_list()
    # F1 started in 1950; this project targets recent (2020+) but allow historical.
    assert all(1950 <= s <= 2100 for s in seasons), seasons


def test_seasons_no_nulls():
    df = load("silver", "seasons")
    assert_no_nulls(df, ["season"])
