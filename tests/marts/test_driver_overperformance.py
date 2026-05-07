"""Tests for marts.driver_overperformance."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_no_duplicate_keys, load


def test_overperf_primary_key_unique():
    df = load("marts", "driver_overperformance")
    assert_no_duplicate_keys(df, ["season", "driver_id"])


def test_overperf_rank_dense_per_season():
    df = load("marts", "driver_overperformance")
    grp = df.group_by("season").agg(
        pl.col("season_rank").min().alias("mn"),
        pl.len().alias("n"),
        pl.col("season_rank").max().alias("mx"),
    )
    assert grp.filter((pl.col("mn") != 1) | (pl.col("mx") > pl.col("n"))).height == 0


def test_overperf_total_overperf_eq_points_minus_expected():
    df = load("marts", "driver_overperformance")
    bad = df.filter(
        ((pl.col("total_points") - pl.col("total_expected_points")) - pl.col("total_overperformance")).abs() > 1e-6
    )
    assert bad.height == 0
