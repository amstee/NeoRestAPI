from flask_restful import Resource
from flask.views import MethodView
from config.database import db_session
from models.User import User
from models.Conversation import Conversation
from utils.decorators import securedRoute, checkContent, securedAdminRoute, securedDeviceRoute
from utils.contentChecker import contentChecker
from utils.apiUtils import *
from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs, parser, abort
import requests
import sys
import jwt

SECRET_KEY = "defaultusersecretkey"
SECRET_TOKEN = "abcdef12345"
PAGE_ACCESS_TOKEN = "EAACr1x9RQUwBANslMAGv4aU4gCqGpNvZCGMZBnQ8YhaAAkssgfGj95z0bAnPUPZBAiiYkgl34TcmEGSdUzaQsx1JcnqyFsKn3EArkEQ7TUZCTQMeZChTxRsZBzmXbCMtHk3SRrtJIwB2YYTKABVwRAQArEGK2HhDOSyB7MkkbMnOsrn8DEtdGF"

def SendMessage(recipient_id, message_text):
    params = {
        "access_token": PAGE_ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        return False
    return True

def MessengerUserModelSend(userTarget, text_message):
    if userTarget.facebookPSID != -1:
        SendMessage(userTarget.facebookPSID, text_message)
        return True
    return False

def IsUserLinked(facebookPSID):
    user = db_session.query(User).filter(User.facebookPSID == facebookPSID).first()
    if user is not None:
        return True
    return False

def LinkUserToFacebook(apiToken, psid):
        try:
            payload = jwt.decode(auth_token, SECRET_KEY)
            try:
                user = db_session.query(User).filter(User.id == payload['sub']).first()
                if user is not None:
                    user.updateContent(facebookPSID=psid)
                    return ("Bienvenue sur NEO, " + payload['first_name'] + " " + payload['last_name'] + " !")
                else:
                    return 'Token invalide !'
            except Exception as e:
                return "Une erreur est survenue, merci de réessayer ultérieurement"
        except jwt.ExpiredSignatureError:
            return 'La token a expiré, authentifiez vous a nouveau'
        except jwt.InvalidTokenError:
            return 'Token invalide, authentifiez vous a nouveau'

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
        print("----facebook content----", file=sys.stderr)
        print(content, file=sys.stderr)
        print("----facebook content end---", file=sys.stderr)
        if content["object"] == "page":
            for entry in content["entry"]:
                for messaging_event in entry["messaging"]:
                    if messaging_event.get("message"):
                        sender_id = messaging_event["sender"]["id"]        
                        recipient_id = messaging_event["recipient"]["id"]  
                        message_text = messaging_event["message"]["text"]
                        # messenger
                        #if IsUserLinked(sender_id):
                        #    print("send message to conversation")
                        #elif len(message_text) == 4096:
                        #    message = LinkUserToFacebook(message_text, sender_id)
                        #    SendMessage(sender_id, message)
                        #else:
                        #    send_message(sender_id, "Votre compte messenger n'est lié a aucun compte messenger")
                        # messenger
                        print("----messenger content----", file=sys.stderr)
                        print("sender id : " + str(sender_id), file=sys.stderr)
                        print("recipient_id : " + str(recipient_id), file=sys.stderr)
                        print("message_text : " + message_text, file=sys.stderr)
                        print("----messenger content end----", file=sys.stderr)
                        send_message(sender_id, "Message received")
        return "ok", 200