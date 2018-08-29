import logging
from os import path, makedirs
from config.log import LEVELS, LOG_LEVEL, LOG_ACTIVATE, LOG_FOLDER, LOG_CONSOLE, LOG_FILE


def logger_set(module, file=None):
    print(file)
    if not path.exists(LOG_FOLDER):
        makedirs(LOG_FOLDER)
    if file is None:
        file = 'neo_api.log'
    logger = logging.getLogger(module)
    logger.setLevel(LEVELS[LOG_LEVEL])
    if LOG_ACTIVATE is False:
        logging.disable(LEVELS.get("CRITICAL"))
    else:
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        if LOG_FILE is True:
            file_handler = logging.FileHandler('%s/%s' % (LOG_FOLDER, file))
            file_handler.setLevel(LEVELS[LOG_LEVEL])
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        if LOG_CONSOLE is True or (LOG_CONSOLE is False and LOG_FILE is False):
            console_handler = logging.StreamHandler()
            console_handler.setLevel(LEVELS[LOG_LEVEL])
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
    return logger

