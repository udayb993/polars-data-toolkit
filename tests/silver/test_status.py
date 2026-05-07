"""Tests for silver.status (DNF reason reference + categorisation)."""
from __future__ import annotations

import polars as pl

from silver.status import DNF_CATEGORIES
from tests._helpers import (
    assert_columns_dtype,
    assert_in_range,
    assert_no_duplicate_keys,
    assert_no_nulls,
    assert_values_subset,
    load,
)

ALLOWED_CATEGORIES = {"finished", "lapped", "mechanical", "accident", "disqualified", "other"}


def test_status_min_rows():
    df = load("silver", "status")
    assert df.height >= 50  # Ergast historical status table is ~130 rows


def test_status_primary_key_unique():
    df = load("silver", "status")
    assert_no_duplicate_keys(df, ["status_id"])


def test_status_dtypes():
    df = load("silver", "status")
    assert_columns_dtype(df, {
        "status_id":        pl.Int32,
        "status":           pl.Utf8,
        "historical_count": pl.Int64,
        "status_category":  DNF_CATEGORIES,
    })


def test_status_no_nulls():
    df = load("silver", "status")
    assert_no_nulls(df, ["status_id", "status", "status_category", "historical_count"])


def test_status_category_values_constrained():
    df = load("silver", "status")
    # Cast Enum → Utf8 to compare as plain strings.
    cats = df.with_columns(pl.col("status_category").cast(pl.Utf8))
    assert_values_subset(cats, "status_category", ALLOWED_CATEGORIES)


def test_status_finished_categorised_as_finished():
    df = load("silver", "status").with_columns(pl.col("status_category").cast(pl.Utf8))
    finished_row = df.filter(pl.col("status").str.to_lowercase() == "finished")
    assert finished_row.height == 1
    assert finished_row["status_category"][0] == "finished"


def test_status_lapped_categorised_as_lapped():
    df = load("silver", "status").with_columns(pl.col("status_category").cast(pl.Utf8))
    lapped = df.filter(pl.col("status").str.contains(r"\+\d+ Lap"))
    if lapped.height:
        cats = set(lapped["status_category"].to_list())
        assert cats == {"lapped"}, f"+N Lap rows mis-categorised: {cats}"


def test_status_historical_count_non_negative():
    df = load("silver", "status")
    assert_in_range(df, "historical_count", 0, 10**9, allow_null=False)
