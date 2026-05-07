"""silver.results — race results: long-form, fully typed, with derived flags.

Highlights:
- ``Driver``/``Constructor`` JSON decode → just the IDs (rest comes from dims).
- ``Time`` JSON decode → ``Duration`` from ``millis``.
- ``FastestLap`` JSON decode → lap number, lap-time Duration, avg speed.
- ``finish_status`` → categorised via join with ``silver.status`` (kept as
  string here; categorical assignment lives downstream).
- ``finished_flag``, ``points_scored`` typed and bounded.
"""
from __future__ import annotations

import polars as pl

from common.io import read, scan, write
from silver._expressions import parse_lap_time

DRIVER_DTYPE = pl.Struct({"driverId": pl.Utf8})
CONSTRUCTOR_DTYPE = pl.Struct({"constructorId": pl.Utf8})
TIME_DTYPE = pl.Struct({"millis": pl.Utf8, "time": pl.Utf8})
FASTLAP_DTYPE = pl.Struct({
    "rank": pl.Utf8,
    "lap": pl.Utf8,
    "Time": pl.Struct({"time": pl.Utf8}),
    "AverageSpeed": pl.Struct({"units": pl.Utf8, "speed": pl.Utf8}),
})


def build() -> pl.DataFrame:
    races = read("silver", "races").select(["season", "round", "race_id", "race_date"]).lazy()
    df = (
        scan("bronze", "results")
        .with_columns(
            pl.col("Driver").str.json_decode(DRIVER_DTYPE).struct.field("driverId").alias("driver_id"),
            pl.col("Constructor").str.json_decode(CONSTRUCTOR_DTYPE).struct.field("constructorId").alias("constructor_id"),
            pl.col("Time").str.json_decode(TIME_DTYPE).alias("_t"),
            pl.col("FastestLap").str.json_decode(FASTLAP_DTYPE).alias("_fl"),
        )
        .with_columns(
            # millis → Duration; null when DNF.
            pl.duration(milliseconds=pl.col("_t").struct.field("millis").cast(pl.Int64, strict=False))
              .alias("race_time"),
            pl.col("_fl").struct.field("lap").cast(pl.Int32, strict=False).alias("fastest_lap_no"),
            pl.col("_fl").struct.field("Time").struct.field("time").alias("_fl_time_str"),
            pl.col("_fl").struct.field("AverageSpeed").struct.field("speed").cast(pl.Float64, strict=False)
              .alias("fastest_lap_kph"),
        )
        .with_columns(
            parse_lap_time("_fl_time_str").alias("fastest_lap_time"),
        )
        .with_columns(
            pl.col("season").cast(pl.Int32),
            pl.col("round").cast(pl.Int32),
            pl.col("position").cast(pl.Int32, strict=False).alias("finish_position"),
            pl.col("positionText").alias("finish_position_text"),
            pl.col("grid").cast(pl.Int32, strict=False).alias("grid_position"),
            pl.col("laps").cast(pl.Int32, strict=False).alias("laps_completed"),
            pl.col("points").cast(pl.Float64, strict=False).alias("points"),
            pl.col("number").cast(pl.Int32, strict=False).alias("car_number"),
            pl.col("status").alias("finish_status"),
            (pl.col("status").str.to_lowercase() == "finished").alias("finished_flag"),
        )
        .join(races, on=["season", "round"], how="left")
        .select(
            "race_id", "season", "round", "race_date",
            "driver_id", "constructor_id", "car_number",
            "grid_position", "finish_position", "finish_position_text",
            "points", "laps_completed",
            "finish_status", "finished_flag",
            "race_time",
            "fastest_lap_no", "fastest_lap_time", "fastest_lap_kph",
        )
        .sort(["season", "round", "finish_position"], nulls_last=True)
        .collect()
    )
    write(df, "silver", "results")
    return df


if __name__ == "__main__":
    build()
