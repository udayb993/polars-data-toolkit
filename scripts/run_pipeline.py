"""End-to-end pipeline driver.

Usage:
    python scripts/run_pipeline.py                      # all layers
    python scripts/run_pipeline.py --layer silver       # only silver
    python scripts/run_pipeline.py --skip-bronze        # skip API fetch
    python scripts/run_pipeline.py --layer marts --skip-bronze --skip-silver --skip-intermediate
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

# Make project root importable when invoked as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analytics import write_reports  # noqa: E402
from bronze import extract as bronze  # noqa: E402
from common.logging_setup import setup  # noqa: E402
from intermediate import runner as intermediate_runner  # noqa: E402
from marts import runner as marts_runner  # noqa: E402
from silver import runner as silver_runner  # noqa: E402

LAYERS = ("bronze", "silver", "intermediate", "marts", "reports")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--layer", choices=LAYERS, help="run only one layer")
    parser.add_argument("--skip-bronze", action="store_true")
    parser.add_argument("--skip-silver", action="store_true")
    parser.add_argument("--skip-intermediate", action="store_true")
    parser.add_argument("--skip-marts", action="store_true")
    parser.add_argument("--skip-reports", action="store_true")
    args = parser.parse_args()

    setup()
    t0 = time.perf_counter()

    def _run(layer: str, fn) -> None:
        if args.layer and args.layer != layer:
            return
        if getattr(args, f"skip_{layer}", False):
            return
        ts = time.perf_counter()
        fn()
        print(f"[{layer}] done in {time.perf_counter() - ts:.1f}s")

    _run("bronze", bronze.run_all)
    _run("silver", silver_runner.run_all)
    _run("intermediate", intermediate_runner.run_all)
    _run("marts", marts_runner.run_all)
    _run("reports", write_reports)

    print(f"[total] {time.perf_counter() - t0:.1f}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
