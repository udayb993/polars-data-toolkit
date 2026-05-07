"""intermediate.championship_state — running standings after each race.

Combines race + sprint points, then ``cum_sum`` over (season, driver) ordered
by race_date.  Adds gap-to-leader and rank-after-race.

Practices: union of two facts, ``cum_sum``/``cum_count`` over partition,
``rank`` for live standings, leader self-join.
"""
from __future__ import annotations

import polars as pl

from common.io import path_for, scan, write


def _maybe_sprints() -> pl.LazyFrame:
    if not path_for("silver", "sprint_results").exists():
        return None  # type: ignore[return-value]
    s = scan("silver", "sprint_results")
    if s.collect_schema().len() == 0:
        return None  # type: ignore[return-value]
    return s.select("race_id", "season", "round", "race_date",
                    "driver_id", pl.col("sprint_points").alias("points"))


def build() -> pl.DataFrame:
    race_pts = scan("silver", "results").select(
        "race_id", "season", "round", "race_date", "driver_id", "constructor_id", "points"
    )
    sprint = _maybe_sprints()
    if sprint is not None:
        # Bring constructor_id onto sprint rows from race_pts (same race+driver).
        c_lookup = race_pts.select("race_id", "driver_id", "constructor_id").unique()
        sprint = (
            sprint.join(c_lookup, on=["race_id", "driver_id"], how="left")
            .select("race_id", "season", "round", "race_date", "driver_id", "constructor_id", "points")
        )
        all_pts = pl.concat([race_pts, sprint], how="vertical_relaxed")
    else:
        all_pts = race_pts

    per_race = (
        all_pts.group_by(["race_id", "season", "round", "race_date", "driver_id", "constructor_id"])
        .agg(pl.col("points").sum().alias("race_points"))
    )

    cum = (
        per_race.sort(["season", "driver_id", "race_date"])
        .with_columns(
            pl.col("race_points").cum_sum().over(["season", "driver_id"]).alias("cumulative_points"),
            pl.col("race_points").cum_count().over(["season", "driver_id"]).alias("races_completed_in_season"),
        )
        # Per (season, race) ranking on cumulative points → live standings.
        .with_columns(
            pl.col("cumulative_points").rank("ordinal", descending=True).over(["season", "race_id"])
              .alias("standing_after_race"),
            pl.col("cumulative_points").max().over(["season", "race_id"]).alias("leader_points_after_race"),
        )
        .with_columns(
            (pl.col("leader_points_after_race") - pl.col("cumulative_points")).alias("gap_to_leader"),
        )
        .sort(["season", "round", "standing_after_race"])
        .collect()
    )
    write(cum, "intermediate", "championship_state")
    return cum


if __name__ == "__main__":
    build()
