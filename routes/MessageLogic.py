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
from .Facebook import *


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
                return FAILED("Vous n'appartenez pas a ce cercle", 403)
            conversation = Conversation(name=content["conversation_name"] if "conversation_name" in content else circle.name, device_access=True)
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
            info_sender = "[" + conversation.name + "] " + user.first_name + " : " 
            MessengerCircleModelSend(0, circle, info_sender + message.text_content)
            return SUCCESS()
        except Exception as e:
            return FAILED(e)

class FirstMessageSend(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("email", "circle_id")
            dest = db_session.query(UserModel).filter(UserModel.email==content["email"]).first()
            circle = db_session.query(Circle).filter(Circle.id==content["circle_id"]).first()
            if dest is None:
                return FAILED("Destinataire introuvable")
            if circle is None:
                return FAILED("Cercle spécifié introuvable")
            if not circle.hasMember(user):
                return FAILED("Vous n'appartenez pas a ce cercle", 403)
            if not circle.hasMember(dest) and circle.hasMember(user):
                return FAILED("Ce cercle ne contient pas l'utilisateur recherché", 403)
            conversation = Conversation()
            conversation.circle = circle
            link1 = UserToConversation(privilege="ADMIN", user=user, conversation=conversation)
            link2 = UserToConversation(privilege="STANDARD", user=dest, conversation=conversation)
            message = Message(content=content["text_message"] if "text_message" in content else None)
            message.conversation = conversation
            message.link = link1
            if "files" in content:
                for file in content["files"]:
                    if file in request.files:
                        new_file = Media().setContent(request.files[file], str(message.conversation_id), message)
                        message.medias.append(new_file)
            db_session.commit()
            info_sender = "[" + conversation.name + "] " + user.first_name + " : " 
            MessengerCircleModelSend(0, circle, info_sender + message.text_content)
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class MessageSend(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("conversation_id")
            link = db_session.query(UserToConversation).filter(UserToConversation.conversation_id==content["conversation_id"],
                                                               UserToConversation.user_id==user.id).first()
            if link is None:
                return FAILED("Conversation introuvable", 403)
            message = Message(content=content["text_message"] if "text_message" in content else None)
            message.conversation = link.conversation
            message.link = link
            if "files" in content:
                for file in content["files"]:
                    if file in request.files:
                        new_file = Media().setContent(request.files[file], str(message.conversation_id), message)
                        message.medias.append(new_file)
            db_session.commit()
            conversation = db_session.query(Conversation).filter(link.conversation_id == Conversation.id).first()
            info_sender = "[" + link.conversation.name + "] " + user.first_name + " : "
            MessengerConversationModelSend(link.user_id, conversation, info_sender + message.text_content)
            return SUCCESS()
        except Exception as e:
            return FAILED(e)