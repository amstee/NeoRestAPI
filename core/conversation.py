from flask import request
from config.database import db
from models.Circle import Circle
from models.Conversation import Conversation
from models.UserToConversation import UserToConversation
from utils.apiUtils import *
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc
from config.log import LOG_CONVERSATION_FILE

logger = logger_set(module=__name__, file=LOG_CONVERSATION_FILE)


def update(content, conversation_id, client, is_device):
    try:
        if not is_device:
            link = db.session.query(UserToConversation).filter(UserToConversation.user_id == client.id,
                                                               UserToConversation.conversation_id ==
                                                               conversation_id).first()
            if link is None:
                resp = FAILED("Cet utilisateur n'appartient pas a cette conversation", 403)
                logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                            request.method, request.host, request.path,
                            request.content_type, request.data, resp.status_code)
                return resp
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
        else:
            conversation = db.session.query(Conversation).filter(Conversation.device_access is True,
                                                                 Conversation.circle_id == client.circle_id).first()
            if conversation is None:
                resp = FAILED("Cet utilisateur n'appartient pas a cette conversation", 403)
                logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                            request.method, request.host, request.path,
                            request.content_type, request.data, resp.status_code)
                return resp
            else:
                conversation.update_content(name=content["conversation_name"] if "conversation_name"
                                            in content else None,
                                            created=content["created"] if "created" in content else None,
                                            device_access=content["device_access"] if "device_access"
                                            in content else None)
                conversation.notify_users(p2={'event': 'update'})
                resp = jsonify({"success": True, "content": conversation.get_simple_content()})
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def conversation_list(circle_id, client, is_device):
    try:
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if circle is None:
            resp = FAILED("Cercle introuvable")
        elif (not is_device and not circle.has_member(client) or
              (is_device and circle.device_id != client.id)):
            resp = FAILED("L'utilisateur n'appartient pas au cercle spécifié", 403)
        elif not is_device:
            convs = db.session.query(Conversation).join(UserToConversation).filter(
                Conversation.circle_id == circle.id,
                UserToConversation.user_id == client.id
            ).all()
            resp = jsonify({"success": True, "content": [conv.get_simple_content() for conv in convs]})
        else:
            convs = db.session.query(Conversation).filter(Conversation.device_access is True,
                                                          Conversation.circle_id == client.circle_id).all()
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


def info(conversation_id, client, is_device):
    try:
        conv = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()
        if conv is None:
            resp = FAILED("Conversation introuvable")
        elif (not is_device and conv.has_members(client)) or \
                (is_device and (conv.device_access and conv.circle_id == client.circle_id)):
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


def admin_create(name, circle_id):
    try:
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if circle is None:
            resp = FAILED("Cercle introuvable")
        else:
            conv = Conversation(name=name)
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


def admin_delete(conversation_id):
    try:
        conv = db.session.query(Conversation).filter(Conversation.id == conversation_id).first()
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
