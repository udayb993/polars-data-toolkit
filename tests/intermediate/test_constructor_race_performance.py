"""Tests for intermediate.constructor_race_performance."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_in_range, assert_no_duplicate_keys, load


def test_crp_primary_key_unique():
    df = load("intermediate", "constructor_race_performance")
    assert_no_duplicate_keys(df, ["race_id", "constructor_id"])


def test_crp_n_cars_positive():
    df = load("intermediate", "constructor_race_performance")
    assert df.filter(pl.col("n_cars") <= 0).height == 0
    # F1 teams have at most 2 cars.
    assert_in_range(df, "n_cars", 1, 2, allow_null=False)


def test_crp_dnfs_le_n_cars():
    df = load("intermediate", "constructor_race_performance")
    bad = df.filter(pl.col("n_dnfs") > pl.col("n_cars"))
    assert bad.height == 0


def test_crp_constructor_points_non_negative():
    df = load("intermediate", "constructor_race_performance")
    assert df.filter(pl.col("constructor_points") < 0).height == 0
