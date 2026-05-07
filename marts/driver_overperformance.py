"""marts.driver_overperformance — per season ranking by points-vs-grid expectation."""
from __future__ import annotations

import polars as pl

from common.io import scan, write


def build() -> pl.DataFrame:
    qvr = scan("intermediate", "qualifying_vs_race")
    df = (
        qvr.group_by(["season", "driver_id"]).agg(
            pl.col("points").sum().alias("total_points"),
            pl.col("expected_points").sum().alias("total_expected_points"),
            pl.col("points_overperformance").sum().alias("total_overperformance"),
            pl.col("points_overperformance").mean().alias("avg_overperformance_per_race"),
            pl.col("positions_gained").mean().alias("avg_positions_gained"),
            pl.col("race_id").count().alias("races_started"),
        )
        .with_columns(
            pl.col("total_overperformance").rank("min", descending=True).over("season").alias("season_rank"),
        )
        .sort(["season", "season_rank"])
        .collect()
    )
    write(df, "marts", "driver_overperformance")
    return df


if __name__ == "__main__":
    build()
