from flask import request
from config.database import db
from models.Circle import Circle
from utils.contentChecker import content_checker
from models.UserToCircle import UserToCircle
from utils.apiUtils import *
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc
from config.log import LOG_CIRCLE_FILE

logger = logger_set(module=__name__, file=LOG_CIRCLE_FILE)


def create(name, user):
    try:
        circle = Circle(name)
        link = UserToCircle(privilege="REGULAR")
        link.circle = circle
        link.user = user
        db.session.commit()
        resp = jsonify({"success": True, "content": circle.get_simple_content()})
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def update(content, client, is_device):
    try:
        content_checker("circle_id")
        circle = db.session.query(Circle).filter(Circle.id == content["circle_id"]).first()
        if circle is not None:
            if (not is_device and not circle.has_member(client)) or \
                    (is_device and client.circle_id != circle.id):
                resp = FAILED("Cet utilisateur n'a pas access a ce cercle", 403)
            else:
                circle.update_content(name=content["name"] if "name" in content else None,
                                      created=content["created"] if "created" in content else None)
                circle.notify_users(p1='circle', p2={'event': 'update'})
                resp = SUCCESS()
        else:
            resp = FAILED("Le cercle est introuvable")
            resp.status_code = 404
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def delete(circle_id):
    try:
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if circle is not None:
            circle.notify_users(p1='circle', p2={'event': 'delete'})
            db.session.delete(circle)
            db.session.commit()
            resp = SUCCESS()
        else:
            resp = FAILED("Le cercle est introuvable")
            resp.status_code = 404
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def get_info(circle_id, client, is_device):
    try:
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if circle is not None:
            if (not is_device and not circle.has_member(client)) or \
                    (is_device and client.circle_id != circle_id):
                resp = FAILED("Cet utilisateur n'a pas access à ce cercle", 403)
            else:
                resp = jsonify({"success": True, "content": circle.get_content()})
        else:
            resp = FAILED("Le cercle est introuvable")
            resp.status_code = 401
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def get_list(user):
    try:
        circle_list = []
        for link in user.circle_link:
            if link.circle not in circle_list:
                circle_list.append(link.circle)
        resp = jsonify({"success": True, "content": [circle.get_simple_content() for circle in circle_list]})
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp
