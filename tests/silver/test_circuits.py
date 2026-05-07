"""Tests for silver.circuits."""
from __future__ import annotations

import polars as pl

from tests._helpers import (
    assert_columns_dtype,
    assert_in_range,
    assert_no_duplicate_keys,
    assert_no_nulls,
    load,
)


def test_circuits_min_rows():
    df = load("silver", "circuits")
    assert df.height >= 15, f"too few circuits: {df.height}"


def test_circuits_primary_key_unique():
    df = load("silver", "circuits")
    assert_no_duplicate_keys(df, ["circuit_id"])


def test_circuits_dtypes():
    df = load("silver", "circuits")
    assert_columns_dtype(df, {
        "circuit_id":   pl.Utf8,
        "circuit_name": pl.Utf8,
        "country":      pl.Utf8,
        "city":         pl.Utf8,
        "lat":          pl.Float64,
        "lon":          pl.Float64,
    })


def test_circuits_no_critical_nulls():
    df = load("silver", "circuits")
    assert_no_nulls(df, ["circuit_id", "circuit_name", "country"])


def test_circuits_lat_lon_in_range():
    df = load("silver", "circuits")
    assert_in_range(df, "lat", -90.0, 90.0)
    assert_in_range(df, "lon", -180.0, 180.0)


def test_circuits_id_kebab_or_snake():
    df = load("silver", "circuits")
    bad = df.filter(~pl.col("circuit_id").str.contains(r"^[a-z0-9_]+$"))
    assert bad.height == 0, f"non-snake_case circuit_ids: {bad['circuit_id'].to_list()}"
