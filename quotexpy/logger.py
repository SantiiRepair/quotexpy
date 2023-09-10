import logging
import logging.handlers

logger = logging.getLogger("papertrail")
logger.setLevel(logging.INFO)
papertrail_handler = logging.handlers.SysLogHandler(address=("logs6.papertrailapp.com", 38366))
logger.addHandler(papertrail_handler)
