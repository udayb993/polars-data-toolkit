"""Tests for silver.constructors."""
from __future__ import annotations

import polars as pl

from tests._helpers import (
    assert_columns_dtype,
    assert_no_duplicate_keys,
    assert_no_nulls,
    load,
)


def test_constructors_min_rows():
    df = load("silver", "constructors")
    # 10 teams per season; typically 10–12 distinct across 3 seasons.
    assert df.height >= 10, f"too few constructors: {df.height}"


def test_constructors_primary_key_unique():
    df = load("silver", "constructors")
    assert_no_duplicate_keys(df, ["constructor_id"])


def test_constructors_dtypes():
    df = load("silver", "constructors")
    assert_columns_dtype(df, {
        "constructor_id":   pl.Utf8,
        "constructor_name": pl.Utf8,
        "nationality":      pl.Utf8,
    })


def test_constructors_no_critical_nulls():
    df = load("silver", "constructors")
    assert_no_nulls(df, ["constructor_id", "constructor_name", "nationality"])


def test_constructors_id_format():
    df = load("silver", "constructors")
    bad = df.filter(~pl.col("constructor_id").str.contains(r"^[a-z0-9_]+$"))
    assert bad.height == 0, f"non-snake_case constructor_ids: {bad['constructor_id'].to_list()}"
