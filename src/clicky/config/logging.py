import logging.config
from pathlib import Path

from clicky.config import settings


def setup_logging() -> None:
    log_file = settings.LOG_CONFIG_FILE or Path(__file__).parent / "logging.ini"
    logging.config.fileConfig(log_file, disable_existing_loggers=False)
