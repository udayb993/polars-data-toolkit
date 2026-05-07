"""intermediate.constructor_race_performance — per constructor per race rollup.

Practices: ``group_by`` with multiple aggregations (count, sum, all),
boolean reductions for double-DNF/double-podium flags.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write


def build() -> pl.DataFrame:
    drp = scan("intermediate", "driver_race_performance")
    df = (
        drp.group_by(["race_id", "season", "round", "race_date", "constructor_id"])
        .agg(
            pl.col("points").sum().alias("constructor_points"),
            pl.col("finish_position").min().alias("best_finish"),
            pl.col("finish_position").max().alias("worst_finish"),
            pl.col("avg_lap_seconds").mean().alias("avg_lap_seconds"),
            pl.col("driver_id").count().alias("n_cars"),
            (~pl.col("finished_flag")).sum().alias("n_dnfs"),
            ((pl.col("finish_position") <= 3).sum()).alias("n_podiums"),
            ((~pl.col("finished_flag")).all()).alias("double_dnf"),
            ((pl.col("finish_position") <= 3).all() & (pl.col("finish_position").is_not_null().all()))
              .alias("double_podium"),
        )
        .sort(["season", "round", "constructor_points"], descending=[False, False, True])
        .collect()
    )
    write(df, "intermediate", "constructor_race_performance")
    return df


if __name__ == "__main__":
    build()
