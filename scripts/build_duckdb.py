"""Build a DuckDB metadata file that exposes the parquet lake as
schemas (one per layer) and views (one per parquet file).

After running this once, you can do::

    duckdb data/lake.duckdb
    duckdb -ui data/lake.duckdb

and browse `bronze.*`, `silver.*`, `intermediate.*`, `marts.*`.

Views point directly at the parquet files via `read_parquet(...)`, so the
`.duckdb` file is tiny and always reflects the current contents on disk —
no re-import needed when you re-run the pipeline.
"""
from __future__ import annotations

import sys
from pathlib import Path

# Make project root importable when invoked as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import duckdb  # noqa: E402

from config import DATA_DIR  # noqa: E402

LAYERS = ("bronze", "silver", "intermediate", "marts")
DB_PATH = DATA_DIR / "lake.duckdb"


def _quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


def _quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def build(db_path: Path = DB_PATH) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    try:
        for layer in LAYERS:
            layer_dir = DATA_DIR / layer
            if not layer_dir.exists():
                continue

            con.execute(f"CREATE SCHEMA IF NOT EXISTS {_quote_ident(layer)}")

            # Drop any views that no longer have a backing parquet file.
            existing = {
                row[0]
                for row in con.execute(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = ? AND table_type = 'VIEW'",
                    [layer],
                ).fetchall()
            }
            on_disk = {p.stem for p in layer_dir.glob("*.parquet")}
            for stale in existing - on_disk:
                con.execute(f"DROP VIEW {_quote_ident(layer)}.{_quote_ident(stale)}")

            # (Re)create one view per parquet file.
            n = 0
            for parquet in sorted(layer_dir.glob("*.parquet")):
                view = f"{_quote_ident(layer)}.{_quote_ident(parquet.stem)}"
                src = _quote_literal(str(parquet.resolve()).replace("\\", "/"))
                con.execute(
                    f"CREATE OR REPLACE VIEW {view} AS "
                    f"SELECT * FROM read_parquet({src})"
                )
                n += 1
            print(f"[{layer}] {n} view(s)")
    finally:
        con.close()
    print(f"wrote {db_path}")


if __name__ == "__main__":
    build()
