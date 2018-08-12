from flask_restful import Resource
from config.database import db_session
from models.User import User
from models.Circle import Circle
from models.UserToCircle import UserToCircle
from models.Conversation import Conversation
from models.UserToConversation import UserToConversation
from models.Message import Message
from utils.decorators import checkContent
from utils.apiUtils import *
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build, build_from_document
import sys
import jwt
import datetime

SECRET_KEY = "defaultusersecretkey"
TOKEN="yZZieXB8D64T1qMxI9fJVCgC1vVMUB70PB9p3lIYSN4="

KEY_FILE={
  "type": "service_account",
  "project_id": "neobot-1531083330987",
  "private_key_id": "0b200e9c75678a354c927ca231982c68c3182956",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDR3Z+9E86VhQHX\nTyk0j5TZILSFq2XnmRjJ2/4buQhfNVS6YDRRPA2r/OpmSMPEYAfqGx4k+dWE4sq4\nm7q1d2jiy2aRsfTc3GiLJJvsC0hmixgGf4SlMCKNkEqLc1fzmyAp3ryj+NBwiXrN\nUavCfzMa4sjeOZYMR62sswOC7E+hZRJXqMZPCnYF7/BceYL14ohHm9uGimhWHgu+\nkP7POpNj5YC6bw3LjgLBSPZMF2lPYkIx7WXqlyB/Gv4OGgl5H4mMHis0WFA/SYkg\nxFoXzU9mwzYnenprhd2/VsgRvgOgBsXZda2I8fRM+dL1V+Fn1BahRGF0eii6s72L\niJTSOx5vAgMBAAECggEAHTehmY08YYyW6QbYUbz7mA75kvJ9yXSDAvdhtTJZfAfM\nt/XU0sptjNg1OfA/cQN9lpYX6EXv+AQq/PCRWdo5+/kdWoNP97+nvldmbcJUXhJX\nUfBG40iERvkjp65zPDMIk0uzL5DgVAqP0i3gn79dugyAso+J2EPSZgy2HHAR1gIf\nh2ZUZPDt9AXvnhx6T2IbkSl2HDMjYTn2F/TSVkfhNHZdSBT/+i2yPNHRJBxzUQlS\nzi8jkQqA/tEoEtSprs5m8m91TTn3wkpFM25oNCqWcatzXEUg9lB3qhJeq3bBQUFC\ndNECfyk0unriBEDvlBvAD/IHoqeMEYUiEemee8McgQKBgQD5whO1DUL95b53hV96\n6BjQHH27v1yeg79awd5jY1vpM9KYUWgUq1n6DJgr1bzLObvAX2ojw3GBFmtXC4X2\niToSJdO48Ti9HTK4rNz9l3tVGF1AdHG+8DKP4JSiQvFD7j66DjDRZ+7ASAXsSVIb\n8j2H3Vshj2gkSomSyTkCq3+UXwKBgQDXHFH1cao1NYU08FnhHQorc12q5gHq63jc\nQTB3a5VHo5J3UxP9hp+m/mzV99MO1eKOLnzsoKK0InsowAEmCAYTmi++HIlE5oyr\n7gXJSygKzAtcLK3nCw3HAkdYfChPPP158nPndaS1GCe88jJU+V3gQP2TQ3rgmzpX\nAUgKT/0v8QKBgQDSBnFaE//c0IDds0t6aIjNINhetGonZnTY1iS0AU6+CXUz32kd\n0IZGbqbcXc14PGF1QQdZcbYWLosvVKJfkkBCGIs1f6wN4+rOP5dKrULqaSWp2QH5\n5bUvJlT3KkIGtOcMwHgu8C5mhWptq66fj5JMmUlULGsP8ZpE1G/bneoYEwKBgGKV\nTQ5yeDIIhDLd0CM2HtoI9i2DWe+i2PIAQkkImhKJ6W8cOPYgw3xR7+kjuat75GeK\n8J+1gruRbeYgEKawWLCVIjo7c8GK8388B5TYB9Li7nXg2BYh37+L0MzBoeumpPhF\nYE78gG6qUlPqn5yH6DkFL/FUpLTZDySeprhrLjrRAoGAY4A+w/+MsEuseamRR1BC\n1M2NZwD/Yj7skN8XR8Jo/jnAXg4QdAoNaVr5mJdVccF9N0u9sVUdHrkHoWIdjJ9I\nO4e0WQqikm7cvamzwoQ1ur/ITahdxwLtft9M+wl208KEGzZpRBs7TOvKqxy6+SyC\nG2OGa7Xhy9wJPA2zFyJO7GE=\n-----END PRIVATE KEY-----\n",
  "client_email": "starting-account-oxs2g8j3eirm@neobot-1531083330987.iam.gserviceaccount.com",
  "client_id": "117878793462799396292",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://accounts.google.com/o/oauth2/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/starting-account-oxs2g8j3eirm%40neobot-1531083330987.iam.gserviceaccount.com"
}

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
            print(messagePayload)
            link = db_session.query(UserToConversation).filter(UserToConversation.id == payload["link_id"] and UserToConversation.user_id == payload["user_id"]).first()
            message = Message(content=payload["message_text"])
            message.link = link
            message.conversation = link.conversation
            db_session.commit()
            return "Votre message a été envoyé avec succès"
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
                    return "Bienvenue sur NEO, " + payload['first_name'] + " " + payload['last_name'] + " !"
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
    scopes = ['https://www.googleapis.com/auth/chat.bot']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(KEY_FILE, scopes)
    http = Http()
    credentials.authorize(http)
    chat = build('chat', 'v1', http=http)
    resp = chat.spaces().messages().create(
        parent=space_id,
        body={'text': message}).execute()
    return resp

def HangoutCircleModelSend(senderID, circle, text_message):
    circleTargets = db_session.query(UserToCircle).filter(UserToCircle.circle_id == circle.id)
    for targetUser in circleTargets:
        targetUserData = db_session.query(User).filter(targetUser.user_id == User.id).first()
        if senderID != targetUserData.id and targetUserData.hangoutEmail is not None and len(targetUserData.hangoutEmail) > 0:
            SendMessage(targetUserData.hangoutEmail, text_message)

def HangoutConversationModelSend(senderID, conversation, text_message):
    circle = db_session.query(Circle).filter(Circle.id == conversation.circle_id).first()
    HangoutCircleModelSend(senderID, circle, text_message)

class WebhookHangout(Resource):
    @checkContent
    def post(self, content):
        try:
            if isTokenValid(content) == True:
                if content['type'] == 'ADDED_TO_SPACE' and content['space']['type'] == 'ROOM':
                    text = 'Thanks for adding me to "%s"!' % content['space']['displayName']
                elif content['type'] == 'MESSAGE':
                    sender_id = content["space"]["name"]
                    message_text = content["message"]["text"]
                    splitMessage = message_text.split(' ')
                    if len(splitMessage) >= 2 and splitMessage[0] == "/token":
                        message = LinkUserToHangout(splitMessage[1], sender_id)
                        resp = jsonify({"text":message})
                    elif IsUserLinked(sender_id) == True:
                        resp = SendMessageChoice(sender_id, message_text)
                    else:
                        resp = jsonify({"text":"Votre compte hangout n'est lié a aucun compte NEO"})
                elif content['type'] == "CARD_CLICKED":
                    for elem in content['action']['parameters']:
                        resp = jsonify({"text" : handleConversationPayload(elem['value'])})
                resp.status_code = 200
                return resp
            return
        except Exception as e:
            print(e, file=sys.stderr)
            return