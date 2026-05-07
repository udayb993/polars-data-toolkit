"""Tests for silver.races."""
from __future__ import annotations

import polars as pl

from tests._helpers import (
    assert_columns_dtype,
    assert_in_range,
    assert_no_duplicate_keys,
    assert_no_nulls,
    load,
)


def _seasons_in_data() -> set[int]:
    return set(load("silver", "seasons")["season"].to_list())


def test_races_min_rows():
    df = load("silver", "races")
    # ~22 races per season.
    assert df.height >= 20 * len(_seasons_in_data())


def test_races_primary_key_unique():
    df = load("silver", "races")
    assert_no_duplicate_keys(df, ["race_id"])
    # Also (season, round) should be unique.
    assert_no_duplicate_keys(df, ["season", "round"])


def test_races_dtypes():
    df = load("silver", "races")
    assert_columns_dtype(df, {
        "season":     pl.Int32,
        "round":      pl.Int32,
        "race_id":    pl.Utf8,
        "race_name":  pl.Utf8,
        "circuit_id": pl.Utf8,
        "race_date":  pl.Date,
    })


def test_races_no_nulls():
    df = load("silver", "races")
    assert_no_nulls(df, ["race_id", "season", "round", "race_date", "circuit_id"])


def test_races_round_in_range():
    df = load("silver", "races")
    # F1 seasons have between 16 and 24 rounds historically.
    assert_in_range(df, "round", 1, 30, allow_null=False)


def test_races_season_in_config():
    df = load("silver", "races")
    seen = set(df["season"].unique().to_list())
    expected = _seasons_in_data()
    assert seen <= expected, f"unexpected seasons: {seen - expected}"


def test_races_race_id_format():
    df = load("silver", "races")
    bad = df.filter(~pl.col("race_id").str.contains(r"^\d{4}_\d{2}$"))
    assert bad.height == 0, f"bad race_id format: {bad['race_id'].to_list()}"


def test_races_race_id_matches_season_round():
    df = load("silver", "races").with_columns(
        (pl.col("season").cast(pl.Utf8) + "_" + pl.col("round").cast(pl.Utf8).str.zfill(2)).alias("expected")
    )
    bad = df.filter(pl.col("race_id") != pl.col("expected"))
    assert bad.height == 0, "race_id does not match season_round"
