from flask import jsonify
from config.database import db
from models.User import User
from models.Circle import Circle
from models.UserToCircle import UserToCircle
from models.Conversation import Conversation
from models.UserToConversation import UserToConversation
from models.Message import Message
from httplib2 import Http
from oauth2client.service_account import ServiceAccountCredentials
from apiclient.discovery import build
import sys
import jwt
import datetime
from config.hangout import SECRET_KEY, TOKEN, KEY_FILE


def encode_post_back_payload(hangout_space, message_text, link):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30, seconds=1),
            'iat': datetime.datetime.utcnow(),
            'hangout_space': hangout_space,
            'user_id': link.user_id,
            'link_id': link.id,
            'message_text': message_text
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token.decode()
    except Exception as e:
        return str(e)


def handle_conversation_payload(message_payload):
    try:
        payload = jwt.decode(message_payload, SECRET_KEY)
        try:
            print(message_payload)
            link = db.session.query(UserToConversation).filter(UserToConversation.id == payload["link_id"] and
                                                               UserToConversation.user_id == payload["user_id"]).first()
            message = Message(content=payload["message_text"])
            message.link = link
            message.conversation = link.conversation
            db.session.commit()
            return "Votre message a été envoyé avec succès"
        except Exception as e:
            return "Une erreur est survenue : " + str(e)
    except jwt.ExpiredSignatureError:
        return 'Message expiré, renvoyez le message'
    except jwt.InvalidTokenError:
        return 'Message expiré, renvoyez le message'


def is_user_linked(hangout_space):
    user = db.session.query(User).filter(User.hangout_space == hangout_space).first()
    if user is not None:
        return True
    return False


def link_user_to_hangout(api_token, email):
        try:
            payload = jwt.decode(api_token, SECRET_KEY)
            try:
                user = db.session.query(User).filter(User.id == payload['sub']).first()
                if user is not None:
                    old_user = db.session.query(User).filter(User.hangout_space == str(email)).first()
                    if old_user is not None:
                        old_user.update_content(facebook_psid=None)
                    user.update_content(hangout_space=email)
                    return "Bienvenue sur NEO, " + payload['first_name'] + " " + payload['last_name'] + " !"
                else:
                    return 'Token invalide !'
            except Exception as e:
                return "Une erreur est survenue, merci de réessayer ultérieurement"
        except jwt.ExpiredSignatureError:
            return 'La token a expiré, authentifiez vous a nouveau'
        except jwt.InvalidTokenError:
            return 'Token invalide, authentifiez vous a nouveau'


def is_token_valid(content):
    try:
        if content['token'] == TOKEN:
            return True
        return False
    except Exception as e:
        return False


def message_choice(hangout_space, message_text, user):
    quick_replies = []
    user = db.session.query(User).filter(User.hangout_space == hangout_space).first()
    for user_to_conversation in user.conversation_links:
        conv = db.session.query(Conversation).filter(Conversation.id == user_to_conversation.conversation_id).first()
        payload = encode_post_back_payload(hangout_space, message_text, user_to_conversation)
        quick_replies.append({
                                "textButton": {
                                    "text": conv.name,
                                    "onClick": {
                                        "action": {
                                            "actionMethodName": conv.name,
                                            "parameters": [{
                                                "key": "message_text",
                                                "value": payload
                                            }]
                                        }
                                    }
                                }
                            })
    return quick_replies


def send_message_choice(recipient_id, message_text):
    user = db.session.query(User).filter(User.hangout_space == recipient_id).first()
    if len(user.conversation_links) > 0:
        resp = jsonify({
                    "cards": [{
                            "header": {
                                "title": "Choisissez une conversation",
                                "subtitle": message_text,
                            },
                            "sections": [{
                                "widgets": [{
                                        "buttons": message_choice(recipient_id, message_text, user)
                                }]
                            }]
                        }]
                    })
        return resp
    else:
        return send_to_space(recipient_id, "Vous n'appartenez à aucune conversation")


def send_to_space(space_id, message):
    scopes = ['https://www.googleapis.com/auth/chat.bot']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(KEY_FILE, scopes)
    http = Http()
    credentials.authorize(http)
    chat = build('chat', 'v1', http=http)
    resp = chat.spaces().messages().create(
        parent=space_id,
        body={'text': message}).execute()
    return resp


def hangout_circle_model_send(sender_id, circle, text_message):
    circle_targets = db.session.query(UserToCircle).filter(UserToCircle.circle_id == circle.id)
    for target_user in circle_targets:
        target_user_data = db.session.query(User).filter(target_user.user_id == User.id).first()
        if sender_id != target_user_data.id and target_user_data.hangout_space is not None and \
                len(target_user_data.hangout_space) > 0:
            send_to_space(target_user_data.hangout_space, text_message)


def hangout_conversation_model_send(sender_id, conversation, text_message):
    circle = db.session.query(Circle).filter(Circle.id == conversation.circle_id).first()
    hangout_circle_model_send(sender_id, circle, text_message)
