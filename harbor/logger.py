import logging
from threading import Lock

_lock = Lock()
logger = logging.getLogger(__name__)


def info(msg: str):
    with _lock:
        logger.info(msg)


def warn(msg: str):
    with _lock:
        logger.warning(msg)


def error(msg: str):
    with _lock:
        logger.error(msg)


def exception(ex: Exception):
    with _lock:
        logger.exception(ex)
