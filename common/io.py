"""I/O helpers for the lake.  Centralised so layer paths never sprawl."""
from __future__ import annotations

import logging
from pathlib import Path

import polars as pl

from config import BRONZE_DIR, INTERMEDIATE_DIR, MARTS_DIR, REPORTS_DIR, SILVER_DIR

log = logging.getLogger(__name__)

_LAYER_DIRS = {
    "bronze": BRONZE_DIR,
    "silver": SILVER_DIR,
    "intermediate": INTERMEDIATE_DIR,
    "marts": MARTS_DIR,
    "reports": REPORTS_DIR,
}


def path_for(layer: str, name: str, suffix: str = ".parquet") -> Path:
    if layer not in _LAYER_DIRS:
        raise ValueError(f"unknown layer {layer!r}")
    return _LAYER_DIRS[layer] / f"{name}{suffix}"


def write(df: pl.DataFrame, layer: str, name: str) -> Path:
    p = path_for(layer, name)
    df.write_parquet(p, compression="zstd")
    log.info("wrote %s rows=%d cols=%d", p.name, df.height, df.width)
    return p


def read(layer: str, name: str) -> pl.DataFrame:
    return pl.read_parquet(path_for(layer, name))


def scan(layer: str, name: str) -> pl.LazyFrame:
    """Lazy scan – preferred for silver/intermediate transforms."""
    return pl.scan_parquet(path_for(layer, name))
