from flask_restful import Resource
from config.database import db_session
from models.UserToConversation import UserToConversation
from models.User import User as UserModel
from utils.decorators import secured_route, check_content
from utils.contentChecker import content_checker
from config.sockets import sockets
from utils.apiUtils import *


class ConversationInvite(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id", "email")
            link = db_session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               content["conversation_id"],
                                                               UserToConversation.user_id == user.id).first()
            if link is None:
                return FAILED("Lien vers la conversation introuvable")
            dest = db_session.query(UserModel).filter(UserModel.email == content["email"]).first()
            if dest is None:
                return FAILED("Utilisateur spécifié introuvable")
            temp = db_session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               link.conversation_id,
                                                               UserToConversation.user_id == dest.id).first()
            if temp is not None:
                return FAILED("Utilisateur fait déjà parti de la conversation")
            if not link.conversation.circle.has_member(dest):
                return FAILED("L'utilisateur spécifié ne fait pas parti du cercle")
            if link.privilege == "ADMIN":
                new_link = UserToConversation(privilege="STANDARD")
                new_link.user = dest
                new_link.conversation = link.conversation
                db_session.commit()
                sockets.notify_user(client=dest, is_device=False, p1='conversation',
                                    p2={'event': 'invite', 'conversation_id': link.conversation_id})
            else:
                return FAILED("Vous n'avez pas les droits suffisants", 403)
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class ConversationUserPromote(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id", "email")
            link = db_session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               content["conversation_id"],
                                                               UserToConversation.user_id == user.id).first()
            if link is None:
                return FAILED("Lien vers la conversation introuvable")
            dest = db_session.query(UserModel).filter(UserModel.email == content["email"]).first()
            if dest is None:
                return FAILED("Utilisateur spécifié introuvable")
            temp = db_session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               link.conversation_id,
                                                               UserToConversation.user_id == dest.id).first()
            if temp is None:
                return FAILED("Utilisateur ne fait pas parti de la conversation")
            if link.privilege == "ADMIN":
                temp.update_content(privilege="ADMIN")
                link.update_content(privilege="STANDARD")
                sockets.notify_user(client=dest, is_device=False, p1='conversation', p2={'event': 'promoted',
                                                                                         'conversation_id':
                                                                                         link.conversation_id})
                return SUCCESS()
            else:
                return FAILED("Vous n'avez pas les droits suffisants", 403)
        except Exception as e:
            return FAILED(e)


class ConversationKick(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id", "email")
            link = db_session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               content["conversation_id"],
                                                               UserToConversation.user_id == user.id).first()
            if link is None:
                return FAILED("Lien vers la conversation introuvable")
            dest = db_session.query(UserModel).filter(UserModel.email == content["email"]).first()
            if dest is None:
                return FAILED("Utilisateur spécifié introuvable")
            temp = db_session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               link.conversation_id,
                                                               UserToConversation.user_id == dest.id).first()
            if temp is None:
                return FAILED("Utilisateur ne fait pas parti de la conversation")
            if link.privilege == "ADMIN":
                db_session.delete(temp)
                db_session.commit()
                link.conversation.check_validity()
                link.conversation.notify_users(p2={'event': 'kick', 'user': dest.email, 'from': user.email})
            else:
                return FAILED("Vous n'avez pas les droits suffisants", 403)
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class ConversationQuit(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id")
            link = db_session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               content["conversation_id"],
                                                               UserToConversation.user_id == user.id).first()
            if link is None:
                return FAILED("Lien vers la conversation introuvable")
            conversation = link.conversation
            if link.user_id == user.id:
                conversation.notify_users(p2={'event': 'quit', 'user': user.email})
                db_session.delete(link)
                db_session.commit()
            if conversation.check_validity():
                conversation.set_other_admin()
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class ConversationAddDevice(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id")
            link = db_session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               content["conversation_id"],
                                                               UserToConversation.user_id == user.id).first()
            if link is None:
                return FAILED("Lien vers la conversation introuvable")
            if link.privilege == "ADMIN":
                link.conversation.update_content(device_access=True)
                link.conversation.notify_users(p2={'event': 'device', 'type': 'add'})
            else:
                return FAILED("Vous n'avec pas les droits pour effectuer cette action", 403)
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class ConversationRemoveDevice(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id")
            link = db_session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               content["conversation_id"],
                                                               UserToConversation.user_id == user.id).first()
            if link is None:
                return FAILED("Lien vers la conversation introuvable")
            if link.privilege == "ADMIN":
                link.conversation.update_content(device_access=False)
                link.conversation.notify_users(p2={'event': 'device', 'type': 'remove'})
            else:
                return FAILED("Vous n'avez pas les droits pour effectuer cette action", 403)
            return SUCCESS()
        except Exception as e:
            return FAILED(e)
