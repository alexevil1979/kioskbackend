from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler

from src.core.config import Settings


def setup_logging(settings: Settings) -> logging.Logger:
    log_path = settings.log_path
    level = getattr(logging, settings.logging.level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=settings.logging.max_bytes,
        backupCount=settings.logging.backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    root.addHandler(console)

    logger = logging.getLogger("kiosk")
    logger.info("Логирование инициализировано: %s", log_path)
    return logger
