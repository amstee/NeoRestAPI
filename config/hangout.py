import json

with open('config.json') as data_file:
    neo_config = json.load(data_file)

SECRET_KEY = neo_config["bot"]["botsecretkey"]
TOKEN = neo_config["hangout"]["hangoutToken"]
KEY_FILE = neo_config["hangout"]["hangoutConfig"]
