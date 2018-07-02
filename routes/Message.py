from flask import request
from flask_restful import Resource
from config.database import db_session
from models.UserToConversation import UserToConversation
from models.Conversation import Conversation
from models.Media import Media
from models.Message import Message
from utils.decorators import securedRoute, checkContent, securedAdminRoute
from utils.contentChecker import contentChecker
from utils.apiUtils import *
from utils.security import userHasAccessToMessage, userIsOwnerOfMessage
from .Facebook import MessengerConversationModelSend
from flask_socketio import emit


class MessageCreate(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content, admin):
        try:
            contentChecker("files", "link_id", "text", "directory_name")
            link = db_session.query(UserToConversation).filter(UserToConversation.id==content["link_id"]).first()
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
                    db_session.commit()
                    media_list.append(media.getSimpleContent())
            db_session.commit()
            if not media_list:
                emit('message', {
                    'conversation_id': link.conversation_id,
                    'message': message.getSimpleContent(),
                    'time': message.sent,
                    'sender': {'email': 'ADMIN'},
                    'media_list': media_list,
                    'status': 'done'},
                     room='conversation_' + str(link.conversation_id), namespace='/')
            else:
                emit('message', {'conversation_id': link.conversation_id, 'message': message.getSimpleContent(),
                                 'status': 'pending'}, room='conversation_' + str(link.conversation_id), namespace='/')
            conversation = db_session.query(Conversation).filter(link.conversation_id == Conversation.id).first()
            info_sender = "[" + link.conversation.name + "] " + admin.first_name + " : " 
            MessengerConversationModelSend(link.user_id, conversation, info_sender + message.text_content)
            resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id})
            resp.status_code = 200
            return resp
        except Exception as e:
            return FAILED(e)


class MessageDelete(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("message_id")
            message = db_session.query(Message).filter(Message.id==content["message_id"]).first()
            if message is None:
                return FAILED("Message spécifié introuvable")
            if not userIsOwnerOfMessage(message, user):
                return FAILED("Cet utilisateur ne peut pas supprimer ce message", 403)
            id = message.id
            conv_id = message.conversation_id
            db_session.delete(message)
            db_session.commit()
            emit('message', {"conversation_id": conv_id, "message_id": id, "event": 'delete'}
                 , room="conversation_" + str(conv_id), namespace='/')
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class MessageInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("message_id")
            message = db_session.query(Message).filter(Message.id==content["message_id"]).first()
            if message is None:
                return FAILED("Message spécifié introuvable")
            if userHasAccessToMessage(message, user):
                return jsonify({"success": True, "content": message.getContent()})
            return FAILED("Cer utilisateur ne peut pas voir ce message", 403)
        except Exception as e:
            return FAILED(e)


class MessageList(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("conversation_id", "quantity")
            if content["quantity"] <= 0:
                return FAILED("Parameter Quantity invalid")
            conversation = db_session.query(Conversation).filter(Conversation.id==content["conversation_id"]).first()
            if not conversation.hasMembers(user):
                return FAILED("Cet utilisateur ne peut pas acceder a cette conversation", 403)
            messages = db_session.query(Message).filter(Message.conversation_id==conversation.id).limit(content["quantity"]).all()
            conv_content = []
            for message in messages:
                conv_content.append(message.getContent())
            return jsonify({"success": True, "content": conv_content})
        except Exception as e:
            return FAILED(e)


class MessageUpdate(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("message_id", "text_content")
            message = db_session.query(Message).filter(Message.id==content["message_id"]).first()
            if message is None:
                return FAILED("Message spécifié introuvable")
            if not userIsOwnerOfMessage(message, user):
                return FAILED("Cet utilisateur ne peut pas modifier ce message", 403)
            message.updateContent(content=content["text_content"])
            emit('message', {"conversation_id": message.conversation_id, "message_id": message.id, "event": 'update'}
                 , room="conversation_" + str(message.conversation_id), namespace='/')
            return SUCCESS()
        except Exception as e:
            return FAILED(e)