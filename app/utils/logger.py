"""
Centralized Loguru configuration.

Import `logger` from this module anywhere in the app instead of using the
standard `logging` module, so all log output (console + rotating file) is
consistent in format and destination.
"""

import sys
from pathlib import Path

from loguru import logger

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Remove default handler so we control format/sinks explicitly.
logger.remove()

# Console sink - human readable, colorized.
logger.add(
    sys.stdout,
    level="INFO",
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    ),
    colorize=True,
)

# File sink - rotated daily, retained for 14 days, JSON-free plain text.
logger.add(
    LOG_DIR / "ecovision_{time:YYYY-MM-DD}.log",
    level="DEBUG",
    rotation="00:00",
    retention="14 days",
    compression="zip",
    enqueue=True,
    backtrace=False,
    diagnose=False,
)

__all__ = ["logger"]
