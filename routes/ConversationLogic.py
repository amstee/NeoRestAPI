from flask_restful import Resource
from flask import request
from config.database import db
from models.UserToConversation import UserToConversation
from models.User import User as UserModel
from utils.decorators import secured_route, check_content
from utils.contentChecker import content_checker
from config.sockets import sockets
from utils.apiUtils import *
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc

logger = logger_set(__name__)


class ConversationInvite(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id", "email")
            link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               content["conversation_id"],
                                                               UserToConversation.user_id == user.id).first()
            if link is None:
                resp = FAILED("Lien vers la conversation introuvable")
            else:
                dest = db.session.query(UserModel).filter(UserModel.email == content["email"]).first()
                if dest is None:
                    resp = FAILED("Utilisateur spécifié introuvable")
                else:
                    temp = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                                       link.conversation_id,
                                                                       UserToConversation.user_id == dest.id).first()
                    if temp is not None:
                        resp = FAILED("Utilisateur fait déjà parti de la conversation")
                    elif not link.conversation.circle.has_member(dest):
                        resp = FAILED("L'utilisateur spécifié ne fait pas parti du cercle")
                    elif link.privilege == "ADMIN":
                        new_link = UserToConversation(privilege="STANDARD")
                        new_link.user = dest
                        new_link.conversation = link.conversation
                        db.session.commit()
                        sockets.notify_user(client=dest, is_device=False, p1='conversation',
                                            p2={'event': 'invite', 'conversation_id': link.conversation_id})
                        resp = SUCCESS()
                    else:
                        resp = FAILED("Vous n'avez pas les droits suffisants", 403)
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class ConversationUserPromote(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id", "email")
            link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               content["conversation_id"],
                                                               UserToConversation.user_id == user.id).first()
            if link is None:
                resp = FAILED("Lien vers la conversation introuvable")
            else:
                dest = db.session.query(UserModel).filter(UserModel.email == content["email"]).first()
                if dest is None:
                    resp = FAILED("Utilisateur spécifié introuvable")
                else:
                    temp = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                                       link.conversation_id,
                                                                       UserToConversation.user_id == dest.id).first()
                    if temp is None:
                        resp = FAILED("Utilisateur ne fait pas parti de la conversation")
                    elif link.privilege == "ADMIN":
                        temp.update_content(privilege="ADMIN")
                        link.update_content(privilege="STANDARD")
                        sockets.notify_user(client=dest, is_device=False, p1='conversation', p2={'event': 'promoted',
                                                                                                 'conversation_id':
                                                                                                 link.conversation_id})
                        resp = SUCCESS()
                    else:
                        resp = FAILED("Vous n'avez pas les droits suffisants", 403)
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class ConversationKick(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id", "email")
            link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               content["conversation_id"],
                                                               UserToConversation.user_id == user.id).first()
            if link is None:
                resp = FAILED("Lien vers la conversation introuvable")
            else:
                dest = db.session.query(UserModel).filter(UserModel.email == content["email"]).first()
                if dest is None:
                    resp = FAILED("Utilisateur spécifié introuvable")
                else:
                    temp = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                                       link.conversation_id,
                                                                       UserToConversation.user_id == dest.id).first()
                    if temp is None:
                        resp = FAILED("Utilisateur ne fait pas parti de la conversation")
                    elif link.privilege == "ADMIN":
                        db.session.delete(temp)
                        db.session.commit()
                        link.conversation.check_validity()
                        link.conversation.notify_users(p2={'event': 'kick', 'user': dest.email, 'from': user.email})
                        resp = SUCCESS()
                    else:
                        resp = FAILED("Vous n'avez pas les droits suffisants", 403)
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class ConversationQuit(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id")
            link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               content["conversation_id"],
                                                               UserToConversation.user_id == user.id).first()
            if link is None:
                resp = FAILED("Lien vers la conversation introuvable")
            else:
                conversation = link.conversation
                if link.user_id == user.id:
                    conversation.notify_users(p2={'event': 'quit', 'user': user.email})
                    db.session.delete(link)
                    db.session.commit()
                if conversation.check_validity():
                    conversation.set_other_admin()
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


class ConversationAddDevice(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id")
            link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               content["conversation_id"],
                                                               UserToConversation.user_id == user.id).first()
            if link is None:
                resp = FAILED("Lien vers la conversation introuvable")
            if link.privilege == "ADMIN":
                link.conversation.update_content(device_access=True)
                link.conversation.notify_users(p2={'event': 'device', 'type': 'add'})
                resp = SUCCESS()
            else:
                resp = FAILED("Vous n'avec pas les droits pour effectuer cette action", 403)
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class ConversationRemoveDevice(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("conversation_id")
            link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               content["conversation_id"],
                                                               UserToConversation.user_id == user.id).first()
            if link is None:
                resp = FAILED("Lien vers la conversation introuvable")
            if link.privilege == "ADMIN":
                link.conversation.update_content(device_access=False)
                link.conversation.notify_users(p2={'event': 'device', 'type': 'remove'})
                resp = SUCCESS()
            else:
                resp = FAILED("Vous n'avez pas les droits pour effectuer cette action", 403)
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp
