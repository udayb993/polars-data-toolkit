"""marts.pit_crew_ranking — per constructor per season pit-stop quality.

Practices: quantile aggregates (p50/p95), IQR for consistency, descending
rank across the field.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write


def build() -> pl.DataFrame:
    pse = scan("intermediate", "pit_stop_efficiency")
    df = (
        pse.group_by(["season", "constructor_id"]).agg(
            pl.col("stop_seconds").count().alias("n_stops"),
            pl.col("stop_seconds").median().alias("median_stop_s"),
            pl.col("stop_seconds").quantile(0.95, "linear").alias("p95_stop_s"),
            (pl.col("stop_seconds").quantile(0.75, "linear")
             - pl.col("stop_seconds").quantile(0.25, "linear")).alias("iqr_stop_s"),
            pl.col("stop_seconds").min().alias("fastest_stop_s"),
        )
        .with_columns(
            pl.col("median_stop_s").rank("min").over("season").alias("rank_in_season"),
        )
        .sort(["season", "rank_in_season"])
        .collect()
    )
    write(df, "marts", "pit_crew_ranking")
    return df


if __name__ == "__main__":
    build()
