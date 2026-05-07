"""intermediate.lap_pace_normalized — circuit-baseline-normalised lap pace.

Each lap is compared to the **median lap time of the top-5 finishers in that
race** (a fair "race pace" baseline that strips out safety-car laps better
than overall mean).  The normalised value is dimensionless and comparable
across circuits.

Practices: scalar broadcast via ``over``, semi-join filter, multi-step lazy.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write


def build() -> pl.DataFrame:
    laps = scan("silver", "lap_times")
    results = scan("silver", "results")

    # Top-5 finishers per race → semi-join filter on laps.
    top5 = (
        results.filter(pl.col("finish_position") <= 5)
        .select("race_id", "driver_id")
    )
    top5_laps = laps.join(top5, on=["race_id", "driver_id"], how="semi")

    baseline = top5_laps.group_by("race_id").agg(
        pl.col("lap_time").median().alias("baseline_lap_time"),
    )

    df = (
        laps.join(baseline, on="race_id", how="left")
        .with_columns(
            (pl.col("lap_time").dt.total_milliseconds() /
             pl.col("baseline_lap_time").dt.total_milliseconds())
              .alias("lap_time_ratio"),
            (pl.col("lap_time").dt.total_milliseconds()
             - pl.col("baseline_lap_time").dt.total_milliseconds())
              .alias("lap_time_delta_ms"),
        )
        .select(
            "race_id", "season", "round", "race_date",
            "driver_id", "lap", "position_at_lap",
            "lap_time", "baseline_lap_time", "lap_time_ratio", "lap_time_delta_ms",
        )
        .sort(["season", "round", "lap", "driver_id"])
        .collect()
    )
    write(df, "intermediate", "lap_pace_normalized")
    return df


if __name__ == "__main__":
    build()
