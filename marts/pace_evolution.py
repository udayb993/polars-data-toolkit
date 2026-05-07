"""marts.pace_evolution — monthly pace per driver per season.

Practices: ``group_by_dynamic`` on race_date for monthly bucketing.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write


def build() -> pl.DataFrame:
    lpn = scan("intermediate", "lap_pace_normalized").select(
        "season", "race_date", "driver_id", "lap_time_ratio"
    ).collect()
    df = (
        lpn.sort("race_date")
        .group_by_dynamic("race_date", every="1mo", group_by=["season", "driver_id"])
        .agg(
            pl.col("lap_time_ratio").mean().alias("avg_lap_ratio"),
            pl.col("lap_time_ratio").median().alias("median_lap_ratio"),
            pl.len().alias("n_laps"),
        )
        .sort(["season", "driver_id", "race_date"])
    )
    write(df, "marts", "pace_evolution")
    return df


if __name__ == "__main__":
    build()
