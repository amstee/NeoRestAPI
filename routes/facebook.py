from flask_restful import Resource
from flask import request
from utils.decorators import check_content_old, route_log
from webargs import fields
from webargs.flaskparser import use_args
from bot.facebook import send_message, link_user_to_facebook, is_user_linked, send_message_choice
from bot.facebook import handle_conversation_payload
from config.facebook import SECRET_TOKEN
import sys
from utils.log import logger_set

logger = logger_set(__name__)


class WebHookMessenger(Resource):
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

    @route_log(logger)
    @check_content_old
    def post(self, content):
        try:
            if content["object"] == "page":
                for entry in content["entry"]:
                    for messaging_event in entry["messaging"]:
                        if messaging_event.get("message"):
                            sender_id = messaging_event["sender"]["id"]        
                            message_text = messaging_event["message"]["text"]
                            split_message = message_text.split(' ')
                            if 'quick_reply' not in messaging_event["message"]:
                                if len(split_message) >= 2 and split_message[0] == "/token":
                                    message = link_user_to_facebook(split_message[1], sender_id)
                                    resp = send_message(sender_id, message)
                                    return resp
                                elif is_user_linked(sender_id):
                                    send_message_choice(sender_id, message_text)
                                    return "To handle", 200
                                else:
                                    resp = send_message(sender_id, "Votre compte messenger n'est lié a aucun compte NEO")
                                    return resp
                            if 'quick_reply' in messaging_event["message"]:
                                handle_conversation_payload(messaging_event["message"]["quick_reply"]["payload"])
                                return "To handle", 200
            return "ok", 200
        except Exception as e:
            print(e, file=sys.stderr)
            return "Failed", 200
