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
from bot.facebook import messenger_conversation_model_send
from bot.hangout import hangout_conversation_model_send
from exceptions import conversation as e_conversation
from exceptions import account as e_account
from exceptions import circle as e_cirle


def message_send(content, conversation_id, device):
    try:
        conv = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv is None:
            raise e_conversation.ConversationNotFound
        elif conv.device_access is False or conv.circle.id != device.circle.id:
            raise e_conversation.UserForbiddenAccess
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


def first_message_to_user(content, email, device):
    try:
        user = db.session.query(UserModel).filter(UserModel.email == email).first()
        if user is None:
            raise e_account.UserNotFound
        elif not device.circle.has_member(user):
            raise e_cirle.UserNotPartOfCircle
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
        response = {
                "data": {"success": True, 'media_list': media_list, 'message_id': message.id},
                "status_code": 200
        }
    except (e_cirle.CircleException, e_account.AccountException) as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response
