from config.database import db
from models.Circle import Circle
from models.UserToCircle import UserToCircle
from utils.apiUtils import *
from exceptions.circle import UserForbiddenAccess, CircleNotFound, CircleException


def create(name, user):
    try:
        circle = Circle(name)
        link = UserToCircle(privilege="REGULAR")
        link.circle = circle
        link.user = user
        db.session.commit()
        response = jsonify({"success": True, "content": circle.get_simple_content()})
        response.status_code = 200
    except CircleException:
        response = jsonify({"success": False, "message": CircleException.message})
        response.status_code = CircleException.status_code
    return response


def update(content, client, is_device):
    try:
        circle = db.session.query(Circle).filter(Circle.id == content["circle_id"]).first()
        if circle is None:
            raise CircleNotFound
        if (not is_device and not circle.has_member(client)) or (is_device and client.circle_id != circle.id):
            raise UserForbiddenAccess
        circle.update_content(name=content["name"] if "name" in content else None,
                              created=content["created"] if "created" in content else None)
        circle.notify_users(p1='circle', p2={'event': 'update'})
        response = jsonify({"success": True})
        response.status_code = 200
    except CircleException:
        response = jsonify({"success": False, "message": CircleException.message})
        response.status_code = CircleException.status_code
    return response


def delete(circle_id):
    try:
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if circle is None:
            raise CircleNotFound
        circle.notify_users(p1='circle', p2={'event': 'delete'})
        db.session.delete(circle)
        db.session.commit()
        response = jsonify({"success": True})
        response.status_code = 200
    except CircleException:
        response = jsonify({"success": False, "message": CircleException.message})
        response.status_code = CircleException.status_code
    return response


def get_info(circle_id, client, is_device):
    try:
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        if circle is None:
            raise CircleNotFound
        if (not is_device and not circle.has_member(client)) or (is_device and client.circle_id != circle_id):
            raise UserForbiddenAccess
        response = jsonify({"success": True, "content": circle.get_content()})
        response.status_code = 200
    except CircleException:
        response = jsonify({"success": False, "message": CircleException.message})
        response.status_code = CircleException.status_code
    return response


def get_list(user):
    try:
        circle_list = []
        for link in user.circle_link:
            if link.circle not in circle_list:
                circle_list.append(link.circle)
        response = jsonify({"success": True, "content": [circle.get_simple_content() for circle in circle_list]})
        response.status_code = 200
    except CircleException:
        response = jsonify({"success": False, "message": CircleException.message})
        response.status_code = CircleException.status_code
    return response
