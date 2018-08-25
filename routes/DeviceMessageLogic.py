from flask_restful import Resource
from flask import request
from config.database import db
from models.Media import Media
from models.UserToConversation import UserToConversation
from models.Message import Message
from models.User import User as UserModel
from utils.decorators import check_content, secured_route
from models.Conversation import Conversation
from utils.contentChecker import content_checker
from utils.apiUtils import *
from flask_socketio import emit
from config.sockets import sockets
from models.MessageToMedia import MessageToMedia
from bot.facebook import messenger_conversation_model_send, messenger_user_model_send
from config.log import logger_set

logger = logger_set(__name__)


class FirstDeviceMessageSend(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            content_checker("email")
            user = db.session.query(UserModel).filter(UserModel.email == content["email"]).first()
            if user is None:
                return FAILED("Utilisateur spécifié introuvable")
            if not device.circle.has_member(user):
                return FAILED("L'utilisateur n'est pas dans votre cercle")
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
                messenger_user_model_send(user_target=user, text_message=info_and_message)
            except Exception:
                pass
            resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id})
            resp.status_code = 200
            return resp
        except Exception as e:
            return FAILED(e)


class DeviceMessageSend(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            content_checker("conversation_id")
            conv = db.session.query(Conversation).filter(Conversation.id == content["conversation_id"]).first()
            if conv is None:
                return FAILED("Conversation introuvable")
            if conv.device_access is False or conv.circle.id != device.circle.id:
                return FAILED("Vous ne pouvez pas acceder a cette conversation", 403)
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
                     'status': 'pending'}, room='conversation_' + str(message.conversation_id), namespace='/')
            info_sender = "[" + conv.name + "] " + device.name + " : "
            try:
                messenger_conversation_model_send(0, conv, info_sender + message.text_content)
            except Exception:
                pass
            resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id})
            resp.status_code = 200
            return resp
        except Exception as e:
            return FAILED(e)
