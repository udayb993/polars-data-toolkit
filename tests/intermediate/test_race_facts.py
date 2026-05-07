"""Tests for intermediate.race_facts."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_no_duplicate_keys, assert_no_nulls, load


def test_race_facts_one_row_per_race():
    df = load("intermediate", "race_facts")
    assert_no_duplicate_keys(df, ["race_id"])


def test_race_facts_matches_silver_races():
    rf = load("intermediate", "race_facts")
    races = load("silver", "races")
    assert rf.height == races.height


def test_race_facts_no_nulls_on_keys():
    df = load("intermediate", "race_facts")
    assert_no_nulls(df, ["race_id", "season", "round", "circuit_id"])


def test_race_facts_winner_is_known_driver():
    rf = load("intermediate", "race_facts")
    drivers = load("silver", "drivers")
    bad = (
        rf.filter(pl.col("winner_driver_id").is_not_null())
        .join(drivers.select("driver_id"), left_on="winner_driver_id", right_on="driver_id", how="anti")
    )
    assert bad.height == 0


def test_race_facts_n_starters_positive():
    df = load("intermediate", "race_facts")
    assert df.filter(pl.col("n_starters") <= 0).height == 0


def test_race_facts_dnfs_le_starters():
    df = load("intermediate", "race_facts")
    bad = df.filter(pl.col("n_dnfs") > pl.col("n_starters"))
    assert bad.height == 0
