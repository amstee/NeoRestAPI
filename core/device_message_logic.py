from flask import request
from config.database import db
from models.Media import Media
from models.UserToConversation import UserToConversation
from models.Message import Message
from models.User import User as UserModel
from models.Conversation import Conversation
from utils.apiUtils import *
from flask_socketio import emit
from config.sockets import sockets
from models.MessageToMedia import MessageToMedia
from bot.facebook import messenger_conversation_model_send, messenger_user_model_send
from bot.hangout import hangout_conversation_model_send
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc
from config.log import LOG_DEVICE_FILE

logger = logger_set(module=__name__, file=LOG_DEVICE_FILE)


def message_send(content, conversation_id, device):
    try:
        conv = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv is None:
            resp = FAILED("Conversation introuvable")
        elif conv.device_access is False or conv.circle.id != device.circle.id:
            resp = FAILED("Vous ne pouvez pas acceder a cette conversation", 403)
        else:
            message = Message(content=content["text_message"] if "text_message" in content else "", is_user=False)
            message.conversation = conv
            message.device = device
            media_list = []
            if "files" in content:
                for file in content["files"]:
                    media = Media()
                    media.identifier = file
                    MessageToMedia(message=message, media=media)
                    db.session.commit()
                    media_list.append(media.get_simple_content())
            db.session.commit()
            if not media_list:
                emit('message', {
                    'conversation_id': message.conversation_id,
                    'message': message.get_simple_json_compliant_content(),
                    'time': message.sent.isoformat(),
                    'sender': device.get_simple_json_compliant_content(),
                    'media_list': media_list,
                    'status': 'done'},
                     room='conversation_' + str(message.conversation_id), namespace='/')
            else:
                emit('message', {'conversation_id': message.conversation_id, 'message':
                     message.get_simple_json_compliant_content(),
                                 'status': 'pending'}, room='conversation_' + str(message.conversation_id),
                     namespace='/')
            info_sender = "[" + conv.name + "] " + device.name + " : "
            try:
                messenger_conversation_model_send(0, conv, info_sender + message.text_content)
            except Exception:
                pass
            try:
                hangout_conversation_model_send(0, conv, info_sender + message.text_content)
            except Exception:
                pass
            resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id})
            resp.status_code = 200
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def first_message_to_user(content, email, device):
    try:
        user = db.session.query(UserModel).filter(UserModel.email == email).first()
        if user is None:
            resp = FAILED("Utilisateur spécifié introuvable")
        elif not device.circle.has_member(user):
            resp = FAILED("L'utilisateur n'est pas dans votre cercle")
        else:
            conversation = Conversation(device_access=True)
            conversation.circle = device.circle
            conversation.name = "NewConversation"
            link = UserToConversation(privilege="ADMIN")
            link.user = user
            link.conversation = conversation
            message = Message(content=content["text_message"] if "text_message" in content else "", is_user=False)
            message.conversation = conversation
            message.device = device
            media_list = []
            if "files" in content:
                for file in content["files"]:
                    media = Media()
                    media.identifier = file
                    MessageToMedia(message=message, media=media)
                    db.session.commit()
                    media_list.append(media.get_simple_content())
            db.session.commit()
            sockets.notify_user(user, False, 'conversation',
                                {"conversation_id": conversation.id,
                                 "event": 'invite'})
            info_and_message = "[" + conversation.name + "] " + device.name + " : " + str(message.text_content)
            try:
                messenger_conversation_model_send(0, conversation, info_and_message)
            except Exception:
                pass
            try:
                hangout_conversation_model_send(0, conversation, info_and_message)
            except Exception:
                pass
            resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id})
            resp.status_code = 200
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp
