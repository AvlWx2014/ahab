import sys
from logging import DEBUG, INFO, Formatter, Logger, StreamHandler, getLogger

LOGGER_NAME = "ahab"


def configure_logging(enable_debug: bool = False) -> Logger:
    logger = getLogger(LOGGER_NAME)
    logger.setLevel(DEBUG if enable_debug else INFO)
    handler = StreamHandler(stream=sys.stdout)
    formatter = Formatter(
        fmt="%(asctime)s [%(levelname)-8s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S%z",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
