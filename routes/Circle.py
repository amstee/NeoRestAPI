from flask import request
from flask_restful import Resource
from config.database import db_session
from models.Circle import Circle
from utils.decorators import securedRoute, checkContent, securedAdminRoute, securedDeviceRoute
from utils.contentChecker import contentChecker
from models.UserToCircle import UserToCircle
from utils.apiUtils import *


class CircleCreate(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("name")
            circle = Circle(content["name"])
            link = UserToCircle(privilege="REGULAR")
            link.circle = circle
            link.user = user
            db_session.commit()
            resp = jsonify({"success": True, "content": circle.getSimpleContent()})
        except Exception as e:
            return FAILED(e)
        return resp


class CircleDelete(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content, admin):
        try:
            contentChecker("circle_id")
            circle = db_session.query(Circle).filter_by(id=content["circle_id"]).first()
            if circle is not None:
                db_session.delete(circle)
                db_session.commit()
                return SUCCESS()
            resp = FAILED("Le cercle est introuvable")
            resp.status_code = 401
        except Exception as e:
            return FAILED(e)
        return resp


class CircleUpdate(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("circle_id")
            circle = db_session.query(Circle).filter_by(id=content["circle_id"]).first()
            if circle is not None:
                if not circle.hasMember(user):
                    return FAILED("Cet utilisateur n'a pas access a ce cercle", 403)
                circle.updateContent(name=content["name"] if "name" in content else None,
                                     created=content["created"] if "created" in content else None)
                circle.notify_users()
                return SUCCESS()
            resp = FAILED("Le cercle est introuvable")
            resp.status_code = 401
        except Exception as e:
            return FAILED(e)
        return resp


class CircleInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("circle_id")
            circle = db_session.query(Circle).filter_by(id=content["circle_id"]).first()
            if circle is not None:
                if not circle.hasMember(user):
                    return FAILED("Cet utilisateur n'a pas access a ce cercle", 403)
                return jsonify({"success": True, "content": circle.getContent()})
            resp = FAILED("Le cercle est introuvable")
            resp.status_code = 401
        except Exception as e:
            return FAILED(e)
        return resp


class CircleDeviceInfo(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        try:
            return jsonify({"success": True, "content": device.circle.getContent()})
        except Exception as e:
            return FAILED(e)


class CircleList(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            circle_list = []
            for link in user.circleLink:
                if link.circle not in circle_list:
                    circle_list.append(link.circle)
            resp = jsonify({"success": True, "content": [circle.getSimpleContent() for circle in circle_list]})
        except Exception as e:
            return FAILED(e)
        return resp
