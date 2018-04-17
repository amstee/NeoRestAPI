from flask import request
from flask_restful import Resource
from config.database import db_session
from models.UserToConversation import UserToConversation
from models.Conversation import Conversation
from models.Media import Media
from models.Message import Message
from models.Circle import Circle
from models.User import User as UserModel
from utils.decorators import securedRoute, checkContent
from utils.contentChecker import contentChecker
from utils.apiUtils import *


class FirstMessageToDeviceSend(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("circle_id")
            circle = db_session.query(Circle).filter(Circle.id==content["circle_id"]).first()
            if circle is None:
                return FAILED("Cercle spécifié introuvable")
            if not circle.hasMember(user):
                return FAILED("Impossible de communiquer avec ce device")
            conversation = Conversation(device_access=True)
            conversation.circle = circle
            link = UserToConversation(privilege="ADMIN")
            link.user = user
            link.conversation = conversation
            message = Message(content=content["text_message"] if "text_message" in content else None)
            message.conversation = conversation
            message.link = link
            if "files" in content:
                for file in content["files"]:
                    if file in request.files:
                        new_file = Media().setContent(request.files[file], str(message.conversation_id), message)
                        message.medias.append(new_file)
            db_session.commit()
            return SUCCESS()
        except Exception as e:
            return FAILED(e)

class FirstMessageSend(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("user_id", "circle_id")
            dest = db_session.query(UserModel).filter(UserModel.id==content["user_id"]).first()
            circle = db_session.query(Circle).filter(Circle.id==content["circle_id"]).first()
            if dest is None:
                return FAILED("Destinataire introuvable")
            if circle is None:
                return FAILED("Cercle spécifié introuvable")
            if not circle.hasMember(dest) and circle.hasMember(user):
                return FAILED("Ce cercle ne contient pas l'utilisateur recherché")
            conversation = Conversation()
            conversation.circle = circle
            link1 = UserToConversation(privilege="ADMIN")
            link2 = UserToConversation(privilege="STANDARD")
            link1.user = user
            link1.conversation = conversation
            link2.user = dest
            link2.conversation = conversation
            message = Message(content=content["text_message"] if "text_message" in content else None)
            message.conversation = conversation
            message.link = link1
            if "files" in content:
                for file in content["files"]:
                    if file in request.files:
                        new_file = Media().setContent(request.files[file], str(message.conversation_id), message)
                        message.medias.append(new_file)
            db_session.commit()
            return SUCCESS()
            # conversation = db_session.query(Conversation).join(UserToConversation).filter(UserToConversation.user_id.in_((dest.id, user.id))).first()
        except Exception as e:
            return FAILED(e)


class MessageSend(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("link_id")
            link = db_session.query(UserToConversation).filter(UserToConversation.id==content["link_id"]).first()
            if link is None:
                return FAILED("Lien vers la conversation introuvable")
            if link.user_id != user.id:
                return FAILED("Cet utilisateur ne peut pas envoyer de message dans cette conversation")
            message = Message(content=content["text_message"] if "text_message" in content else None)
            message.conversation = link.conversation
            if "files" in content:
                for file in content["files"]:
                    if file in request.files:
                        new_file = Media().setContent(request.files[file], str(message.conversation_id), message)
                        message.medias.append(new_file)
            db_session.commit()
            return SUCCESS()
        except Exception as e:
            return FAILED(e)