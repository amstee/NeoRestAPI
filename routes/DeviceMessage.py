from flask_restful import Resource
from flask import request
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
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc
from config.log import LOG_DEVICE_FILE

logger = logger_set(module=__name__, file=LOG_DEVICE_FILE)


class DeviceMessageCreate(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("files", "device_id", "conversation_id", "text", "directory_name")
            device = db.session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is None:
                resp = FAILED("Le device spécifié est introuvable")
            else:
                conversation = db.session.query(Conversation).filter(Conversation.id ==
                                                                     content["conversation_id"]).first()
                if conversation is None:
                    resp = FAILED("La conversation spécifié est introuvable")
                else:
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
                                         'status': 'pending'}, room='conversation_' + str(conversation.id),
                             namespace='/')
                    info_sender = "[" + conversation.name + "] " + device.name + " : "
                    try:
                        messenger_conversation_model_send(0, conversation, info_sender + message.text_content)
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


class DeviceMessageDelete(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("message_id")
            message = db.session.query(Message).filter(Message.id == content["message_id"]).first()
            if message is None:
                resp = FAILED("Message spécifié introuvable")
            elif message.is_user or message.device_id != device.id:
                resp = FAILED("Ce message n'appartient pas a ce device", 403)
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


class DeviceMessageInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("message_id")
            message = db.session.query(Message).filter(Message.id == content["message_id"]).first()
            if message is None:
                resp = FAILED("Message spécifié introuvable")
            elif not device_has_access_to_message(message, device):
                resp = FAILED("Ce device ne peut pas voir ce message", 403)
            else:
                resp = jsonify({"success": True, "content": message.get_content()})
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class DeviceMessageList(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("conversation_id", "quantity")
            conv = db.session.query(Conversation).filter(Conversation.id == content["conversation_id"]).first()
            if conv.device_access is False or conv.circle.device.id != device.id:
                resp = FAILED("Ce device ne peut pas voir cette conversation", 403)
            else:
                messages = db.session.query(Message).filter(Message.conversation_id == conv.id).\
                    limit(content["quantity"]).all()
                resp = jsonify({"success": True, "content": [message.get_content() for message in messages]})
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class DeviceMessageUpdate(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("message_id")
            message = db.session.query(Message).filter(Message.id == content["message_id"]).first()
            if message is None:
                resp = FAILED("Message spécifié introuvable")
            elif not device_has_access_to_message(message, device):
                resp = FAILED("Ce device n'a pas accès a ce message", 403)
            else:
                message.update_content(sent=content["sent"] if "sent" in content else None,
                                       read=content["read"] if "read" in content else None,
                                       content=content["text_message"] if "text_message" in content else None)
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
