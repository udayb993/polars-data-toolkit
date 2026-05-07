"""analytics — SQL-context views over the marts + helper reports.

Exposes a single function ``sql_context()`` that returns a Polars
``SQLContext`` with every silver/intermediate/mart parquet registered as a
table, lazily.  Also writes a few CSV "reports" derived from marts.

Practices: ``pl.SQLContext``, lazy registration, CSV write.
"""
from __future__ import annotations

import logging

import polars as pl

from common.io import path_for, scan
from config import INTERMEDIATE_DIR, MARTS_DIR, REPORTS_DIR, SILVER_DIR

log = logging.getLogger(__name__)


def sql_context() -> pl.SQLContext:
    ctx = pl.SQLContext(eager=False)
    for layer_dir, layer in [(SILVER_DIR, "silver"), (INTERMEDIATE_DIR, "intermediate"), (MARTS_DIR, "marts")]:
        for p in sorted(layer_dir.glob("*.parquet")):
            name = f"{layer}_{p.stem}"
            ctx.register(name, pl.scan_parquet(p))
    return ctx


def _csv_safe(df: pl.DataFrame) -> pl.DataFrame:
    """Cast Duration columns to total milliseconds (Int64) for CSV export."""
    duration_cols = [c for c, t in df.schema.items() if t == pl.Duration]
    if not duration_cols:
        return df
    return df.with_columns(
        [pl.col(c).dt.total_milliseconds().alias(c) for c in duration_cols]
    )


def write_reports() -> None:
    """A handful of human-readable CSVs derived from marts."""
    if path_for("marts", "season_summary").exists():
        _csv_safe(scan("marts", "season_summary").collect()).write_csv(REPORTS_DIR / "season_summary.csv")
    if path_for("marts", "championship_progression").exists():
        # Final-state slice per season — the de-facto standings table.
        df = (
            scan("marts", "championship_progression")
            .filter(pl.col("round") == pl.col("total_rounds"))
            .select("season", "standing_after_race", "driver_id", "constructor_id",
                    "cumulative_points", "races_completed_in_season")
            .sort(["season", "standing_after_race"])
            .collect()
        )
        _csv_safe(df).write_csv(REPORTS_DIR / "final_standings.csv")
    if path_for("marts", "race_narrative").exists():
        _csv_safe(scan("marts", "race_narrative").collect()).write_csv(REPORTS_DIR / "race_narrative.csv")
    log.info("wrote %d reports", len(list(REPORTS_DIR.glob("*.csv"))))


def example_sql() -> pl.DataFrame:
    """Demonstrates the SQL context on a non-trivial query."""
    ctx = sql_context()
    return ctx.execute(
        """
        SELECT season,
               winner_constructor_id,
               COUNT(*) AS wins
        FROM marts_race_narrative
        GROUP BY season, winner_constructor_id
        ORDER BY season, wins DESC
        """
    ).collect()
