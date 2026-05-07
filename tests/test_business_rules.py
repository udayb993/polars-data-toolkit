"""Business-rule assertions on intermediate + marts."""
from __future__ import annotations

import polars as pl

from common.io import read


def test_race_facts_one_row_per_race():
    df = read("intermediate", "race_facts")
    assert df.select("race_id").n_unique() == df.height
    # Every race has at least 1 starter.
    assert df.filter(pl.col("n_starters").is_null() | (pl.col("n_starters") < 1)).height == 0


def test_championship_state_monotonic_per_driver():
    df = read("intermediate", "championship_state").sort(["season", "driver_id", "race_date"])
    diffs = df.with_columns(
        pl.col("cumulative_points").diff().over(["season", "driver_id"]).alias("d")
    )
    assert diffs.filter(pl.col("d") < 0).height == 0, "cumulative points decreased"


def test_driver_form_rolling_in_range():
    df = read("intermediate", "driver_form")
    assert df.filter(
        (pl.col("podium_rate_5r") < 0) | (pl.col("podium_rate_5r") > 1)
    ).height == 0


def test_teammate_h2h_pair_uniqueness():
    df = read("marts", "teammate_h2h")
    keys = ["season", "constructor_id", "driver_a", "driver_b"]
    assert df.select(keys).n_unique() == df.height
    # a < b enforced.
    assert df.filter(pl.col("driver_a") >= pl.col("driver_b")).height == 0


def test_season_summary_champion_has_most_points():
    summary = read("marts", "season_summary")
    standings = read("silver", "driver_standings")
    for season, champion_id, champion_pts in summary.select(
        "season", "champion_driver_id", "champion_points"
    ).iter_rows():
        max_pts = (
            standings.filter(pl.col("season") == season).select(pl.col("final_points").max()).item()
        )
        assert champion_pts == max_pts, f"season {season} champion mismatch"


def test_dnf_analysis_reliability_in_range():
    df = read("marts", "dnf_analysis")
    bad = df.filter((pl.col("reliability") < 0) | (pl.col("reliability") > 1))
    assert bad.height == 0
