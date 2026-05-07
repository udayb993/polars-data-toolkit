"""Tests for marts.pit_crew_ranking."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_no_duplicate_keys, load


def test_pcr_primary_key_unique():
    df = load("marts", "pit_crew_ranking")
    assert_no_duplicate_keys(df, ["season", "constructor_id"])


def test_pcr_p95_ge_median():
    df = load("marts", "pit_crew_ranking").filter(
        pl.col("median_stop_s").is_not_null() & pl.col("p95_stop_s").is_not_null()
    )
    bad = df.filter(pl.col("p95_stop_s") < pl.col("median_stop_s"))
    assert bad.height == 0


def test_pcr_rank_dense_per_season():
    df = load("marts", "pit_crew_ranking")
    grp = df.group_by("season").agg(
        pl.col("rank_in_season").min().alias("mn"),
        pl.col("rank_in_season").max().alias("mx"),
        pl.len().alias("n"),
    )
    # min should be 1; max should be ≤ n (ties allowed → can be < n).
    assert grp.filter((pl.col("mn") != 1) | (pl.col("mx") > pl.col("n"))).height == 0
