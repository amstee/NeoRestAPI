from flask_restful import Resource
from flask import request
from config.database import db
from models.Circle import Circle
from utils.decorators import secured_route, check_content, secured_admin_route
from utils.contentChecker import content_checker
from models.UserToCircle import UserToCircle
from utils.apiUtils import *
from config.log import logger_set
from traceback import format_exc as traceback_format_exc

logger = logger_set(__name__)


class CircleCreate(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("name")
            circle = Circle(content["name"])
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


class CircleDelete(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("circle_id")
            circle = db.session.query(Circle).filter_by(id=content["circle_id"]).first()
            if circle is not None:
                db.session.delete(circle)
                db.session.commit()
                circle.notify_users(p1='circle', p2={'event': 'delete'})
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


class CircleUpdate(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("circle_id")
            circle = db.session.query(Circle).filter_by(id=content["circle_id"]).first()
            if circle is not None:
                if not circle.has_member(user):
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


class CircleInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("circle_id")
            circle = db.session.query(Circle).filter_by(id=content["circle_id"]).first()
            if circle is not None:
                if not circle.has_member(user):
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


class CircleDeviceInfo(Resource):
    @secured_route
    def post(self, device):
        try:
            resp = jsonify({"success": True, "content": device.circle.get_content()})
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class CircleList(Resource):
    @secured_route
    def post(self, user):
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
