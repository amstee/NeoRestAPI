from flask import request
from flask_restful import Resource
from config.database import db_session
from models.Media import Media
from models.UserToConversation import UserToConversation
from models.Message import Message
from models.User import User as UserModel
from utils.decorators import checkContent, securedDeviceRoute
from models.Conversation import Conversation
from utils.contentChecker import contentChecker
from utils.apiUtils import *
from flask_socketio import emit
from config.sockets import sockets
from models.MessageToMedia import MessageToMedia
from .Facebook import MessengerConversationModelSend, MessengerUserModelSend


class FirstDeviceMessageSend(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        try:
            contentChecker("email")
            user = db_session.query(UserModel).filter(UserModel.email==content["email"]).first()
            if user is None:
                return FAILED("Utilisateur spécifié introuvable")
            if not device.circle.hasMember(user):
                return FAILED("L'utilisateur n'est pas dans votre cercle")
            conversation = Conversation(device_access=True)
            conversation.circle = device.circle
            conversation.name = "NewConversation"
            link = UserToConversation(privilege="ADMIN")
            link.user = user
            link.conversation = conversation
            message = Message(content=content["text_message"] if "text_message" in content else "", isUser=False)
            message.conversation = conversation
            message.device = device
            media_list = []
            if "files" in content:
                for file in content["files"]:
                    media = Media()
                    media.identifier = file
                    MessageToMedia(message=message, media=media)
                    db_session.commit()
                    media_list.append(media.getSimpleContent())
            db_session.commit()
            sockets.notify_user(user, False, 'conversation',
                                {"conversation_id": conversation.id,
                                 "event": 'invite'})
            info_and_message = "[" + conversation.name + "] " + device.name + " : " + str(message.text_content)
            MessengerUserModelSend(userTarget=user, text_message=info_and_message)
            resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id})
            resp.status_code = 200
            return resp
        except Exception as e:
            return FAILED(e)


class DeviceMessageSend(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        try:
            contentChecker("conversation_id")
            conv = db_session.query(Conversation).filter(Conversation.id==content["conversation_id"]).first()
            if conv is None:
                return FAILED("Conversation introuvable")
            if conv.device_access is False or conv.circle.id != device.circle.id:
                return FAILED("Vous ne pouvez pas acceder a cette conversation", 403)
            message = Message(content=content["text_message"] if "text_message" in content else "", isUser=False)
            message.conversation = conv
            message.device = device
            media_list = []
            if "files" in content:
                for file in content["files"]:
                    media = Media()
                    media.identifier = file
                    MessageToMedia(message=message, media=media)
                    db_session.commit()
                    media_list.append(media.getSimpleContent())
            if not media_list:
                emit('message', {
                    'conversation_id': message.conversation_id,
                    'message': message.getSimpleContent(),
                    'time': message.sent,
                    'sender': device.getSimpleContent(),
                    'media_list': media_list,
                    'status': 'done'},
                     room='conversation_' + str(message.conversation_id), namespace='/')
            else:
                emit('message', {'conversation_id': message.conversation_id, 'message': message.getSimpleContent(),
                                 'status': 'pending'}, room='conversation_' + str(message.conversation_id), namespace='/')
            db_session.commit()
            info_sender = "[" + conv.name + "] " + device.name + " : "
            MessengerConversationModelSend(0, conv, info_sender + message.text_content)
            resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id})
            resp.status_code = 200
            return resp
        except Exception as e:
            return FAILED(e)