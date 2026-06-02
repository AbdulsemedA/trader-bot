"""Logging configuration for the trading bot."""

import logging
import sys
from pathlib import Path


def setup_logging(log_file: str = "trading_bot.log", level: str = "DEBUG") -> None:
    """Configure logging with both file and console handlers.

    Args:
        log_file: Path to the log file.
        level: Logging level for the file handler.
    """
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    root_logger = logging.getLogger("trading_bot")
    root_logger.setLevel(getattr(logging, level.upper(), logging.DEBUG))

    # Prevent duplicate handlers on repeated calls
    root_logger.handlers.clear()

    # File handler — captures everything (DEBUG+)
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    root_logger.addHandler(file_handler)

    # Console handler — user-facing messages only (INFO+)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    root_logger.addHandler(console_handler)
