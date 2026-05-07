"""Thin paginated HTTP client for the Ergast (Jolpica mirror) F1 API.

The Ergast API returns a wrapper of the form:

    {"MRData": {"limit": "30", "offset": "0", "total": "123", ... <payload>}}

This module hides pagination + retry/back-off + polite throttling behind a
single ``fetch_all`` call that returns the raw ``MRData`` dict for every page
concatenated as a list.

Jolpica has tight rate limits for unauthenticated traffic (≈4 req/s, ~500
req/hour).  We sleep ``REQUEST_DELAY_S`` between calls and honour the
``Retry-After`` header on 429.
"""
from __future__ import annotations

import logging
import threading
import time
from typing import Any, Iterable

import httpx
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from config import ERGAST_BASE_URL, HTTP_MAX_RETRIES, HTTP_PAGE_SIZE, HTTP_TIMEOUT_S

log = logging.getLogger(__name__)

_RETRYABLE = (httpx.TransportError, httpx.HTTPStatusError)

# Jolpica burst budget is ~4 req/s — stay well under that to avoid 429s.
REQUEST_DELAY_S = 0.4
_lock = threading.Lock()
_last_call_ts: float = 0.0


def _throttle() -> None:
    global _last_call_ts
    with _lock:
        elapsed = time.monotonic() - _last_call_ts
        if elapsed < REQUEST_DELAY_S:
            time.sleep(REQUEST_DELAY_S - elapsed)
        _last_call_ts = time.monotonic()


@retry(
    retry=retry_if_exception_type(_RETRYABLE),
    wait=wait_exponential(multiplier=2, min=2, max=60),
    stop=stop_after_attempt(HTTP_MAX_RETRIES),
    reraise=True,
)
def _get(client: httpx.Client, url: str, params: dict[str, Any]) -> dict:
    _throttle()
    r = client.get(url, params=params, timeout=HTTP_TIMEOUT_S)
    if r.status_code == 429:
        wait = float(r.headers.get("Retry-After", "5"))
        log.warning("429 from %s; sleeping %.1fs", url, wait)
        time.sleep(wait)
        r.raise_for_status()
    r.raise_for_status()
    return r.json()


def fetch_all(path: str, *, limit: int = HTTP_PAGE_SIZE) -> list[dict]:
    """Fetch every page of an Ergast endpoint.

    ``path`` is the part *after* ``ERGAST_BASE_URL``, e.g. ``"2023/results"``.
    Returns the list of ``MRData`` dicts (one per page) so downstream code can
    decide which inner key (``RaceTable``, ``DriverTable``, ...) to extract.
    """
    url = f"{ERGAST_BASE_URL}/{path.lstrip('/')}.json"
    pages: list[dict] = []
    offset = 0
    with httpx.Client(headers={"User-Agent": "polars-data-toolkit/0.1"}) as client:
        while True:
            payload = _get(client, url, {"limit": limit, "offset": offset})
            mrdata = payload["MRData"]
            pages.append(mrdata)
            total = int(mrdata.get("total", 0))
            offset += limit
            log.debug("fetched %s offset=%d/%d", path, min(offset, total), total)
            if offset >= total:
                break
    return pages


def iter_inner(pages: Iterable[dict], *table_path: str) -> list[dict]:
    """Concatenate the rows nested at ``MRData.<table_path>...`` across pages.

    Example: ``iter_inner(pages, "RaceTable", "Races")`` returns the union of
    every page's ``MRData.RaceTable.Races`` array.
    """
    out: list[dict] = []
    for page in pages:
        node: Any = page
        for key in table_path:
            node = node.get(key, {}) if isinstance(node, dict) else node
        if isinstance(node, list):
            out.extend(node)
    return out
