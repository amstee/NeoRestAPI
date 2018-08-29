import logging
import json

with open('config.json') as data_file:
    neo_config = json.load(data_file)

LOG_ACTIVATE = neo_config["logs"]["activate"]
LOG_LEVEL = neo_config["logs"]["level"]
LOG_FOLDER = neo_config["logs"]["folder"]
LOG_FILE = neo_config["logs"]["file"]
LOG_CONSOLE = neo_config["logs"]["console"]
LOG_ACCOUNT_FILE = "neo_account.log"
LOG_CIRCLE_FILE = "neo_circle.log"
LOG_CONVERSATION_FILE = "neo_conversation.log"
LOG_DEVICE_FILE = "neo_device.log"
LOG_MEDIA_FILE = "neo_media.log"
LOG_MESSAGE_FILE = "neo_message.log"
LOG_DATABASE_FILE = "neo_database.log"
LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}
