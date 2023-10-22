import logging
import logging.handlers

logger = logging.getLogger(__name__)

logging.basicConfig(
    filename="quotexpy.log",
    format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
    level=logging.INFO,
)
