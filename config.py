"""Project-wide configuration."""
import os
from pathlib import Path

# Seasons to ingest. Keep small for fast iteration.
# Override with env: SEASONS="2023" or SEASONS="2022,2023,2024"
SEASONS: list[int] = [
    int(s) for s in os.environ.get("SEASONS", "2022,2023,2024").split(",") if s.strip()
]

# Ergast mirror (Jolpica). Free, no auth.
ERGAST_BASE_URL = "https://api.jolpi.ca/ergast/f1"

# Data lake root and per-layer subdirs.
ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
BRONZE_DIR = DATA_DIR / "bronze"
SILVER_DIR = DATA_DIR / "silver"
INTERMEDIATE_DIR = DATA_DIR / "intermediate"
MARTS_DIR = DATA_DIR / "marts"
REPORTS_DIR = DATA_DIR / "reports"

for _d in (BRONZE_DIR, SILVER_DIR, INTERMEDIATE_DIR, MARTS_DIR, REPORTS_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# HTTP client tuning.
HTTP_TIMEOUT_S = 30.0
HTTP_MAX_RETRIES = 5
HTTP_PAGE_SIZE = 100  # Ergast default; results/laps support up to 1000 but keep modest.
