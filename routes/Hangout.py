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

class WebhookHangout(Resource):
    @checkContent
    def post(self, content):
        print("---Hangout---", file=sys.stderr)
        try:
            if isTokenValid(content) == True:
                if content['type'] == 'ADDED_TO_SPACE' and content['space']['type'] == 'ROOM':
                    text = 'Thanks for adding me to "%s"!' % content['space']['displayName']
                elif content['type'] == 'MESSAGE':
                    text = 'You said: `%s`' % content['message']['text']
                else:
                    return
                sender_id = content["message"]["sender"]["email"]
                message_text = content["message"]["text"]
                splitMessage = message_text.split(' ')
                if len(splitMessage) >= 2 and splitMessage[0] == "/token":
                    message = LinkUserToHangout(splitMessage[1], sender_id)
                    resp = jsonify({"text":message})
                elif IsUserLinked(sender_id) == True:
                    resp = jsonify({"text":"Non implémenté"})
                    #SendMessageChoice(sender_id, message_text)
                else:
                    resp = jsonify({"text":"Votre compte messenger n'est lié a aucun compte NEO"})
                resp.status_code = 200
                return resp
            return
        except Exception as e:
            print(e, file=sys.stderr)
            return