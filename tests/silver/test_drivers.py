"""Tests for silver.drivers."""
from __future__ import annotations

import datetime as dt

import polars as pl

from tests._helpers import (
    assert_columns_dtype,
    assert_in_range,
    assert_no_duplicate_keys,
    assert_no_nulls,
    load,
)


def test_drivers_min_rows():
    df = load("silver", "drivers")
    # ~22 unique drivers per season; 3 seasons usually 25–30 distinct.
    assert df.height >= 20, f"too few drivers: {df.height}"


def test_drivers_primary_key_unique():
    df = load("silver", "drivers")
    assert_no_duplicate_keys(df, ["driver_id"])


def test_drivers_dtypes():
    df = load("silver", "drivers")
    assert_columns_dtype(df, {
        "driver_id":        pl.Utf8,
        "permanent_number": pl.Int32,
        "given_name":       pl.Utf8,
        "family_name":      pl.Utf8,
        "full_name":        pl.Utf8,
        "date_of_birth":    pl.Date,
        "nationality":      pl.Utf8,
    })


def test_drivers_no_critical_nulls():
    df = load("silver", "drivers")
    assert_no_nulls(df, ["driver_id", "given_name", "family_name", "full_name", "nationality"])


def test_drivers_full_name_concatenation():
    df = load("silver", "drivers")
    bad = df.filter(pl.col("full_name") != pl.col("given_name") + " " + pl.col("family_name"))
    assert bad.height == 0, f"full_name != given + family for {bad.height} rows"


def test_drivers_dob_plausible():
    df = load("silver", "drivers")
    today = dt.date.today()
    # F1 drivers are realistically 17–60 years old.
    df_ages = df.with_columns(
        ((pl.lit(today) - pl.col("date_of_birth")).dt.total_days() / 365.25).alias("age")
    )
    assert_in_range(df_ages, "age", 17.0, 60.0)


def test_drivers_permanent_number_in_range():
    df = load("silver", "drivers").filter(pl.col("permanent_number").is_not_null())
    # F1 permanent numbers historically 1..99.
    assert_in_range(df, "permanent_number", 1, 99, allow_null=False)


def test_drivers_code_three_uppercase_when_present():
    df = load("silver", "drivers").filter(pl.col("driver_code").is_not_null())
    bad = df.filter(~pl.col("driver_code").str.contains(r"^[A-Z]{3}$"))
    assert bad.height == 0, f"bad driver_code values: {bad['driver_code'].to_list()}"
