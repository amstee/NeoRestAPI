import json

with open('config.json') as data_file:
    neo_config = json.load(data_file)


PROJECT_ID = neo_config["firebase"]["project_id"]
KEY_FILE = neo_config["firebase"]
BASE_URL = 'https://fcm.googleapis.com'
FCM_ENDPOINT = 'v1/projects/' + PROJECT_ID + '/messages:send'
FCM_URL = BASE_URL + '/' + FCM_ENDPOINT
SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
