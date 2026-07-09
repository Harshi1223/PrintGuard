"""
PrintGuard Fog Node Logging
-----------------------------
Centralised logger so every fog module (subscriber, processor,
dispatcher, buffer, etc.) writes to the same log file and console
with a consistent format. This is what backs the "logged to
CloudWatch" story in the report once the fog node runs on EC2 -
CloudWatch can tail LOG_FILE directly via the CloudWatch agent.
"""

import logging

from config import LOG_FILE


def get_logger(name):

    logger = logging.getLogger(name)

    # Avoid attaching duplicate handlers if get_logger() is called
    # more than once for the same module name.
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    )

    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger