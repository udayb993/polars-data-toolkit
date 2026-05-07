"""silver.lap_times — large-ish (~120k rows for 3 seasons) typed lap facts.

Practices: lazy + Duration parsing on a sizable file, sort key for windows.
"""
from __future__ import annotations

import polars as pl

from common.io import read, scan, write
from silver._expressions import parse_lap_time


def build() -> pl.DataFrame:
    races = read("silver", "races").select(["season", "round", "race_id", "race_date"]).lazy()
    df = (
        scan("bronze", "lap_times")
        .select(
            pl.col("season").cast(pl.Int32),
            pl.col("round").cast(pl.Int32),
            pl.col("lap").cast(pl.Int32).alias("lap"),
            pl.col("driverId").alias("driver_id"),
            pl.col("position").cast(pl.Int32, strict=False).alias("position_at_lap"),
            parse_lap_time("time").alias("lap_time"),
        )
        .join(races, on=["season", "round"], how="left")
        .select(
            "race_id", "season", "round", "race_date",
            "driver_id", "lap", "position_at_lap", "lap_time",
        )
        .sort(["season", "round", "lap", "driver_id"])
        .collect()
    )
    write(df, "silver", "lap_times")
    return df


if __name__ == "__main__":
    build()
