from logging import getLogger, FileHandler, Formatter

LEVEL_MAPPING = {
    'debug': 10,
    'info': 20,
    'warning': 30,
    'error': 40,
    'critical': 50
}


def log_event(level: str, event, logger_name: str = 'default'):
    logger = getLogger(logger_name)
    logger.log(level=LEVEL_MAPPING.get(level.lower(), 0), msg=event)


def configure_logger(name, level, output_file=None):
    logger = getLogger(name)
    logger.setLevel(LEVEL_MAPPING.get(level.lower(), 0))
    if output_file is None:
        return logger
    handler = FileHandler(output_file)
    handler.setLevel(LEVEL_MAPPING.get(level.lower(), 0))
    formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
