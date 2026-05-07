"""Tests for silver.results."""
from __future__ import annotations

import polars as pl

from tests._helpers import (
    assert_columns_dtype,
    assert_in_range,
    assert_no_duplicate_keys,
    assert_no_nulls,
    load,
)


def test_results_min_rows():
    df = load("silver", "results")
    # 20 cars × 22 races × 3 seasons ≈ 1320.
    assert df.height >= 400


def test_results_primary_key_unique():
    df = load("silver", "results")
    assert_no_duplicate_keys(df, ["race_id", "driver_id"])


def test_results_dtypes():
    df = load("silver", "results")
    assert_columns_dtype(df, {
        "race_id":         pl.Utf8,
        "season":          pl.Int32,
        "round":           pl.Int32,
        "race_date":       pl.Date,
        "driver_id":       pl.Utf8,
        "constructor_id":  pl.Utf8,
        "grid_position":   pl.Int32,
        "finish_position": pl.Int32,
        "points":          pl.Float64,
        "laps_completed":  pl.Int32,
        "finished_flag":   pl.Boolean,
        "race_time":       pl.Duration("us"),
        "fastest_lap_time": pl.Duration("us"),
        "fastest_lap_kph": pl.Float64,
    })


def test_results_no_nulls_on_keys():
    df = load("silver", "results")
    assert_no_nulls(df, ["race_id", "driver_id", "constructor_id", "season", "round"])


def test_results_grid_position_in_range():
    df = load("silver", "results")
    # 0 = pit-lane start; up to 26 grid slots historically.
    assert_in_range(df, "grid_position", 0, 30)


def test_results_finish_position_in_range():
    df = load("silver", "results")
    assert_in_range(df, "finish_position", 1, 30)


def test_results_points_non_negative_and_capped():
    df = load("silver", "results")
    # Max possible: 25 (win) + 1 (FL) = 26 per race.
    assert_in_range(df, "points", 0.0, 26.0)


def test_results_laps_completed_non_negative():
    df = load("silver", "results")
    assert_in_range(df, "laps_completed", 0, 100)


def test_results_winner_finished_with_position_1():
    df = load("silver", "results")
    winners = df.filter(pl.col("finish_position") == 1)
    # One winner per race, all finished.
    n_races = df.select("race_id").n_unique()
    assert winners.height == n_races, f"{winners.height} winners vs {n_races} races"
    assert winners.filter(~pl.col("finished_flag")).height == 0


def test_results_finished_flag_consistency():
    df = load("silver", "results")
    # If flag True, status must equal "Finished" (case-insensitive).
    bad = df.filter(pl.col("finished_flag") & (pl.col("finish_status").str.to_lowercase() != "finished"))
    assert bad.height == 0


def test_results_fastest_lap_kph_plausible():
    df = load("silver", "results").filter(pl.col("fastest_lap_kph").is_not_null())
    assert_in_range(df, "fastest_lap_kph", 100.0, 280.0)


def test_results_fk_to_drivers():
    res = load("silver", "results")
    drv = load("silver", "drivers")
    assert res.join(drv.select("driver_id"), on="driver_id", how="anti").height == 0


def test_results_fk_to_constructors():
    res = load("silver", "results")
    con = load("silver", "constructors")
    assert res.join(con.select("constructor_id"), on="constructor_id", how="anti").height == 0


def test_results_fk_to_races():
    res = load("silver", "results")
    rac = load("silver", "races")
    assert res.join(rac.select("race_id"), on="race_id", how="anti").height == 0
