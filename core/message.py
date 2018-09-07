from flask import request
from config.database import db
from models.Conversation import Conversation
from models.Message import Message
from utils.apiUtils import *
from utils.security import user_has_access_to_message, user_is_owner_of_message
from utils.security import device_has_access_to_message, device_is_owner_of_message
from flask_socketio import emit
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc
from config.log import LOG_MESSAGE_FILE

logger = logger_set(module=__name__, file=LOG_MESSAGE_FILE)


def update(message_id, text_content, client, is_device):
    try:
        message = db.session.query(Message).filter(Message.id == message_id).first()
        if message is None:
            resp = FAILED("Message spécifié introuvable")
        elif not is_device and not user_is_owner_of_message(message, client):
            resp = FAILED("Cet utilisateur ne peut pas modifier ce message", 403)
        elif is_device and not device_is_owner_of_message(message, client):
            resp = FAILED("Cet utilisateur ne peut pas modifier ce message", 403)
        else:
            message.update_content(content=text_content)
            emit('message', {"conversation_id": message.conversation_id, "message_id": message.id, "event": 'update'},
                 room="conversation_" + str(message.conversation_id), namespace='/')
            resp = SUCCESS()
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def message_list(conversation_id, quantity, client, is_device):
    try:
        if quantity <= 0:
            resp = FAILED("Parameter Quantity invalid")
        else:
            conversation = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()
            if not is_device and not conversation.has_members(client):
                resp = FAILED("Cet utilisateur ne peut pas acceder a cette conversation", 403)
            elif is_device and (conversation.circle_id != client.circle_id or conversation.device_access is False):
                resp = FAILED("Cet utilisateur ne peut pas acceder a cette conversation", 403)
            else:
                messages = db.session.query(Message).filter(Message.conversation_id == conversation.id). \
                    limit(quantity).all()
                conv_content = []
                for message in messages:
                    conv_content.append(message.get_content())
                resp = jsonify({"success": True, "content": conv_content})
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def info(message_id, client, is_device):
    try:
        message = db.session.query(Message).filter(Message.id == message_id).first()
        if message is None:
            resp = FAILED("Message spécifié introuvable")
        elif not is_device and user_has_access_to_message(message, client):
            resp = jsonify({"success": True, "content": message.get_content()})
        elif is_device and device_has_access_to_message(message, client):
            resp = jsonify({"success": True, "content": message.get_content()})
        else:
            resp = FAILED("Cet utilisateur ne peut pas voir ce message", 403)
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def delete(message_id, client, is_device):
    try:
        message = db.session.query(Message).filter(Message.id == message_id).first()
        if message is None:
            resp = FAILED("Message spécifié introuvable")
        elif not is_device and not user_is_owner_of_message(message, client):
            resp = FAILED("Cet utilisateur ne peut pas supprimer ce message", 403)
        elif is_device and (not message.is_user or message.device_id != client.id):
            resp = FAILED("Cet utilisateur ne peut pas supprimer ce message", 403)
        else:
            id_message = message.id
            conv_id = message.conversation_id
            db.session.delete(message)
            db.session.commit()
            emit('message', {"conversation_id": conv_id, "message_id": id_message, "event": 'delete'},
                 room="conversation_" + str(conv_id), namespace='/')
            resp = SUCCESS()
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp
