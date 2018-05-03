from flask_restful import Resource
from flask.views import MethodView
from config.database import db_session
from models.Circle import Circle
from models.Conversation import Conversation
from utils.decorators import securedRoute, checkContent, securedAdminRoute, securedDeviceRoute
from utils.contentChecker import contentChecker
from utils.apiUtils import *
from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs, parser, abort
import requests

SECRET_TOKEN = "abcdef12345"
PAGE_ACCESS_TOKEN = "EAACr1x9RQUwBAN7T2V2fhZCLKhXsjeWRXSeHrB6OUbPs8wcSQeKwPlcNPTbLXgENzdMcI2JZCjdVZCSSr7AYBgVRMZC5RSclC6ZBEm9ZCHINZB1TWTXy1M450ikhYX8qy0lbzKPcHeVcbmMZAAdjj5179kz5MiHclwc7v2yq1OvDNIIA04z6iWyC"

def SendMessage(recipient_id, message_text):
    data = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    }
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params={"access_token": PAGE_ACCESS_TOKEN}, json=data)
    if r.status_code != 200:
        return False
    return True

class Webhook(Resource):
    messenger_hook = {
        "hub.mode": fields.Str(missing=None),
        "hub.challenge": fields.Int(missing=None),
        "hub.verify_token": fields.Str(missing=None)
    }

    @use_args(messenger_hook)
    def get(self, args):
        if args["hub"]["mode"] == "subscribe" and args["hub"]["challenge"]:
            if args["hub"]["verify_token"] != SECRET_TOKEN:
                return "Verification token mismatch", 403
            return args["hub"]["challenge"], 200
        return "Hello Facebook", 200

    @checkContent
    def post(self, content):
        print("----facebook content----")
        print(content, file=sys.stderr)
        print("----facebook content end---")
        #if data["object"] == "page":
        #    for entry in data["entry"]:
        #        for messaging_event in entry["messaging"]:
        #            if messaging_event.get("message"):
        #                sender_id = messaging_event["sender"]["id"]        
        #                recipient_id = messaging_event["recipient"]["id"]  
        #                message_text = messaging_event["message"]["text"]
        #                print("----messenger content----")
        #                print("sender id : " + str(sender_id))
        #                print("recipient_id : " + str(recipient_id))
        #                print("message_text : " + message_text)
        #                print("----messenger content end----")
        #                send_message(sender_id, "Message received")

        return "ok", 200