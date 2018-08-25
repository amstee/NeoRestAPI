import logging


def logger_set(module):
    logger = logging.getLogger(module)
    logger.setLevel(logging.DEBUG)

    # create a file handler
    handler = logging.FileHandler('./neo_api.log')
    handler.setLevel(logging.DEBUG)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)
    return logger
