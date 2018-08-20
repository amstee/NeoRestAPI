from flask_restful import Resource
from config.database import db
from models.Circle import Circle
from models.Conversation import Conversation
from models.UserToConversation import UserToConversation
from utils.decorators import secured_route, check_content, secured_admin_route
from utils.contentChecker import content_checker
from utils.apiUtils import *


class ConversationCreate(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("conversation_name", "circle_id")
            circle = db.session.query(Circle).filter(Circle.id == content["circle_id"]).first()
            if circle is None:
                return FAILED("Cercle introuvable")
            conv = Conversation(name=content["conversation_name"])
            conv.circle = circle
            db.session.commit()
            return jsonify({"success": True, "content": conv.get_simple_content()})
        except Exception as e:
            return FAILED(e)


class ConversationDelete(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("conversation_id")
            conv = db.session.query(Conversation).filter(Conversation.id == content["conversation_id"]).first()
            if conv is None:
                return FAILED("Conversation introuvable")
            db.session.delete(conv)
            db.session.commit()
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class ConversationInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id")
            conv = db.session.query(Conversation).filter(Conversation.id == content["conversation_id"]).first()
            if conv is None:
                return FAILED("Conversation introuvable")
            if conv.has_members(user):
                return jsonify({"success": True, "content": conv.get_content()})
            return FAILED("L'utilisateur n'a pas acces a cette conversation", 403)
        except Exception as e:
            return FAILED(e)


class ConversationDeviceInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("conversation_id")
            conv = db.session.query(Conversation).filter(Conversation.id == content["conversation_id"]).first()
            if conv is None:
                return FAILED("Conversation introuvable")
            if conv.device_access and conv.circle.device.id == device.id:
                return jsonify({"success": True, "content": conv.get_content()})
            return FAILED("Le device n'a pas acces a cette conversation")
        except Exception as e:
            return FAILED(e)


class ConversationList(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("circle_id")
            circle = db.session.query(Circle).filter(Circle.id == content["circle_id"]).first()
            if circle is None:
                return FAILED("Cercle introuvable")
            if not circle.has_member(user):
                return FAILED("L'utilisateur n'appartient pas au cercle spécifié", 403)
            convs = db.session.query(Conversation).join(UserToConversation).filter(
                Conversation.circle_id == circle.id,
                UserToConversation.user_id == user.id
            ).all()
            return jsonify({"success": True, "content": [conv.get_simple_content() for conv in convs]})
        except Exception as e:
            return FAILED(e)


class ConversationDeviceList(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("circle_id")
            circle = db.session.query(Circle).filter(Circle.id == content["circle_id"]).first()
            if circle is None:
                return FAILED("Cercle introuvable")
            if circle.device.id == device.id:
                convs = db.session.query(Conversation).filter(Conversation.device_access is True).all()
                return jsonify({"success": True, "content": [conv.get_simple_content() for conv in convs]})
            else:
                return FAILED("Device n'a pas acces a ce cercle")
        except Exception as e:
            return FAILED(e)


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
                return FAILED("Cet utilisateur n'appartient pas a cette conversation", 403)
            if link.privilege == "ADMIN":
                link.conversation.update_content(name=content["conversation_name"] if "conversation_name"
                                                                                     in content else None,
                                                 created=content["created"] if "created" in content else None,
                                                 device_access=content["device_access"] if "device_access"
                                                 in content else None)
                link.conversation.notify_users(p2={'event': 'update'})
                return jsonify({"success": True, "content": link.conversation.get_simple_content()})
            else:
                return FAILED("Cet utilisateur n'a pas les droits suffisants pour modifier cette conversation", 403)
        except Exception as e:
            return FAILED(e)
