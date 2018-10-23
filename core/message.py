from config.database import db
from models.Conversation import Conversation
from models.Message import Message
from utils.security import user_has_access_to_message, user_is_owner_of_message
from utils.security import device_has_access_to_message, device_is_owner_of_message
from flask_socketio import emit
from exceptions import message as e_message
from exceptions import conversation as e_conversation


def update(message_id, text_content, client, is_device):
    try:
        message = db.session.query(Message).filter(Message.id == message_id).first()
        if message is None:
            raise e_message.MessageNotFound
        if not is_device and not user_is_owner_of_message(message, client):
            raise e_message.ForbiddenAccess
        if is_device and not device_is_owner_of_message(message, client):
            raise e_message.ForbiddenAccess
        message.update_content(content=text_content)
        emit('message', {"conversation_id": message.conversation_id, "message_id": message.id, "event": 'update'},
             room="conversation_" + str(message.conversation_id), namespace='/')
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_message.MessageException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def message_list(conversation_id, quantity, client, is_device):
    try:
        if quantity <= 0:
            raise e_message.MessageQuantityInvalid
        conversation = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conversation is None:
            raise e_conversation.ConversationNotFound
        if not is_device and not conversation.has_members(client):
            raise e_message.ForbiddenAccess
        elif is_device and (conversation.circle_id != client.circle_id or conversation.device_access is False):
            raise e_message.ForbiddenAccess
        messages = db.session.query(Message).filter(Message.conversation_id == conversation.id). \
            limit(quantity).all()
        conv_content = []
        for message in messages:
            conv_content.append(message.get_content())
        response = {
            "data": {"success": True, "content": conv_content},
            "status_code": 200
        }
    except (e_message.MessageException, e_conversation.ConversationException) as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def info(message_id, client, is_device):
    try:
        message = db.session.query(Message).filter(Message.id == message_id).first()
        if message is None:
            raise e_message.MessageNotFound
        if not (not is_device and user_has_access_to_message(message, client)) and \
                not (is_device and device_has_access_to_message(message, client)):
            raise e_message.ForbiddenAccess
        response = {
            "data": {"success": True, "content": message.get_content()},
            "status_code": 200
        }
    except e_message.MessageException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def delete(message_id, client, is_device):
    try:
        message = db.session.query(Message).filter(Message.id == message_id).first()
        if message is None:
            raise e_message.MessageNotFound
        if not is_device and not user_is_owner_of_message(message, client):
            raise e_message.ForbiddenAccess
        if is_device and (not message.is_user or message.device_id != client.id):
            raise e_message.ForbiddenAccess
        id_message = message.id
        conv_id = message.conversation_id
        db.session.delete(message)
        db.session.commit()
        emit('message', {"conversation_id": conv_id, "message_id": id_message, "event": 'delete'},
             room="conversation_" + str(conv_id), namespace='/')
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_message.MessageException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response

