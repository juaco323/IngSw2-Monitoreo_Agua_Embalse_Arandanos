import json
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Any, Optional

_FALLBACK_LOGGER: Optional[logging.Logger] = None


def setup_fallback_logging() -> None:
    global _FALLBACK_LOGGER
    log_dir = Path(os.getenv("LOG_DIR", "logs"))
    log_dir.mkdir(parents=True, exist_ok=True)
    fallback_path = log_dir / "fallback.log"

    max_bytes = int(os.getenv("LOG_FILE_MAX_BYTES", str(5 * 1024 * 1024)))
    backup_count = int(os.getenv("LOG_FILE_BACKUP_COUNT", "5"))

    handler = RotatingFileHandler(
        fallback_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
    )
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

    _FALLBACK_LOGGER = logging.getLogger("app.fallback")
    _FALLBACK_LOGGER.setLevel(logging.INFO)
    _FALLBACK_LOGGER.handlers.clear()
    _FALLBACK_LOGGER.addHandler(handler)


def write_fallback_record(**payload: Any) -> None:
    logger = _FALLBACK_LOGGER or logging.getLogger("app.fallback")
    line = json.dumps({**payload, "fallback": True}, ensure_ascii=False, default=str)
    level = payload.get("level", "INFO")
    if level == "FATAL":
        logger.critical(line)
    elif level == "WARN":
        logger.warning(line)
    else:
        logger.info(line)
