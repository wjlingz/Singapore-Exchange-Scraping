"""Logging configuration module."""

import logging
import sys
from datetime import datetime
import os


def setup_logging():
    """Setup logging configuration.

    Returns:
        logger: Configured logger instance. Return is optional, does not need to be used.
    """
    # Setup logging
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # Generate folder/filename with current datetime
    os.makedirs("logs", exist_ok=True)
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = os.path.join("logs", f"{current_time}.log")

    # Formatting
    formatter = logging.Formatter("[%(asctime)s] - %(levelname)s: %(message)s")

    # File handler - only WARNING and above
    file_handler = logging.FileHandler(log_filename, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)  # All levels
    file_handler.setFormatter(formatter)

    # Console handler - all levels (DEBUG and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)  # Only INFO and above
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logging.debug("Logging is set up.")

    return logger
