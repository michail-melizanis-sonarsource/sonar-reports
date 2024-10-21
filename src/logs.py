from logging import getLogger

logger = getLogger(__name__)
MAPPING = {
    'debug': 10,
    'info': 20,
    'warning': 30,
    'error': 40,
    'critical': 50
}


def log_event(level: str, event):
    logger.log(level=MAPPING.get(level.lower(), 0), msg=event)
