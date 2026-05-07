"""Tests for marts.season_summary."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_no_duplicate_keys, load


def test_season_summary_primary_key_unique():
    df = load("marts", "season_summary")
    assert_no_duplicate_keys(df, ["season"])


def test_season_summary_one_row_per_season_in_silver():
    df = load("marts", "season_summary")
    expected = set(load("silver", "seasons")["season"].to_list())
    seen = set(df["season"].to_list())
    assert seen == expected, f"missing/extra seasons: {seen ^ expected}"


def test_season_summary_margins_non_negative():
    df = load("marts", "season_summary")
    assert df.filter(pl.col("driver_title_margin") < 0).height == 0
    assert df.filter(pl.col("constructor_title_margin") < 0).height == 0


def test_season_summary_n_distinct_winners_le_n_races():
    df = load("marts", "season_summary")
    assert df.filter(pl.col("n_distinct_winners") > pl.col("n_races")).height == 0
