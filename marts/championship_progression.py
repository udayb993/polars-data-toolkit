"""marts.championship_progression — full live-standings table for reporting.

One row per (season, race, driver). Adds:
- ``points_delta_vs_prev_race`` (per driver per season)
- ``positions_changed_vs_prev_race``
- ``mathematically_eliminated`` flag (cannot reach leader's points even if
  they win every remaining race at 25 + 1 fastest-lap point + 8 sprint).

Practices: lag via ``shift().over()``, conditional flag from arithmetic on
remaining-races column.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write

MAX_POINTS_PER_REMAINING_RACE = 25 + 1 + 8  # rough upper bound (race+FL+sprint)


def build() -> pl.DataFrame:
    cs = scan("intermediate", "championship_state")
    races_per_season = (
        scan("silver", "races").group_by("season").agg(pl.col("round").max().alias("total_rounds"))
    )

    df = (
        cs.join(races_per_season, on="season", how="left")
        .sort(["season", "driver_id", "race_date"])
        .with_columns(
            (pl.col("cumulative_points") - pl.col("cumulative_points").shift(1).over(["season", "driver_id"]))
              .alias("points_delta_vs_prev_race"),
            (pl.col("standing_after_race") - pl.col("standing_after_race").shift(1).over(["season", "driver_id"]))
              .alias("position_change_vs_prev_race"),
            (pl.col("total_rounds") - pl.col("round")).alias("rounds_remaining"),
        )
        .with_columns(
            (pl.col("cumulative_points")
             + pl.col("rounds_remaining").cast(pl.Float64) * MAX_POINTS_PER_REMAINING_RACE
             < pl.col("leader_points_after_race")).alias("mathematically_eliminated"),
        )
        .sort(["season", "round", "standing_after_race"])
        .collect()
    )
    write(df, "marts", "championship_progression")
    return df


if __name__ == "__main__":
    build()
