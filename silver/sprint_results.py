"""silver.sprint_results — same shape as results, smaller points scale."""
from __future__ import annotations

import polars as pl

from common.io import path_for, read, scan, write
from silver.results import DRIVER_DTYPE, CONSTRUCTOR_DTYPE, TIME_DTYPE


def build() -> pl.DataFrame:
    if not path_for("bronze", "sprint_results").exists():
        # Some seasons have no sprints; skip cleanly.
        write(pl.DataFrame(), "silver", "sprint_results")
        return pl.DataFrame()
    races = read("silver", "races").select(["season", "round", "race_id", "race_date"]).lazy()
    src = scan("bronze", "sprint_results")
    if src.collect_schema().len() == 0:
        write(pl.DataFrame(), "silver", "sprint_results")
        return pl.DataFrame()
    df = (
        src
        .with_columns(
            pl.col("Driver").str.json_decode(DRIVER_DTYPE).struct.field("driverId").alias("driver_id"),
            pl.col("Constructor").str.json_decode(CONSTRUCTOR_DTYPE).struct.field("constructorId").alias("constructor_id"),
            pl.col("Time").str.json_decode(TIME_DTYPE).alias("_t"),
        )
        .with_columns(
            pl.duration(milliseconds=pl.col("_t").struct.field("millis").cast(pl.Int64, strict=False))
              .alias("sprint_time"),
            pl.col("season").cast(pl.Int32),
            pl.col("round").cast(pl.Int32),
            pl.col("position").cast(pl.Int32, strict=False).alias("finish_position"),
            pl.col("grid").cast(pl.Int32, strict=False).alias("grid_position"),
            pl.col("points").cast(pl.Float64, strict=False).alias("sprint_points"),
            pl.col("laps").cast(pl.Int32, strict=False).alias("laps_completed"),
            pl.col("status").alias("finish_status"),
            (pl.col("status").str.to_lowercase() == "finished").alias("finished_flag"),
        )
        .join(races, on=["season", "round"], how="left")
        .select(
            "race_id", "season", "round", "race_date",
            "driver_id", "constructor_id",
            "grid_position", "finish_position", "sprint_points", "laps_completed",
            "finish_status", "finished_flag", "sprint_time",
        )
        .sort(["season", "round", "finish_position"], nulls_last=True)
        .collect()
    )
    write(df, "silver", "sprint_results")
    return df


if __name__ == "__main__":
    build()
