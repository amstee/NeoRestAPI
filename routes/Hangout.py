from flask_restful import Resource
from flask.views import MethodView
from config.database import db_session
from models.User import User
from models.Circle import Circle
from models.UserToCircle import UserToCircle
from models.Conversation import Conversation
from models.UserToConversation import UserToConversation
from models.Message import Message
from utils.decorators import securedRoute, checkContent, securedAdminRoute, securedDeviceRoute
from utils.contentChecker import contentChecker
from utils.apiUtils import *
from webargs import fields, validate
from webargs.flaskparser import use_args, use_kwargs, parser, abort
import requests
import sys
import hashlib
import jwt
import datetime
import json

SECRET_KEY = "defaultusersecretkey"
TOKEN="yZZieXB8D64T1qMxI9fJVCgC1vVMUB70PB9p3lIYSN4="

def encodePostBackPayload(hangoutEmail, message_text, link):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30, seconds=1),
            'iat': datetime.datetime.utcnow(),
            'hangoutEmail': hangoutEmail,
            'user_id': link.user_id,
            'link_id': link.id,
            'message_text': message_text
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token.decode()
    except Exception as e:
        print(e)
        return (str(e))

def handleConversationPayload(messagePayload):
    try:
        payload = jwt.decode(messagePayload, SECRET_KEY)
        try:
            link = db_session.query(UserToConversation).filter(UserToConversation.id == payload["link_id"] and UserToConversation.user_id == payload["user_id"]).first()
            message = Message(content=payload["message_text"])
            message.link = link
            message.conversation = link.conversation
            db_session.commit()
            return ("Votre message a été envoyé avec succès")
        except Exception as e:
            print("Une erreur est survenue : " + str(e), file=sys.stderr)
            return ("Une erreur est survenue : " + str(e))
    except jwt.ExpiredSignatureError:
        return ('Message expiré, renvoyez le message')
    except jwt.InvalidTokenError:
        return ('Message expiré, renvoyez le message')

def IsUserLinked(hangoutEmail):
    user = db_session.query(User).filter(User.hangoutEmail == hangoutEmail).first()
    if user is not None:
        return True
    return False

def LinkUserToHangout(apiToken, email):
        try:
            payload = jwt.decode(apiToken, SECRET_KEY)
            try:
                user = db_session.query(User).filter(User.id == payload['sub']).first()
                if user is not None:
                    user.updateContent(hangoutEmail=email)
                    return ("Bienvenue sur NEO, " + payload['first_name'] + " " + payload['last_name'] + " !")
                else:
                    return 'Token invalide !'
            except Exception as e:
                return "Une erreur est survenue, merci de réessayer ultérieurement"
        except jwt.ExpiredSignatureError:
            return 'La token a expiré, authentifiez vous a nouveau'
        except jwt.InvalidTokenError:
            return 'Token invalide, authentifiez vous a nouveau'

def isTokenValid(content):
    try:
        print("---Check hangout token---", file=sys.stderr)
        if content['token'] == TOKEN:
            return True
        return False
    except Exception as e:
        print(e, file=sys.stderr)
        return False

def MessageChoice(sender_id, message_text):
    quick_replies = []
    user = db_session.query(User).filter(User.hangoutEmail== sender_id).first()
    for UserToConv in user.conversationLinks:
        conv = db_session.query(Conversation).filter(Conversation.id == UserToConv.conversation_id).first()
        payload = encodePostBackPayload(sender_id, message_text, UserToConv)
        quick_replies.append({
                                    "textButton": {
                                    "text": conv.name,
                                    "onClick": {
                                        "action": {
                                        "actionMethodName": conv.name,
                                        "parameters": [
                                            {
                                            "key": "message_text",
                                            "value": payload
                                            }
                                        ]
                                        }
                                    }
                                    }
                                })
    return quick_replies

def SendMessageChoice(recipient_id, message_text):
    resp = jsonify({
                "cards": [
                    {
                    "header": {
                        "title": "Choisissez une conversation",
                        "subtitle": message_text,
                    },
                    "sections": [
                        {
                        "widgets": [
                            {
                                "buttons": MessageChoice(recipient_id, message_text)
                            }
                        ]
                        }
                    ]
                    }
                ]
                })
    return resp

def sendToSpace(space_id, message):
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "text": message
    })
    r = requests.post("https://chat.googleapis.com/v1/" + space_id + "/messages", headers=headers, data=data)
    if r.status_code != 200:
        return False
    return True

class WebhookHangout(Resource):
    @checkContent
    def post(self, content):
        print("---Hangout---", file=sys.stderr)
        try:
            if isTokenValid(content) == True:
                if content['type'] == 'ADDED_TO_SPACE' and content['space']['type'] == 'ROOM':
                    text = 'Thanks for adding me to "%s"!' % content['space']['displayName']
                elif content['type'] == 'MESSAGE':
                    sender_id = content["message"]["sender"]["email"]
                    message_text = content["message"]["text"]
                    splitMessage = message_text.split(' ')
                    if len(splitMessage) >= 2 and splitMessage[0] == "/token":
                        message = LinkUserToHangout(splitMessage[1], sender_id)
                        resp = jsonify({"text":message})
                    elif IsUserLinked(sender_id) == True:
                        resp = SendMessageChoice(sender_id, message_text)
                    else:
                        resp = jsonify({"text":"Votre compte messenger n'est lié a aucun compte NEO"})
                elif content['type'] == "CARD_CLICKED":
                    print(str(content['action']['parameters']))
                    for elem in content['action']['parameters']:
                        resp = jsonify(handleConversationPayload(elem['value']))
                resp.status_code = 200
                return resp
            return
        except Exception as e:
            print(e, file=sys.stderr)
            return