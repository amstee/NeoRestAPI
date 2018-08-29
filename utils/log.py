import logging
from config.log import LEVELS, LOG_LEVEL, LOG_ACTIVATE


def logger_set(module, file=None):
    if file is None:
        file = './neo_api.log'
    logger = logging.getLogger(module)
    logger.setLevel(LEVELS[LOG_LEVEL])

    if LOG_ACTIVATE is False:
        logging.disable(LEVELS.get("CRITICAL"))
    else:
        # create a file handler
        handler = logging.FileHandler(file)
        handler.setLevel(LEVELS[LOG_LEVEL])

        # create a logging format
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)

        # add the handlers to the logger
        logger.addHandler(handler)
    return logger

