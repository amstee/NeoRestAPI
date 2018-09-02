from flask_restful import Resource
from flask import request
from config.database import db
from models.Circle import Circle
from models.Conversation import Conversation
from models.UserToConversation import UserToConversation
from utils.decorators import secured_route, check_content, secured_admin_route
from utils.contentChecker import content_checker
from utils.apiUtils import *
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc
from config.log import LOG_CONVERSATION_FILE

logger = logger_set(module=__name__, file=LOG_CONVERSATION_FILE)


class ConversationCreate(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("conversation_name", "circle_id")
            circle = db.session.query(Circle).filter(Circle.id == content["circle_id"]).first()
            if circle is None:
                resp = FAILED("Cercle introuvable")
            else:
                conv = Conversation(name=content["conversation_name"])
                conv.circle = circle
                db.session.commit()
                resp = jsonify({"success": True, "content": conv.get_simple_content()})
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class ConversationDelete(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("conversation_id")
            conv = db.session.query(Conversation).filter(Conversation.id == content["conversation_id"]).first()
            if conv is None:
                resp = FAILED("Conversation introuvable")
            else:
                db.session.delete(conv)
                db.session.commit()
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


class ConversationInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id")
            conv = db.session.query(Conversation).filter(Conversation.id == content["conversation_id"]).first()
            if conv is None:
                resp = FAILED("Conversation introuvable")
            elif conv.has_members(user):
                resp = jsonify({"success": True, "content": conv.get_content()})
            else:
                resp = FAILED("L'utilisateur n'a pas acces a cette conversation", 403)
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class ConversationDeviceInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("conversation_id")
            conv = db.session.query(Conversation).filter(Conversation.id == content["conversation_id"]).first()
            if conv is None:
                resp = FAILED("Conversation introuvable")
            elif conv.device_access and conv.circle.device.id == device.id:
                resp = jsonify({"success": True, "content": conv.get_content()})
            else:
                resp = FAILED("Le device n'a pas acces a cette conversation")
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class ConversationList(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("circle_id")
            circle = db.session.query(Circle).filter(Circle.id == content["circle_id"]).first()
            if circle is None:
                resp = FAILED("Cercle introuvable")
            elif not circle.has_member(user):
                resp = FAILED("L'utilisateur n'appartient pas au cercle spécifié", 403)
            else:
                convs = db.session.query(Conversation).join(UserToConversation).filter(
                    Conversation.circle_id == circle.id,
                    UserToConversation.user_id == user.id
                ).all()
                resp = jsonify({"success": True, "content": [conv.get_simple_content() for conv in convs]})
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class ConversationDeviceList(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("circle_id")
            circle = db.session.query(Circle).filter(Circle.id == content["circle_id"]).first()
            if circle is None:
                resp = FAILED("Cercle introuvable")
            elif circle.device.id == device.id:
                convs = db.session.query(Conversation).filter(Conversation.device_access is True).all()
                resp = jsonify({"success": True, "content": [conv.get_simple_content() for conv in convs]})
            else:
                resp = FAILED("Device n'a pas acces a ce cercle")
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class ConversationUpdate(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id")
            link = db.session.query(UserToConversation).filter(UserToConversation.user_id == user.id,
                                                               UserToConversation.conversation_id ==
                                                               content["conversation_id"]).first()
            if link is None:
                resp = FAILED("Cet utilisateur n'appartient pas a cette conversation", 403)
            elif link.privilege == "ADMIN":
                link.conversation.update_content(name=content["conversation_name"] if "conversation_name"
                                                                                     in content else None,
                                                 created=content["created"] if "created" in content else None,
                                                 device_access=content["device_access"] if "device_access"
                                                 in content else None)
                link.conversation.notify_users(p2={'event': 'update'})
                resp = jsonify({"success": True, "content": link.conversation.get_simple_content()})
            else:
                resp = FAILED("Cet utilisateur n'a pas les droits suffisants pour modifier cette conversation", 403)
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp
