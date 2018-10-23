import json
from .APNs import APNs, Payload
from config.log import LOG_MOBILE
from utils.log import logger_set

with open('config.json') as data_file:
    neo_config = json.load(data_file)


logger = logger_set(module=__name__, file=LOG_MOBILE)
apns = APNs(use_sandbox=True, cert_file="ressources/cert_ios.pem", key_file="ressources/key_ios.pem")


def send_notification(user, alert="Neo notification", sound="default", badge=1, mutable_content=True):
    if user.ios_token:
        payload = Payload(alert=alert, sound=sound, badge=badge, mutable_content=mutable_content)
        if neo_config.use_ios:
            apns.gateway_server.send_notification(user.ios_token, payload)
    else:
        logger.info("Unable to send notification : %s --> ios_token not found for user %s" % (alert, user.email))
