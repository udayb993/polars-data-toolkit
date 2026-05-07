"""intermediate.qualifying_vs_race — over/under-performance vs grid.

For each driver-race we compute: actual points scored, expected points from
the grid position (using a static F1 points table indexed by grid slot, NOT
the formal podium table — it's a *rough* expectation), and the over/under.

Practices: in-memory lookup table joined as a DataFrame, ``coalesce`` for
out-of-points-paying positions.
"""
from __future__ import annotations

import polars as pl

from common.io import scan, write

# Empirical: median points scored historically by each starting grid slot.
# Approximated for teaching purposes.
EXPECTED_POINTS_BY_GRID = pl.DataFrame({
    "grid_position": list(range(1, 21)),
    "expected_points": [18.5, 14.0, 11.5, 9.5, 7.5, 5.5, 4.0, 3.0, 2.0, 1.5,
                        1.0, 0.7, 0.5, 0.3, 0.2, 0.1, 0.0, 0.0, 0.0, 0.0],
})


def build() -> pl.DataFrame:
    results = scan("silver", "results")
    quali = scan("silver", "qualifying").select("race_id", "driver_id", "quali_position", "best_quali_time", "gap_to_pole")

    df = (
        results.select("race_id", "season", "round", "race_date",
                       "driver_id", "constructor_id",
                       "grid_position", "finish_position", "points")
        .join(quali, on=["race_id", "driver_id"], how="left")
        .join(EXPECTED_POINTS_BY_GRID.lazy(), on="grid_position", how="left")
        .with_columns(
            pl.col("expected_points").fill_null(0.0),
        )
        .with_columns(
            (pl.col("points") - pl.col("expected_points")).alias("points_overperformance"),
            (pl.col("grid_position") - pl.col("finish_position")).alias("positions_gained"),
            (pl.col("quali_position") - pl.col("finish_position")).alias("quali_to_finish_delta"),
        )
        .sort(["season", "round", "points_overperformance"], descending=[False, False, True], nulls_last=True)
        .collect()
    )
    write(df, "intermediate", "qualifying_vs_race")
    return df


if __name__ == "__main__":
    build()
