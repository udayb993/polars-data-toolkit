"""intermediate.driver_race_performance — one row per driver per race.

Adds derived metrics built primarily with **window functions**:
- positions_gained = grid - finish (positive = overtook the field)
- total_pit_time per driver per race
- avg_lap_pace (Duration → cast to seconds Float for portability)
- pace_vs_winner = avg_lap_pace / winner's avg_lap_pace
- pace_vs_teammate = avg_lap_pace - mean(avg_lap_pace) over (race, constructor)
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write


def build() -> pl.DataFrame:
    results = scan("silver", "results")
    pits = scan("silver", "pit_stops")
    laps = scan("silver", "lap_times")

    pit_total = pits.group_by(["race_id", "driver_id"]).agg(
        pl.col("stop_duration").sum().alias("total_pit_time"),
        pl.col("stop_duration").count().alias("n_stops"),
    )
    lap_pace = laps.group_by(["race_id", "driver_id"]).agg(
        pl.col("lap_time").mean().alias("avg_lap_time"),
        pl.col("lap_time").median().alias("median_lap_time"),
        pl.col("lap_time").std().alias("std_lap_time"),
        pl.col("lap_time").min().alias("best_lap_time"),
    )

    df = (
        results.select(
            "race_id", "season", "round", "race_date",
            "driver_id", "constructor_id",
            "grid_position", "finish_position", "points",
            "finished_flag", "finish_status",
        )
        .join(pit_total, on=["race_id", "driver_id"], how="left")
        .join(lap_pace, on=["race_id", "driver_id"], how="left")
        .with_columns(
            (pl.col("grid_position") - pl.col("finish_position")).alias("positions_gained"),
            # Avg lap as seconds (Float) for ratio math; Duration / Duration not supported.
            (pl.col("avg_lap_time").dt.total_milliseconds() / 1000.0).alias("avg_lap_seconds"),
        )
        # Winner's avg lap as a per-race scalar via window.
        .with_columns(
            pl.col("avg_lap_seconds")
              .filter(pl.col("finish_position") == 1)
              .mean().over("race_id")
              .alias("winner_avg_lap_seconds"),
            # Teammate-relative pace: per (race_id, constructor_id) demeaning.
            (pl.col("avg_lap_seconds") - pl.col("avg_lap_seconds").mean().over(["race_id", "constructor_id"]))
              .alias("pace_vs_teammate_s"),
        )
        .with_columns(
            (pl.col("avg_lap_seconds") / pl.col("winner_avg_lap_seconds")).alias("pace_vs_winner_ratio"),
        )
        .sort(["season", "round", "finish_position"], nulls_last=True)
        .collect()
    )
    write(df, "intermediate", "driver_race_performance")
    return df


if __name__ == "__main__":
    build()
