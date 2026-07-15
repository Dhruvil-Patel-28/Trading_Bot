"""
Logging configuration for the trading bot.
Sets up a shared logger that writes structured logs to logs/trading_bot.log.
"""

import logging
import os


def get_logger(name: str = "trading_bot") -> logging.Logger:
    """
    Returns a configured logger instance.
    All modules should use this to get a consistent logger.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers if get_logger is called multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    # Ensure the logs directory exists
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "trading_bot.log")

    # File handler — captures DEBUG and above
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    # Console handler — captures WARNING and above (keeps CLI output clean)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    # Structured format: timestamp | level | module | message
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s.%(module)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
