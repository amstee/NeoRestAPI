from flask_restful import Resource
from config.database import db
from models.MessageToMedia import MessageToMedia
from models.Media import Media
from models.Device import Device
from models.Message import Message
from utils.decorators import check_content, secured_admin_route, secured_route
from utils.security import device_has_access_to_message
from models.Conversation import Conversation
from utils.contentChecker import content_checker
from utils.apiUtils import *
from bot.facebook import messenger_conversation_model_send
from flask_socketio import emit


class DeviceMessageCreate(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("files", "device_id", "conversation_id", "text", "directory_name")
            device = db.session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is None:
                return FAILED("Le device spécifié est introuvable")
            conversation = db.session.query(Conversation).filter(Conversation.id == content["conversation_id"]).first()
            if conversation is None:
                return FAILED("La conversation spécifié est introuvable")
            message = Message(content=content["text"], is_user=False)
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
            if not media_list:
                emit('message', {
                    'conversation_id': conversation.id,
                    'message': message.get_simple_json_compliant_content(),
                    'time': message.sent.isoformat(),
                    'sender': {"email": "ADMIN"},
                    'media_list': media_list,
                    'status': 'done'},
                     room='conversation_' + str(conversation.id), namespace='/')
            else:
                emit('message', {'conversation_id': conversation.id, 'message':
                                 message.get_simple_json_compliant_content(),
                                 'status': 'pending'}, room='conversation_' + str(conversation.id), namespace='/')
            info_sender = "[" + conversation.name + "] " + device.name + " : "
            try:
                messenger_conversation_model_send(0, conversation, info_sender + message.text_content)
            except Exception:
                pass
            resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id})
            resp.status_code = 200
            return resp
        except Exception as e:
            return FAILED(e)


class DeviceMessageDelete(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("message_id")
            message = db.session.query(Message).filter(Message.id == content["message_id"]).first()
            if message is None:
                return FAILED("Message spécifié introuvable")
            if message.is_user or message.device_id != device.id:
                return FAILED("Ce message n'appartient pas a ce device", 403)
            id_message = message.id
            conv_id = message.conversation_id
            db.session.delete(message)
            db.session.commit()
            emit('message', {"conversation_id": conv_id, "message_id": id_message, "event": 'delete'},
                 room="conversation_" + str(conv_id), namespace='/')
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class DeviceMessageInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("message_id")
            message = db.session.query(Message).filter(Message.id == content["message_id"]).first()
            if message is None:
                return FAILED("Message spécifié introuvable")
            if not device_has_access_to_message(message, device):
                return FAILED("Ce device ne peut pas voir ce message", 403)
            return jsonify({"success": True, "content": message.get_content()})
        except Exception as e:
            return FAILED(e)


class DeviceMessageList(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("conversation_id", "quantity")
            conv = db.session.query(Conversation).filter(Conversation.id == content["conversation_id"]).first()
            if conv.device_access is False or conv.circle.device.id != device.id:
                return FAILED("Ce device ne peut pas voir cette conversation", 403)
            messages = db.session.query(Message).filter(Message.conversation_id == conv.id).\
                limit(content["quantity"]).all()
            return jsonify({"success": True, "content": [message.get_content() for message in messages]})
        except Exception as e:
            return FAILED(e)


class DeviceMessageUpdate(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("message_id")
            message = db.session.query(Message).filter(Message.id == content["message_id"]).first()
            if message is None:
                return FAILED("Message spécifié introuvable")
            if not device_has_access_to_message(message, device):
                return FAILED("Ce device n'a pas accès a ce message", 403)
            message.update_content(sent=content["sent"] if "sent" in content else None,
                                   read=content["read"] if "read" in content else None,
                                   content=content["text_message"] if "text_message" in content else None)
            emit('message', {"conversation_id": message.conversation_id, "message_id": message.id, "event": 'update'},
                 room="conversation_" + str(message.conversation_id), namespace='/')
            return SUCCESS()
        except Exception as e:
            return FAILED(e)
