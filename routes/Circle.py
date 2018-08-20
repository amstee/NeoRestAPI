from flask_restful import Resource
from config.database import db
from models.Circle import Circle
from utils.decorators import secured_route, check_content, secured_admin_route
from utils.contentChecker import content_checker
from models.UserToCircle import UserToCircle
from utils.apiUtils import *


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
        except Exception as e:
            return FAILED(e)
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
                return SUCCESS()
            resp = FAILED("Le cercle est introuvable")
            resp.status_code = 404
        except Exception as e:
            return FAILED(e)
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
                    return FAILED("Cet utilisateur n'a pas access a ce cercle", 403)
                circle.update_content(name=content["name"] if "name" in content else None,
                                      created=content["created"] if "created" in content else None)
                circle.notify_users(p1='circle', p2={'event': 'update'})
                return SUCCESS()
            resp = FAILED("Le cercle est introuvable")
            resp.status_code = 404
        except Exception as e:
            return FAILED(e)
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
                    return FAILED("Cet utilisateur n'a pas access à ce cercle", 403)
                return jsonify({"success": True, "content": circle.get_content()})
            resp = FAILED("Le cercle est introuvable")
            resp.status_code = 401
        except Exception as e:
            return FAILED(e)
        return resp


class CircleDeviceInfo(Resource):
    @secured_route
    def post(self, device):
        try:
            return jsonify({"success": True, "content": device.circle.get_content()})
        except Exception as e:
            return FAILED(e)


class CircleList(Resource):
    @secured_route
    def post(self, user):
        try:
            circle_list = []
            for link in user.circle_link:
                if link.circle not in circle_list:
                    circle_list.append(link.circle)
            resp = jsonify({"success": True, "content": [circle.get_simple_content() for circle in circle_list]})
        except Exception as e:
            return FAILED(e)
        return resp
