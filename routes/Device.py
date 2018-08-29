from flask_restful import Resource
from flask import request
from utils.decorators import check_content, secured_admin_route, secured_route
from models.Device import Device
from models.Circle import Circle
from config.database import db
from utils.apiUtils import *
from utils.contentChecker import content_checker
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc

logger = logger_set(__name__)


class DeviceAdd(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("circle_id", "name")
            circle = db.session.query(Circle).filter(Circle.id == content["circle_id"]).first()
            new_device = Device(name=content["name"], username=content["username"] if "username" in content else None)
            new_device.circle = circle
            db.session.commit()
            circle.notify_users('device created')
            resp = SUCCESS()
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            resp.status_code = 409
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class DeviceUpdate(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("device_id")
            device = db.session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is None:
                resp = FAILED("Device introuvable")
            elif not device.circle.has_admin(user):
                resp = FAILED("Privileges insuffisants", 403)
            else:
                device.update_content(name=content['name'] if "name" in content else None)
                device.circle.notify_users(p2={'event': 'device', 'type': 'update', 'device_id': device.id})
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


class DeviceInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("device_id")
            device = db.session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is not None:
                if not device.circle.has_member(user):
                    resp = FAILED("Vous n'appartenez pas au cercle de ce device", 403)
                else:
                    resp = jsonify({"success": True, "content": device.get_content()})
            else:
                resp = FAILED("Le NEO avec identifiant %s n'existe pas" % content["device_id"])
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


class InfoForDevice(Resource):
    @secured_route
    def post(self, device):
        try:
            resp = jsonify({"success": True, "content": device.get_content()})
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class DeviceDelete(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("device_id")
            device = db.session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is not None:
                db.session.delete(device)
                db.session.commit()
                resp = SUCCESS()
            else:
                resp = FAILED("Le NEO avec identifiant id %s n'existe pas" % content["device_id"])
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


class DeviceActivate(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("device_id", "activation_key")
            device = db.session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is not None:
                res = device.activate(content["activation_key"])
                if res:
                    resp = SUCCESS()
                else:
                    resp = FAILED("Clé d'activation invalide")
            else:
                resp = FAILED("Le Neo avec identifiant id %s n'existe pas") % content["device_id"]
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class DeviceLogin(Resource):
    @check_content
    def post(self, content):
        try:
            content_checker("device_username", "device_password")
            device = db.session.query(Device).filter(Device.username == content["device_username"]).first()
            if device is not None:
                res, data = device.authenticate(content["device_password"])
                if res is True:
                    resp = jsonify({"success": True, "device_token": data})
                    resp.status_code = 200
                    device.circle.notify_users(p2={'event': 'device', 'type': 'connect', 'device_id': device.id})
                else:
                    resp = FAILED(data)
            else:
                resp = FAILED("Device introuvable")
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class ModifyDevicePassword(Resource):
    @check_content
    def post(self, content):
        try:
            content_checker("device_username", "previous_password", "new_password")
            device = db.session.query(Device).filter(Device.username == content["device_username"]).first()
            if device is not None:
                if device.check_password(content["previous_password"]):
                    device.update_password(content["new_password"])
                    resp = SUCCESS()
                else:
                    resp = FAILED("Ancien mot de passe invalide")
            else:
                resp = FAILED("Device introuvable")
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class CheckDeviceToken(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            resp = jsonify({"success": True, "message": "Le token json de ce device est valide"})
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class DeviceLogout(Resource):
    @check_content
    def post(self, content):
        try:
            content_checker("device_token")
            res, data = Device.decode_auth_token(content["device_token"])
            if res is True:
                data.disconnect()
                data.circle.notify_users(p2={'event': 'device', 'type': 'disconnect', 'device_id': data.id})
                resp = SUCCESS()
            else:
                resp = jsonify({"success": True, "message": data})
                resp.status_code = 403
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class UsernameAvailability(Resource):
    @check_content
    def post(self, content):
        try:
            content_checker("device_username")
            device = db.session.query(Device).filter(Device.username == content["device_username"]).first()
            if device is not None:
                resp = FAILED("Le nom de device existe déja.")
            else:
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


class DeviceCredentials(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("device_id")
            device = db.session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is None:
                resp = FAILED("Device Neo introuvable")
            else:
                resp = jsonify({"success": True, "content": {
                                    "key": device.key,
                                    "username": device.username,
                                    "password": device.get_pre_activation_password()
                                    }})
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp
