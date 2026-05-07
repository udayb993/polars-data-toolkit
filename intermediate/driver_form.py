"""intermediate.driver_form — rolling 5-race form per driver.

Practices: ``rolling_*`` aggregations *over* a per-driver partition, ordered
by race_date.  Polars' rolling expressions are date-aware via the index
argument or simply use ``.rolling_mean`` after sorting per group.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write

WINDOW = 5


def build() -> pl.DataFrame:
    drp = scan("intermediate", "driver_race_performance").select(
        "race_id", "season", "round", "race_date",
        "driver_id", "points", "finish_position", "finished_flag",
    )
    df = (
        drp.sort(["driver_id", "race_date"])
        .with_columns(
            pl.col("points").rolling_mean(window_size=WINDOW, min_samples=1).over("driver_id").alias("avg_points_5r"),
            pl.col("finish_position").rolling_mean(window_size=WINDOW, min_samples=1).over("driver_id").alias("avg_finish_5r"),
            ((pl.col("finish_position") <= 3).cast(pl.Float64))
              .rolling_mean(window_size=WINDOW, min_samples=1).over("driver_id").alias("podium_rate_5r"),
            ((~pl.col("finished_flag")).cast(pl.Float64))
              .rolling_mean(window_size=WINDOW, min_samples=1).over("driver_id").alias("dnf_rate_5r"),
            pl.col("race_date").cum_count().over("driver_id").alias("races_to_date"),
        )
        .sort(["season", "round", "driver_id"])
        .collect()
    )
    write(df, "intermediate", "driver_form")
    return df


if __name__ == "__main__":
    build()
