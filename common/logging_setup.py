"""Shared logging setup."""
import logging
import os


def setup(level: str | None = None) -> None:
    logging.basicConfig(
        level=level or os.environ.get("LOG_LEVEL", "INFO"),
        format="%(asctime)s %(levelname)-7s %(name)s :: %(message)s",
        datefmt="%H:%M:%S",
    )
