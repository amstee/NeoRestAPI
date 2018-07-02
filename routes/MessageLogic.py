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
from config.sockets import sockets
from flask_socketio import emit
from .Facebook import MessengerCircleModelSend, MessengerConversationModelSend


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
            message = Message(content=content["text_message"] if "text_message" in content else "")
            message.conversation = conversation
            message.link = link
            media_list = []
            if "files" in content:
                for file in content["files"]:
                    media = Media()
                    media.identifier = file
                    media.message = message
                    db_session.commit()
                    media_list.append(media.getSimpleContent())
            db_session.commit()
            sockets.notify_user(circle.device, True, 'conversation',
                                {"conversation_id": conversation.id,
                                 "event": 'invite'})
            info_sender = "[" + conversation.name + "] " + user.first_name + " : "
            MessengerCircleModelSend(0, circle, info_sender + message.text_content)
            resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id})
            resp.status_code = 200
            return resp
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
            message = Message(content=content["text_message"] if "text_message" in content else "")
            message.conversation = conversation
            media_list = []
            if "files" in content:
                for file in content["files"]:
                    media = Media()
                    media.identifier = file
                    media.message = message
                    db_session.commit()
                    media_list.append(media.getSimpleContent())
            db_session.commit()
            sockets.notify_user(dest, False, 'conversation',
                                {"conversation_id": conversation.id,
                                 "event": 'invite'})
            info_sender = "[" + conversation.name + "] " + user.first_name + " : "
            MessengerCircleModelSend(0, circle, info_sender + message.text_content)
            resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id})
            resp.status_code = 200
            return resp
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
            message = Message(content=content["text_message"] if "text_message" in content else "")
            message.conversation = link.conversation
            message.link = link
            media_list = []
            if "files" in content:
                for file in content["files"]:
                    media = Media()
                    media.identifier = file
                    media.message = message
                    db_session.commit()
                    media_list.append(media.getSimpleContent())
            if not media_list:
                emit('message', {
                    'conversation_id': message.conversation_id,
                    'message': message.getSimpleContent(),
                    'time': message.sent,
                    'sender': user.getSimpleContent(),
                    'media_list': media_list,
                    'status': 'done'},
                     room='conversation_' + str(message.conversation_id), namespace='/')
            else:
                emit('message', {'conversation_id': message.conversation_id, 'message': message.getSimpleContent(),
                                 'status': 'pending'}, room='conversation_' + str(message.conversation_id), namespace='/')
            db_session.commit()
            conversation = db_session.query(Conversation).filter(link.conversation_id == Conversation.id).first()
            info_sender = "[" + link.conversation.name + "] " + user.first_name + " : "
            MessengerConversationModelSend(link.user_id, conversation, info_sender + message.text_content)
            resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id})
            resp.status_code = 200
            return resp
        except Exception as e:
            return FAILED(e)