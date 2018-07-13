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

TOKEN="yZZieXB8D64T1qMxI9fJVCgC1vVMUB70PB9p3lIYSN4="

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
                #resp = jsonify({'text': text})
                resp = jsonify({
                                "cards": [
                                    {
                                    "header": {
                                        "title": "Pizza Bot Customer Support",
                                        "subtitle": "pizzabot@example.com",
                                        "imageUrl": "https://goo.gl/aeDtrS"
                                    },
                                    "sections": [
                                        {
                                        "widgets": [
                                            {
                                                "keyValue": {
                                                "topLabel": "Order No.",
                                                "content": "12345"
                                                }
                                            },
                                            {
                                                "keyValue": {
                                                "topLabel": "Status",
                                                "content": "In Delivery"
                                                }
                                            }
                                        ]
                                        },
                                        {
                                        "header": "Location",
                                        "widgets": [
                                            {
                                            "image": {
                                                "imageUrl": "https://maps.googleapis.com/..."
                                            }
                                            }
                                        ]
                                        },
                                        {
                                        "widgets": [
                                            {
                                                "buttons": [
                                                    {
                                                    "textButton": {
                                                        "text": "OPEN ORDER",
                                                        "onClick": {
                                                        "openLink": {
                                                            "url": "https://example.com/orders/..."
                                                        }
                                                        }
                                                    }
                                                    }
                                                ]
                                            }
                                        ]
                                        }
                                    ]
                                    }
                                ]
                                })
                resp.status_code = 200
                return resp
            return
        except Exception as e:
            print(e, file=sys.stderr)
            return