from flask_restful import Resource
from flask import request
from config.database import db
from models.UserToConversation import UserToConversation
from models.Conversation import Conversation
from models.Media import Media
from models.Message import Message
from utils.decorators import secured_route, check_content, secured_admin_route
from utils.contentChecker import content_checker
from utils.apiUtils import *
from utils.security import user_has_access_to_message, user_is_owner_of_message
from bot.facebook import messenger_conversation_model_send
from flask_socketio import emit
from config.log import logger_set

logger = logger_set(__name__)


class MessageCreate(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            content_checker("files", "link_id", "text", "directory_name")
            link = db.session.query(UserToConversation).filter(UserToConversation.id == content["link_id"]).first()
            if link is None:
                return FAILED("Lien entre utilisateur et conversation introuvable")
            message = Message(content=content["text"])
            message.link = link
            message.conversation = link.conversation
            media_list = []
            if "files" in content:
                for file in content["files"]:
                    media = Media()
                    media.identifier = file
                    media.message = message
                    db.session.commit()
                    media_list.append(media.get_simple_content())
            db.session.commit()
            if not media_list:
                emit('message', {
                    'conversation_id': link.conversation_id,
                    'message': message.get_simple_json_compliant_content(),
                    'time': message.sent.isoformat(),
                    'sender': {'email': 'ADMIN'},
                    'media_list': media_list,
                    'status': 'done'},
                     room='conversation_' + str(link.conversation_id), namespace='/')
            else:
                emit('message', {'conversation_id': link.conversation_id, 'message':
                     message.get_simple_json_compliant_content(),
                     'status': 'pending'}, room='conversation_' + str(link.conversation_id), namespace='/')
            conversation = db.session.query(Conversation).filter(link.conversation_id == Conversation.id).first()
            info_sender = "[" + link.conversation.name + "] " + admin.first_name + " : "
            try:
                messenger_conversation_model_send(link.user_id, conversation, info_sender + message.text_content)
            except Exception:
                pass
            resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id})
            resp.status_code = 200
            return resp
        except Exception as e:
            return FAILED(e)


class MessageDelete(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            content_checker("message_id")
            message = db.session.query(Message).filter(Message.id == content["message_id"]).first()
            if message is None:
                return FAILED("Message spécifié introuvable")
            if not user_is_owner_of_message(message, user):
                return FAILED("Cet utilisateur ne peut pas supprimer ce message", 403)
            id_message = message.id
            conv_id = message.conversation_id
            db.session.delete(message)
            db.session.commit()
            emit('message', {"conversation_id": conv_id, "message_id": id_message, "event": 'delete'},
                 room="conversation_" + str(conv_id), namespace='/')
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class MessageInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            content_checker("message_id")
            message = db.session.query(Message).filter(Message.id == content["message_id"]).first()
            if message is None:
                return FAILED("Message spécifié introuvable")
            if user_has_access_to_message(message, user):
                return jsonify({"success": True, "content": message.get_content()})
            return FAILED("Cer utilisateur ne peut pas voir ce message", 403)
        except Exception as e:
            return FAILED(e)


class MessageList(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            content_checker("conversation_id", "quantity")
            if content["quantity"] <= 0:
                return FAILED("Parameter Quantity invalid")
            conversation = db.session.query(Conversation).filter(Conversation.id == content["conversation_id"]).first()
            if not conversation.has_members(user):
                return FAILED("Cet utilisateur ne peut pas acceder a cette conversation", 403)
            messages = db.session.query(Message).filter(Message.conversation_id == conversation.id).\
                limit(content["quantity"]).all()
            conv_content = []
            for message in messages:
                conv_content.append(message.get_content())
            return jsonify({"success": True, "content": conv_content})
        except Exception as e:
            return FAILED(e)


class MessageUpdate(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            content_checker("message_id", "text_content")
            message = db.session.query(Message).filter(Message.id == content["message_id"]).first()
            if message is None:
                return FAILED("Message spécifié introuvable")
            if not user_is_owner_of_message(message, user):
                return FAILED("Cet utilisateur ne peut pas modifier ce message", 403)
            message.update_content(content=content["text_content"])
            emit('message', {"conversation_id": message.conversation_id, "message_id": message.id, "event": 'update'},
                 room="conversation_" + str(message.conversation_id), namespace='/')
            return SUCCESS()
        except Exception as e:
            return FAILED(e)
