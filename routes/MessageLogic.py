from flask import request
from flask_restful import Resource
from config.database import db
from models.UserToConversation import UserToConversation
from models.Conversation import Conversation
from models.Media import Media
from models.Message import Message
from models.Circle import Circle
from models.User import User as UserModel
from models.MessageToMedia import MessageToMedia
from utils.decorators import secured_route, check_content
from utils.contentChecker import content_checker
from utils.apiUtils import *
from config.sockets import sockets
from flask_socketio import emit
from bot.facebook import messenger_circle_model_send, messenger_conversation_model_send
from config.log import logger_set

logger = logger_set(__name__)


class FirstMessageToDeviceSend(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("circle_id")
            circle = db.session.query(Circle).filter(Circle.id == content["circle_id"]).first()
            if circle is None:
                resp = FAILED("Cercle spécifié introuvable")
            elif not circle.has_member(user):
                resp = FAILED("Vous n'appartenez pas a ce cercle", 403)
            else:
                conversation = Conversation(name=content["conversation_name"] if "conversation_name" in content else
                                            circle.name, device_access=True)
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
                        MessageToMedia(message=message, media=media)
                        db.session.commit()
                        media_list.append(media.get_simple_content())
                db.session.commit()
                sockets.notify_user(circle.device, True, 'conversation',
                                    {"conversation_id": conversation.id,
                                     "event": 'invite'})
                info_sender = "[" + conversation.name + "] " + user.first_name + " : "
                try:
                    messenger_circle_model_send(0, circle, info_sender + message.text_content)
                except Exception:
                    pass
                resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id})
                resp.status_code = 200
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
            return resp
        except Exception as e:
            return FAILED(e)


class FirstMessageSend(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("email", "circle_id")
            dest = db.session.query(UserModel).filter(UserModel.email == content["email"]).first()
            circle = db.session.query(Circle).filter(Circle.id == content["circle_id"]).first()
            if dest is None:
                resp = FAILED("Destinataire introuvable")
            elif circle is None:
                resp = FAILED("Cercle spécifié introuvable")
            elif not circle.has_member(user):
                resp = FAILED("Vous n'appartenez pas a ce cercle", 403)
            elif not circle.has_member(dest) and circle.has_member(user):
                resp = FAILED("Ce cercle ne contient pas l'utilisateur recherché", 403)
            else:
                conversation = Conversation()
                conversation.circle = circle
                UserToConversation(privilege="ADMIN", user=user, conversation=conversation)
                UserToConversation(privilege="STANDARD", user=dest, conversation=conversation)
                message = Message(content=content["text_message"] if "text_message" in content else "")
                message.conversation = conversation
                media_list = []
                if "files" in content:
                    for file in content["files"]:
                        media = Media()
                        media.identifier = file
                        MessageToMedia(message=message, media=media)
                        db.session.commit()
                        media_list.append(media.get_simple_content())
                db.session.commit()
                sockets.notify_user(dest, False, 'conversation',
                                    {"conversation_id": conversation.id,
                                     "event": 'invite'})
                info_sender = "[" + conversation.name + "] " + user.first_name + " : "
                try:
                    messenger_circle_model_send(0, circle, info_sender + message.text_content)
                except Exception:
                    pass
                resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id,
                                'conversation_id': message.conversation_id})
                resp.status_code = 200
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
            return resp
        except Exception as e:
            return FAILED(e)


class MessageSend(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id")
            link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               content["conversation_id"],
                                                               UserToConversation.user_id == user.id).first()
            if link is None:
                return FAILED("Conversation introuvable", 403)
            else:
                message = Message(content=content["text_message"] if "text_message" in content else "")
                message.conversation = link.conversation
                message.link = link
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
                    print(message.conversation_id)
                    emit('message', {
                        'conversation_id': message.conversation_id,
                        'message': message.get_simple_json_compliant_content(),
                        'time': message.sent.isoformat(),
                        'sender': user.get_simple_json_compliant_content(),
                        'media_list': media_list,
                        'status': 'done'},
                         room='conversation_' + str(message.conversation_id), namespace='/')
                else:
                    emit('message', {'conversation_id': message.conversation_id,
                                     'message': message.get_simple_json_compliant_content(),
                                     'status': 'pending'}, room='conversation_' + str(message.conversation_id),
                         namespace='/')
                conversation = db.session.query(Conversation).filter(link.conversation_id == Conversation.id).first()
                info_sender = "[" + link.conversation.name + "] " + user.first_name + " : "
                try:
                    messenger_conversation_model_send(link.user_id, conversation, info_sender + message.text_content)
                except Exception:
                    pass
                resp = jsonify({"success": True, 'media_list': media_list, 'message_id': message.id})
                resp.status_code = 200
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
            return resp
        except Exception as e:
            return FAILED(e)
