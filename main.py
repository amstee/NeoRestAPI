import json
import requests
from oauth2client.service_account import ServiceAccountCredentials
from config.firebase import KEY_FILE, SCOPES, FCM_URL

def get_access_token():
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(KEY_FILE, SCOPES)
    access_token_info = credentials.get_access_token()
    return access_token_info.access_token


def send_fcm_message(fcm_message):
    headers = {
        'Authorization': 'Bearer ' + get_access_token(),
        'Content-Type': 'application/json; UTF-8',
    }
    resp = requests.post(FCM_URL, data=json.dumps(fcm_message), headers=headers)
    return resp


def fcm_message(token, title, body):
    message = {
        'message': {
            'notification': {
                'title': title,
                'body': body
            },
            'token': token,
            'tag': 'caca'
        }
    }
    return message


message = fcm_message("cXpkw4SbZh8:APA91bFefc1hawWRDnfz4-TG_NLeceA-4vF8LB_Re3ZP3vAEn2vPppZZUWllb702GGcmEkIp6Lq6dB59rJ-Y3PO2zOQsjmho17SYcUvLKQWFDwv-ii9ypAQ8iEzSp9Z2dpvSe08wfu-P", "TAG TEST", "test")
response = send_fcm_message(message)
print(response)