"""A python wrapper for Quotex API"""

import logging

__author__ = "Santiago Ramirez"

logging.basicConfig(
    filename=".quotexpy.log",
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())
