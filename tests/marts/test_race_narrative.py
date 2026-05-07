"""Tests for marts.race_narrative."""
from __future__ import annotations

import polars as pl

from tests._helpers import assert_no_duplicate_keys, load


def test_narrative_one_row_per_race():
    df = load("marts", "race_narrative")
    assert_no_duplicate_keys(df, ["race_id"])
    assert df.height == load("silver", "races").height


def test_narrative_winner_and_pole_known_drivers():
    df = load("marts", "race_narrative")
    drivers = load("silver", "drivers").select("driver_id")
    for col in ("winner_driver_id", "pole_driver_id", "fastest_lap_driver_id",
                "biggest_mover_driver", "biggest_faller_driver"):
        bad = df.filter(pl.col(col).is_not_null()).join(
            drivers, left_on=col, right_on="driver_id", how="anti"
        )
        assert bad.height == 0, f"unknown driver in {col}"


def test_narrative_dnfs_le_starters():
    df = load("marts", "race_narrative")
    bad = df.filter(pl.col("n_dnfs") > pl.col("n_starters"))
    assert bad.height == 0
