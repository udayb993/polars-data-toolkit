"""Pytest fixtures: build the lake once per session.

Tests run against an isolated per-session lake by overriding the env
``SEASONS`` to ``2023`` (single season → fast).  We re-use any pre-built
bronze parquet files in the user's ``data/bronze`` directory if present;
otherwise we re-fetch.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Make project root importable.
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# Force a small, deterministic season set BEFORE importing config.
os.environ.setdefault("SEASONS", "2023")


@pytest.fixture(scope="session", autouse=True)
def _build_lake():
    """Build silver/intermediate/marts once per pytest session.

    Bronze is only re-fetched if missing — speeds up local iteration.
    """
    from bronze import extract  # noqa: WPS433
    from common.io import path_for  # noqa: WPS433
    from intermediate import runner as intermediate_runner  # noqa: WPS433
    from marts import runner as marts_runner  # noqa: WPS433
    from silver import runner as silver_runner  # noqa: WPS433

    # Bronze: fetch only the missing tables.
    for name, fn in extract.TASKS.items():
        if not path_for("bronze", name).exists():
            fn()
    silver_runner.run_all()
    intermediate_runner.run_all()
    marts_runner.run_all()
    yield
