"""Verify analytics SQL context registers all marts and a query runs."""
from __future__ import annotations

from analytics import example_sql, sql_context


def test_sql_context_registers_marts():
    ctx = sql_context()
    tables = set(ctx.tables())
    # A spot-check on a couple of must-have tables.
    assert "marts_season_summary" in tables
    assert "intermediate_championship_state" in tables
    assert "silver_results" in tables


def test_example_sql_runs():
    df = example_sql()
    assert df.height > 0
    assert "wins" in df.columns
