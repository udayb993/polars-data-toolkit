"""marts.teammate_h2h — head-to-head per driver pair per season.

A self-join of ``intermediate.driver_race_performance`` on
``(season, race_id, constructor_id)`` keeping only ``driver_id_left <
driver_id_right`` rows.  Aggregates per pair per season.

Practices: self-join with explicit suffix, anti-pair filter, rate computation.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write


def build() -> pl.DataFrame:
    drp = scan("intermediate", "driver_race_performance").select(
        "season", "race_id", "constructor_id",
        pl.col("driver_id"),
        pl.col("finish_position"),
        pl.col("points"),
        pl.col("avg_lap_seconds"),
    )

    paired = (
        drp.join(drp, on=["season", "race_id", "constructor_id"], how="inner", suffix="_b")
        .filter(pl.col("driver_id") < pl.col("driver_id_b"))
        .with_columns(
            (pl.col("finish_position") < pl.col("finish_position_b")).alias("a_beat_b_race"),
            (pl.col("points") - pl.col("points_b")).alias("a_minus_b_points"),
            (pl.col("avg_lap_seconds") - pl.col("avg_lap_seconds_b")).alias("a_minus_b_pace_s"),
        )
    )

    df = (
        paired.group_by(["season", "constructor_id",
                         pl.col("driver_id").alias("driver_a"),
                         pl.col("driver_id_b").alias("driver_b")])
        .agg(
            pl.col("a_beat_b_race").sum().alias("a_wins"),
            (~pl.col("a_beat_b_race")).sum().alias("b_wins"),
            pl.col("a_beat_b_race").count().alias("races_compared"),
            pl.col("a_minus_b_points").sum().alias("a_points_advantage"),
            pl.col("a_minus_b_pace_s").mean().alias("a_avg_pace_advantage_s"),
        )
        .with_columns(
            (pl.col("a_wins") / pl.col("races_compared")).alias("a_win_rate"),
        )
        .sort(["season", "constructor_id", "a_win_rate"], descending=[False, False, True])
        .collect()
    )
    write(df, "marts", "teammate_h2h")
    return df


if __name__ == "__main__":
    build()
