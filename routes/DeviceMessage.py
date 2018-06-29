from flask import request
from flask_restful import Resource
from config.database import db_session
from models.Media import Media
from models.Device import Device
from models.Message import Message
from utils.decorators import checkContent, securedAdminRoute, securedDeviceRoute
from utils.security import deviceHasAccessToMessage
from models.Conversation import Conversation
from utils.contentChecker import contentChecker
from utils.apiUtils import *
from .Facebook import *


class DeviceMessageCreate(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content, admin):
        try:
            contentChecker("files", "device_id", "conversation_id", "text", "directory_name")
            file_list = content["files"]
            device = db_session.query(Device).filter(Device.id==content["device_id"]).first()
            if device is None:
                return (FAILED("Le device spécifié est introuvable"))
            conversation = db_session.query(Conversation).filter(Conversation.id==content["conversation_id"]).first()
            if conversation is None:
                return FAILED("La conversation spécifié est introuvable")
            message = Message(content=content["text"], isUser=False)
            message.conversation = conversation
            message.device = device
            for file in file_list:
                if file in request.files:
                    new_file = Media().setContent(request.files[file], content["directory_name"], message)
                    message.medias.append(new_file)
            db_session.commit()
            info_sender = "[" + conversation.name + "] " + device.name + " : " 
            MessengerConversationModelSend(0, conversation, info_sender + message.text_content)
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class DeviceMessageDelete(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        try:
            contentChecker("message_id")
            message = db_session.query(Message).filter(Message.id==content["message_id"]).first()
            if message is None:
                return FAILED("Message spécifié introuvable")
            if message.isUser or message.device_id != device.id:
                return FAILED("Ce message n'appartient pas a ce device", 403)
            db_session.delete(message)
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class DeviceMessageInfo(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        try:
            contentChecker("message_id")
            message = db_session.query(Message).filter(Message.id==content["message_id"]).first()
            if message is None:
                return FAILED("Message spécifié introuvable")
            if not deviceHasAccessToMessage(message, device):
                return FAILED("Ce device ne peut pas voir ce message", 403)
            return jsonify({"success": True, "content": message.getContent()})
        except Exception as e:
            return FAILED(e)


class DeviceMessageList(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        try:
            contentChecker("conversation_id", "quantity")
            conv = db_session.query(Conversation).filter(Conversation.id==content["conversation_id"]).first()
            if conv.device_access == False or conv.circle.device.id != device.id:
                return FAILED("Ce device ne peut pas voir cette conversation", 403)
            messages = db_session.query(Message).filter(Message.conversation_id==conv.id).limit(content["quantity"]).all()
            return jsonify({"success": True, "content": [message.getContent() for message in messages]})
        except Exception as e:
            return FAILED(e)


class DeviceMessageUpdate(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        try:
            contentChecker("message_id")
            message = db_session.query(Message).filter(Message.id==content["message_id"]).first()
            if message is None:
                return FAILED("Message spécifié introuvable")
            if not deviceHasAccessToMessage(message, device):
                return FAILED("Ce device n'a pas accès a ce message", 403)
            message.updateContent(sent=content["sent"] if "sent" in content else None,
                                  read=content["read"] if "read" in content else None,
                                  content=content["text_message"] if "text_message" in content else None)
            return SUCCESS()
        except Exception as e:
            return FAILED(e)