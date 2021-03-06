import json
import requests
from config.log import LOG_MOBILE
from utils.log import logger_set

from oauth2client.service_account import ServiceAccountCredentials
from config.firebase import KEY_FILE, SCOPES, FCM_URL


logger = logger_set(module=__name__, file=LOG_MOBILE)


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
            'token': token,
            'notification': {
                'title': title,
                'body': body
            }
        }
    }
    return message


def send_notification(user, body, title="NEO"):
    if user.android_token is not None and user.android_token != "":
        message = fcm_message(user.android_token, title, body)
        response = send_fcm_message(message)
        logger.info("[NOTIFICATION] [%s] : %s (%s) -> %s" % (response.status_code, user.email, body, response.content))
    else:
        logger.info("[NOTIFICATION] [ERROR] : %s (%s) -> %s" % (user.email, body, "No android token found"))
