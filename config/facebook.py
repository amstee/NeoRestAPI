import json

with open('config.json') as data_file:
    neo_config = json.load(data_file)

SECRET_KEY = neo_config["bot"]["botsecretkey"]
SECRET_TOKEN = neo_config["facebook"]["facebookSecretToken"]
PAGE_ACCESS_TOKEN = neo_config["facebook"]["facebookPageAccessToken"]
