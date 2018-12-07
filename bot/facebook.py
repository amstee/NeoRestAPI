from config.database import db
from models.User import User
from models.Circle import Circle
from models.UserToCircle import UserToCircle
from models.Conversation import Conversation
from models.UserToConversation import UserToConversation
from models.Message import Message
from config.facebook import SECRET_KEY, PAGE_ACCESS_TOKEN
from models.Media import Media
from exceptions import conversation as e_conversation
from exceptions import media as e_media
from models.MessageToMedia import MessageToMedia
import base64
from flask_socketio import emit
import requests
import jwt
import datetime
import json
import io
from utils.log import logger_set

logger = logger_set(__name__)

with open('config.json') as data_file:
    neo_config = json.load(data_file)

PORT = neo_config["project"]["port"]
HOST = neo_config["project"]["host"]
BASE_ENDPOINT = "http://"+str(HOST)+":"+str(PORT)


def core_upload(media_id, url, client):
    try:
        logger.debug("STARTING CORE UPLOAD")
        media = db.session.query(Media).filter(Media.id == media_id).first()
        logger.debug("CORE UPLOAD URL: %s", url)
        part_a = url.split('?')
        logger.debug("CORE UPLOAD URL_A: %s", part_a)
        part_b = part_a[0].split('//')
        logger.debug("CORE UPLOAD URL_B: %s", part_b)
        filename = str(url.split('?')[0]).split('/')[6]
        logger.debug("CORE UPLOAD SPLIT: %s", filename)
        media.set_content_bot(filename)
        #media.upload_bot(url, filename)
        db.session.commit()
        logger.debug("STARTING CORE UPLOAD DONE")
        if media.is_attached_to_message():
            message = media.message_link.message
            emit('message', {
                'conversation_id': message.conversation.id,
                'message': message.get_simple_json_compliant_content(),
                'sender': client.get_simple_json_compliant_content(),
                'media': media.get_simple_content(),
                'status': 'done'},
                 room='conversation_' + str(message.conversation.id), namespace='/')
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_media.MediaException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def core_message_send(content, conversation_id, user):
    try:
        link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                           conversation_id,
                                                           UserToConversation.user_id == user.id).first()
        if link is None:
            raise e_conversation.ConversationNotFound
        message = Message(content=content["text_message"] if "text_message" in content else "")
        message.conversation = link.conversation
        message.link = link
        media_list = []
        if "files" in content:
            for file in content["files"]:
                media = Media()
                media.identifier = file
                MessageToMedia(message=message, media=media)
                db.session.commit()
                media_list.append(media.get_simple_content())
        db.session.commit()
        response = {
            "data": {"success": True, 'media_list': media_list, 'message_id': message.id},
            "status_code": 200
        }
    except e_conversation.ConversationException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def encode_post_back_payload(facebook_psid, message_text, link, attachment_images):
    try:
        payload = {
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30, seconds=1),
            'iat': datetime.datetime.utcnow(),
            'facebook_psid': facebook_psid,
            'user_id': link.user_id,
            'link_id': link.id,
            'message_text': message_text,
            'images': attachment_images
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
        return token.decode()
    except Exception as e:
        return str(e)


def push_images_to_api(user, conv_id, message, attachment_images):
    logger.debug("I AM IN IMAGE PUSH")
    for url in attachment_images:
        response = core_message_send(content={"text_message": message, "files": [url]},
                                     conversation_id=conv_id, user=user)
        logger.debug("CORE_MESSAGE :\n%s", response)
        response = core_upload(response["data"]["media_list"][0]["id"], url, user)
        logger.debug("CORE_UPLOAD :\n%s", response)


def handle_conversation_payload(message_payload):
    try:
        payload = jwt.decode(message_payload, SECRET_KEY)
        try:
            link = db.session.query(UserToConversation).filter(UserToConversation.id == payload["link_id"],
                                                               UserToConversation.user_id == payload["user_id"]).first()
            user = db.session.query(User).filter(User.id == payload["user_id"]).first()
            if len(payload["images"]) == 0:
                message = Message(content=payload["message_text"])
                message.link = link
                message.conversation = link.conversation
                db.session.commit()
                emit('message', {
                    'conversation_id': message.conversation_id,
                    'message': message.get_simple_json_compliant_content(),
                    'time': message.sent.isoformat(),
                    'sender': user.get_simple_json_compliant_content(),
                    'media_list': [],
                    'status': 'done'},
                     room='conversation_' + str(message.conversation_id), namespace='/')
                message.conversation.mobile_notification(title="Message",
                                                         body=user.first_name + " vous à envoyer un message.")
            else:
                push_images_to_api(user=user, conv_id=link.conversation.id,
                                   message=payload["message_text"], attachment_images=payload["images"])
        except Exception as e:
            return "Une erreur est survenue : " + str(e)
    except jwt.ExpiredSignatureError:
        return 'Message expiré, renvoyez le message'
    except jwt.InvalidTokenError:
        return 'Message expiré, renvoyez le message'


def send_message(recipient_id, message_text):
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
    return data, r.status_code


def message_choice(sender_id, message_text, user, attachment_images):
    quick_replies = []
    for user_to_conv in user.conversation_links:
        conv = db.session.query(Conversation).filter(Conversation.id == user_to_conv.conversation_id).first()
        payload = encode_post_back_payload(sender_id, message_text, user_to_conv, attachment_images)
        quick_replies.append({"content_type": "text", "title": conv.name, "payload": payload})
    return quick_replies


def send_message_choice(recipient_id, message_text, attachment_images):
    user = db.session.query(User).filter(User.facebook_psid == recipient_id).first()
    if len(user.conversation_links) > 0:
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
                "text": "Choisissez une conversation",
                "quick_replies": message_choice(recipient_id, message_text, user, attachment_images)
            }
        })
        r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
        return data, r.status_code
    else:
        return send_message(recipient_id, "Vous n'appartenez à aucune conversation")


def messenger_user_model_send(user_target, text_message):
    if user_target.facebook_psid is not None and user_target.facebook_psid != "":
        send_message(user_target.facebook_psid, text_message)
        return True
    return False


def messenger_circle_model_send(sender_id, circle, text_message):
    circle_targets = db.session.query(UserToCircle).filter(UserToCircle.circle_id == circle.id)
    for targetUser in circle_targets:
        targer_user_data = db.session.query(User).filter(targetUser.user_id == User.id).first()
        if sender_id != targer_user_data.id and targer_user_data.facebook_psid is not None:
            send_message(targer_user_data.facebook_psid, text_message)


def messenger_conversation_model_send(sender_id, conversation, text_message):
    circle = db.session.query(Circle).filter(Circle.id == conversation.circle_id).first()
    messenger_circle_model_send(sender_id, circle, text_message)


def is_user_linked(facebook_psid):
    user = db.session.query(User).filter(User.facebook_psid == facebook_psid).first()
    if user is not None:
        return True
    return False


def link_user_to_facebook(api_token, psid):
        try:
            payload = jwt.decode(api_token, SECRET_KEY)
            try:
                user = db.session.query(User).filter(User.id == payload['sub']).first()
                if user is not None:
                    old_user = db.session.query(User).filter(User.facebook_psid == str(psid)).first()
                    if old_user is not None:
                        old_user.update_content(facebook_psid=None)
                    user.update_content(facebook_psid=str(psid))
                    return "Bienvenue sur NEO, " + payload['first_name'] + " " + payload['last_name'] + " !"
                else:
                    return 'Token invalide !'
            except Exception as e:
                return "Une erreur est survenue, merci de réessayer ultérieurement"
        except jwt.ExpiredSignatureError:
            return 'La token a expiré, authentifiez vous a nouveau'
        except jwt.InvalidTokenError:
            return 'Token invalide, authentifiez vous a nouveau'
