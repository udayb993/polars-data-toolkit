"""Tests for intermediate.driver_form."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_in_range, assert_no_duplicate_keys, load


def test_driver_form_primary_key_unique():
    df = load("intermediate", "driver_form")
    assert_no_duplicate_keys(df, ["race_id", "driver_id"])


def test_driver_form_rates_in_unit_interval():
    df = load("intermediate", "driver_form")
    assert_in_range(df, "podium_rate_5r", 0.0, 1.0)
    assert_in_range(df, "dnf_rate_5r", 0.0, 1.0)


def test_driver_form_avg_finish_in_range():
    df = load("intermediate", "driver_form")
    assert_in_range(df, "avg_finish_5r", 1.0, 30.0)


def test_driver_form_races_to_date_monotonic():
    df = load("intermediate", "driver_form").sort(["driver_id", "race_date"])
    diffs = df.with_columns(pl.col("races_to_date").diff().over("driver_id").alias("d"))
    assert diffs.filter(pl.col("d") < 0).height == 0
