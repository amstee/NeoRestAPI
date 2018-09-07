from flask import request
from config.database import db
from models.UserToConversation import UserToConversation
from models.Conversation import Conversation
from models.User import User as UserModel
from config.sockets import sockets
from utils.apiUtils import *
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc
from config.log import LOG_CONVERSATION_FILE

logger = logger_set(module=__name__, file=LOG_CONVERSATION_FILE)


def set_device(conversation_id, client, is_device):
    try:
        privilege = ""
        if not is_device:
            link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               conversation_id,
                                                               UserToConversation.user_id == client.id).first()
            if link is None:
                resp = FAILED("Lien vers la conversation introuvable")
                logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                            request.method, request.host, request.path,
                            request.content_type, request.data, resp.status_code)
                return resp
            conversation = link.conversation
            privilege = link.privilege
        else:
            conversation = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()
        if privilege == "ADMIN":
            conversation.update_content(device_access=(not conversation.device_access))
            if conversation.device_access:
                conversation.notify_users(p2={'event': 'device', 'type': 'add'})
            else:
                conversation.notify_users(p2={'event': 'device', 'type': 'remove'})
            resp = SUCCESS()
        elif is_device and conversation.device_access:
            conversation.update_content(device_access=False)
            conversation.notify_users(p2={'event': 'device', 'type': 'remove'})
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


def invite(conversation_id, email, client, is_device):
    try:
        if not is_device:
            link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               conversation_id,
                                                               UserToConversation.user_id == client.id).first()
            if link is None:
                resp = FAILED("Lien vers la conversation introuvable")
                logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                            request.method, request.host, request.path,
                            request.content_type, request.data, resp.status_code)
                return resp
            conversation = link.conversation
        else:
            conversation = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()
        dest = db.session.query(UserModel).filter(UserModel.email == email).first()
        if dest is None:
            resp = FAILED("Utilisateur spécifié introuvable")
        else:
            temp = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                               conversation_id,
                                                               UserToConversation.user_id == dest.id).first()
            if temp is not None:
                resp = FAILED("Utilisateur fait déjà parti de la conversation")
            elif not conversation.circle.has_member(dest):
                resp = FAILED("L'utilisateur spécifié ne fait pas parti du cercle")
            else:
                new_link = UserToConversation(privilege="STANDARD")
                new_link.user = dest
                new_link.conversation = conversation
                db.session.commit()
                sockets.notify_user(client=dest, is_device=False, p1='conversation',
                                    p2={'event': 'invite', 'conversation_id': conversation_id})
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


def conversation_quit(conversation_id, user):
    try:
        link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                           conversation_id,
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


def conversation_kick(conversation_id, email, user):
    try:
        link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                           conversation_id,
                                                           UserToConversation.user_id == user.id).first()
        if link is None:
            resp = FAILED("Lien vers la conversation introuvable")
        else:
            dest = db.session.query(UserModel).filter(UserModel.email == email).first()
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


def user_promote(conversation_id, email, user):
    try:
        link = db.session.query(UserToConversation).filter(UserToConversation.conversation_id ==
                                                           conversation_id,
                                                           UserToConversation.user_id == user.id).first()
        if link is None:
            resp = FAILED("Lien vers la conversation introuvable")
        else:
            dest = db.session.query(UserModel).filter(UserModel.email == email).first()
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
