"""silver.pit_stops — typed pit-stop facts.

Practices: numeric duration parse, race_id join, stop sequence integrity.
"""
from __future__ import annotations

import polars as pl

from common.io import read, scan, write


def build() -> pl.DataFrame:
    races = read("silver", "races").select(["season", "round", "race_id", "race_date"]).lazy()
    df = (
        scan("bronze", "pit_stops")
        .select(
            pl.col("season").cast(pl.Int32),
            pl.col("round").cast(pl.Int32),
            pl.col("driverId").alias("driver_id"),
            pl.col("lap").cast(pl.Int32, strict=False).alias("lap"),
            pl.col("stop").cast(pl.Int32, strict=False).alias("stop_number"),
            pl.col("time").alias("clock_time"),
            # ``duration`` is seconds-with-decimals string, e.g. "25.885".
            pl.duration(microseconds=(pl.col("duration").cast(pl.Float64, strict=False) * 1_000_000).cast(pl.Int64, strict=False))
              .alias("stop_duration"),
        )
        .join(races, on=["season", "round"], how="left")
        .select(
            "race_id", "season", "round", "race_date",
            "driver_id", "stop_number", "lap", "clock_time", "stop_duration",
        )
        .sort(["season", "round", "driver_id", "stop_number"])
        .collect()
    )
    write(df, "silver", "pit_stops")
    return df


if __name__ == "__main__":
    build()
