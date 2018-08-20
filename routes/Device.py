from flask_restful import Resource
from utils.decorators import check_content, secured_admin_route, secured_route
from models.Device import Device
from models.Circle import Circle
from config.database import db_session
from utils.apiUtils import *
from utils.contentChecker import content_checker


class DeviceAdd(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("circle_id", "name")
            circle = db_session.query(Circle).filter(Circle.id == content["circle_id"]).first()
            new_device = Device(name=content["name"], username=content["username"] if "username" in content else None)
            new_device.circle = circle
            db_session.commit()
            circle.notify_users('device created')
            resp = SUCCESS()
        except Exception as e:
            resp = FAILED(e)
            resp.status_code = 409
            return resp
        return resp


class DeviceUpdate(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("device_id")
            device = db_session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is None:
                return FAILED("Device introuvable")
            if not device.circle.has_admin(user):
                return FAILED("Privileges insuffisants", 403)
            device.update_content(name=content['name'] if "name" in content else None)
            device.circle.notify_users(p2={'event': 'device', 'type': 'update', 'device_id': device.id})
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class DeviceInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("device_id")
            device = db_session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is not None:
                if not device.circle.has_member(user):
                    return FAILED("Vous n'appartenez pas au cercle de ce device", 403)
                return jsonify({"success": True, "content": device.get_content()})
            resp = FAILED("Le NEO avec identifiant %s n'existe pas" % content["device_id"])
            resp.status_code = 401
        except Exception as e:
            return FAILED(e)
        return resp


class InfoForDevice(Resource):
    @secured_route
    def post(self, device):
        try:
            return jsonify({"success": True, "content": device.get_content()})
        except Exception as e:
            return FAILED(e)


class DeviceDelete(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("device_id")
            device = db_session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is not None:
                db_session.delete(device)
                db_session.commit()
                return SUCCESS()
            resp = FAILED("Le NEO avec identifiant id %s n'existe pas" % content["device_id"])
            resp.status_code = 401
        except Exception as e:
            return FAILED(e)
        return resp


class DeviceActivate(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("device_id", "activation_key")
            device = db_session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is not None:
                res = device.activate(content["activation_key"])
                if res:
                    return SUCCESS()
                else:
                    return FAILED("Clé d'activation invalide")
            resp = FAILED("Le Neo avec identifiant id %s n'existe pas") % content["device_id"]
        except Exception as e:
            return FAILED(e)
        return resp


class DeviceLogin(Resource):
    @check_content
    def post(self, content):
        try:
            content_checker("device_username", "device_password")
            device = db_session.query(Device).filter(Device.username == content["device_username"]).first()
            if device is not None:
                res, data = device.authenticate(content["device_password"])
                if res is True:
                    resp = jsonify({"success": True, "device_token": data})
                    resp.status_code = 200
                    device.circle.notify_users(p2={'event': 'device', 'type': 'connect', 'device_id': device.id})
                else:
                    return FAILED(data)
            else:
                return FAILED("Device introuvable")
            return resp
        except Exception as e:
            return FAILED(e)


class ModifyDevicePassword(Resource):
    @check_content
    def post(self, content):
        try:
            content_checker("device_username", "previous_password", "new_password")
            device = db_session.query(Device).filter(Device.username == content["device_username"]).first()
            if device is not None:
                if device.check_password(content["previous_password"]):
                    device.update_password(content["new_password"])
                    return SUCCESS()
                return FAILED("Ancien mot de passe invalide")
            return FAILED("Device introuvable")
        except Exception as e:
            return FAILED(e)


class CheckDeviceToken(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        return jsonify({"success": True, "message": "Le token json de ce device est valide"})


class DeviceLogout(Resource):
    @check_content
    def post(self, content):
        try:
            content_checker("device_token")
            res, data = Device.decode_auth_token(content["device_token"])
            if res is True:
                data.disconnect()
                data.circle.notify_users(p2={'event': 'device', 'type': 'disconnect', 'device_id': data.id})
                return SUCCESS()
            else:
                resp = jsonify({"success": True, "message": data})
                resp.status_code = 403
            return resp
        except Exception as e:
            return FAILED(e)


class UsernameAvailability(Resource):
    @check_content
    def post(self, content):
        try:
            content_checker("device_username")
            device = db_session.query(Device).filter(Device.username == content["device_username"]).first()
            if device is not None:
                return FAILED("")
            else:
                return SUCCESS()
        except Exception as e:
            return FAILED(e)


class DeviceCredentials(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("device_id")
            device = db_session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is None:
                return FAILED("Device Neo introuvable")
            return jsonify({"success": True, "content": {
                                "key": device.key,
                                "username": device.username,
                                "password": device.get_pre_activation_password()
                                }})
        except Exception as e:
            return FAILED(e)
