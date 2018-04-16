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


class MessageCreate(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content):
        try:
            contentChecker("files", "link_id", "text", "directory_name")
            file_list = content["files"]
            link = db_session.query(UserToConversation).filter(UserToConversation.id==content["link_id"]).first()
            if link is None:
                return FAILED("Lien entre utilisateur et conversation introuvable")
            message = Message(content=content["text"])
            message.link = link
            message.conversation = link.conversation
            for file in file_list:
                if file in request.files:
                    new_file = Media().setContent(request.files[file], content["directory_name"], message)
                    message.medias.append(new_file)
            db_session.commit()
            return SUCCESS()
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
                return FAILED("Cet utilisateur ne peut pas supprimer ce message")
            db_session.delete(message)
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
            return FAILED("Cer utilisateur ne peut pas voir ce message")
        except Exception as e:
            return FAILED(e)


class MessageList(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("conversation_id")
            conversation = db_session.query(Conversation).filter(Conversation.id==content["conversation_id"]).first()
            if not conversation.hasMembers(user):
                return FAILED("Cet utilisateur ne peut pas acceder a cette conversation")
            conv_content = []
            for link in conversation.links:
                conv_content.append(link.getMessages())
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
                return FAILED("Cet utilisateur ne peut pas modifier ce message")
            message.updateContent(content=content["text_content"])
            return SUCCESS()
        except Exception as e:
            return FAILED(e)