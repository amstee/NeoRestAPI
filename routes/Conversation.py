from flask_restful import Resource
from config.database import db_session
from models.Circle import Circle
from models.Conversation import Conversation
from models.UserToConversation import UserToConversation
from utils.decorators import securedRoute, checkContent, securedAdminRoute, securedDeviceRoute
from utils.contentChecker import contentChecker
from utils.apiUtils import *


class ConversationCreate(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content, admin):
        try:
            contentChecker("conversation_name", "circle_id")
            circle = db_session.query(Circle).filter(Circle.id==content["circle_id"]).first()
            if circle is None:
                return FAILED("Cercle introuvable")
            conv = Conversation(name=content["conversation_name"])
            conv.circle = circle
            db_session.commit()
            return jsonify({"success": True, "content": conv.getSimpleContent()})
        except Exception as e:
            return FAILED(e)


class ConversationDelete(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content, admin):
        try:
            contentChecker("conversation_id")
            conv = db_session.query(Conversation).filter(Conversation.id==content["conversation_id"]).first()
            if conv is None:
                return FAILED("Conversation introuvable")
            db_session.delete(conv)
            db_session.commit()
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class ConversationInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("conversation_id")
            conv = db_session.query(Conversation).filter(Conversation.id==content["conversation_id"]).first()
            if conv is None:
                return FAILED("Conversation introuvable")
            if conv.hasMembers(user):
                return jsonify({"success": True, "content": conv.getContent()})
            return FAILED("L'utilisateur n'a pas acces a cette conversation", 403)
        except Exception as e:
            return FAILED(e)


class ConversationDeviceInfo(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        try:
            contentChecker("conversation_id")
            conv = db_session.query(Conversation).filter(Conversation.id==content["conversation_id"]).first()
            if conv is None:
                return FAILED("Conversation introuvable")
            if conv.device_access and conv.circle.device.device_id == device.id:
                return jsonify({"success": True, "content": conv.getContent()})
            return FAILED("Le device n'a pas acces a cette conversation")
        except Exception as e:
            return FAILED(e)


class ConversationList(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("circle_id")
            circle = db_session.query(Circle).filter(Circle.id==content["circle_id"]).first()
            if circle is None:
                return FAILED("Cercle introuvable")
            if not circle.hasMember(user):
                return FAILED("L'utilisateur n'appartient pas au cercle spécifié", 403)
            convs = db_session.query(Conversation).join(UserToConversation).filter(
                Conversation.circle_id==circle.id,
                UserToConversation.user_id==user.id
            ).all()
            return jsonify({"success": True, "content": [conv.getSimpleContent() for conv in convs]})
        except Exception as e:
            return FAILED(e)


class ConversationDeviceList(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        try:
            contentChecker("circle_id")
            circle = db_session.query(Circle).filter(Circle.id == content["circle_id"]).first()
            if circle is None:
                return FAILED("Cercle introuvable")
            if circle.device.id == device.id:
                convs = db_session.query(Conversation).filter(Conversation.device_access==True).all()
                return jsonify({"success": True, "content": [conv.getSimpleContent() for conv in convs]})
            else:
                return FAILED("Device n'a pas acces a ce cercle")
        except Exception as e:
            return FAILED(e)


class ConversationUpdate(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("conversation_id")
            link = db_session.query(UserToConversation).filter(UserToConversation.user_id==user.id,
                                                               UserToConversation.conversation_id==content["conversation_id"]).first()
            if link is None:
                return FAILED("Cet utilisateur n'appartient pas a cette conversation", 403)
            if link.privilege == "ADMIN":
                link.conversation.updateContent(name=content["conversation_name"] if "conversation_name" in content else None,
                                                created=content["created"] if "created" in content else None,
                                                device_access=content["device_access"] if "device_access" in content else None)
                return jsonify({"success": True, "content": link.conversation.getSimpleContent()})
            else:
                return FAILED("Cet utilisateur n'a pas les droits suffisants pour modifier cette conversation", 403)
        except Exception as e:
            return FAILED(e)