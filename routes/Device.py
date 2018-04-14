from flask_restful import Resource
from utils.decorators import checkContent, securedAdminRoute, securedRoute
from models.Device import Device
from models.Circle import Circle
from config.database import db_session
from utils.apiUtils import *
from utils.contentChecker import contentChecker


class DeviceAdd(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content):
        try:
            contentChecker("circle_id", "name")
            circle = db_session.query(Circle).filter(Circle.id==content["circle_id"]).first()
            new_device = Device(name=content["name"])
            new_device.circle = circle
            db_session.commit()
            resp = SUCCESS()
        except Exception as e:
            resp = FAILED(e)
            resp.status_code = 409
            return resp
        return resp


class DeviceUpdate(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("device_id")
            for device in user.device:
                if device.id == content["device_id"]:
                    device.updateContent(created=content["created"] if "created" in content else None,
                                         name=content['name'] if "name" in content else None)
                    return SUCCESS()
            resp = FAILED("Le NEO avec identifiant %s n'existe pas" + str(content["device_id"]))
            resp.status_code = 401
        except Exception as e:
            return FAILED(e)
        return resp


class DeviceInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content):
        try:
            contentChecker("device_id")
            device = db_session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is not None:
                return jsonify({"success": True, "content": device.getContent()})
            resp = FAILED("Le NEO avec identifiant %s n'existe pas" % content["device_id"])
            resp.status_code = 401
        except Exception as e:
            return FAILED(e)
        return resp


class DeviceDelete(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content):
        try:
            contentChecker("device_id")
            device = db_session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is not None:
                db_session.delete(device)
                return SUCCESS()
            resp = FAILED("Le NEO avec identifiant id %s n'existe pas" % content["device_id"])
            resp.status_code = 401
        except Exception as e:
            return FAILED(e)
        return resp