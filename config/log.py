import logging
import json

with open('../config.json') as data_file:
    neo_config = json.load(data_file)

LOG_ACTIVATE = neo_config["logs"]["activate"]
LOG_LEVEL = neo_config["logs"]["level"]
LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}
