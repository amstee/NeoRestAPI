from flask_restful import Resource
from config.database import db_session
from models.UserToConversation import UserToConversation
from models.User import User as UserModel
from utils.decorators import securedRoute, checkContent
from utils.contentChecker import contentChecker
from utils.apiUtils import *


class ConversationInvite(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("link_id", "email")
            link = db_session.query(UserToConversation).filter(UserToConversation.id==content["link_id"]).first()
            if link is None:
                return FAILED("Lien vers la conversation introuvable")
            dest = db_session.query(UserModel).filter(UserModel.email==content["email"]).first()
            if dest is None:
                return FAILED("Utilisateur spécifié introuvable")
            temp = db_session.query(UserToConversation).filter(UserToConversation.conversation_id==link.conversation_id
                                                               ,UserToConversation.user_id==dest.id)
            if temp is not None:
                return FAILED("Utilisateur fait déjà parti de la conversation")
            if link.user_id == user.id and link.privilege == "ADMIN":
                new_link = UserToConversation(privilege="STANDARD")
                new_link.user = dest
                new_link.conversation = link.conversation
                db_session.commit()
            else:
                return FAILED("Vous n'avez pas les droits suffisants")
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class ConversationUserPromote(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("link_id", "email")
            link = db_session.query(UserToConversation).filter(UserToConversation.id == content["link_id"]).first()
            if link is None:
                return FAILED("Lien vers la conversation introuvable")
            dest = db_session.query(UserModel).filter(UserModel.email == content["email"]).first()
            if dest is None:
                return FAILED("Utilisateur spécifié introuvable")
            temp = db_session.query(UserToConversation).filter(UserToConversation.conversation_id == link.conversation_id
                                                               , UserToConversation.user_id == dest.id)
            if temp is None:
                return FAILED("Utilisateur ne fait pas parti de la conversation")
            if link.user_id == user.id and link.privilege == "ADMIN":
                temp.updateContent(privilege="ADMIN")
                link.updateContent(privilege="STANDARD")
            else:
                return FAILED("Vous n'avez pas les droits suffisants")
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class ConversationKick(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("link_id", "email")
            link = db_session.query(UserToConversation).filter(UserToConversation.id == content["link_id"]).first()
            if link is None:
                return FAILED("Lien vers la conversation introuvable")
            dest = db_session.query(UserModel).filter(UserModel.email == content["email"]).first()
            if dest is None:
                return FAILED("Utilisateur spécifié introuvable")
            temp = db_session.query(UserToConversation).filter(UserToConversation.conversation_id == link.conversation_id
                                                               , UserToConversation.user_id == dest.id)
            if temp is None:
                return FAILED("Utilisateur ne fait pas parti de la conversation")
            if link.user_id == user.id and link.privilege == "ADMIN":
                db_session.remove(temp)
                db_session.commit()
                link.conversation.checkValidity()
            else:
                return FAILED("Vous n'avez pas les droits suffisants")
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class ConversationQuit(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("link_id")
            link = db_session.query(UserToConversation).filter(UserToConversation.id == content["link_id"]).first()
            if link is None:
                return FAILED("Lien vers la conversation introuvable")
            conversation = link.conversation
            if link.user_id == user.id:
                db_session.remove(link)
                db_session.commit()
            if conversation.checkValidity():
                conversation.setOtherAdmin()
        except Exception as e:
            return FAILED(e)


class ConversationAddDevice(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("link_id")
            link = db_session.query(UserToConversation).filter(UserToConversation.id == content["link_id"]).first()
            if link is None:
                return FAILED("Lien vers la conversation introuvable")
            if link.user_id == user.id and link.privilege == "ADMIN":
                link.conversation.updateContent(device_access=True)
            else:
                return FAILED("Vous n'avec pas les droits pour effectuer cette action")
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class ConversationRemoveDevice(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("link_id")
            link = db_session.query(UserToConversation).filter(UserToConversation.id == content["link_id"]).first()
            if link is None:
                return FAILED("Lien vers la conversation introuvable")
            if link.user_id == user.id and link.privilege == "ADMIN":
                link.conversation.updateContent(device_access=False)
            else:
                return FAILED("Vous n'avec pas les droits pour effectuer cette action")
            return SUCCESS()
        except Exception as e:
            return FAILED(e)