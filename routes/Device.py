from flask_restful import Resource
from utils.decorators import checkContent, securedAdminRoute, securedRoute, securedDeviceRoute
from models.Device import Device
from models.Circle import Circle
from config.database import db_session
from utils.apiUtils import *
from utils.contentChecker import contentChecker


class DeviceAdd(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content, admin):
        try:
            contentChecker("circle_id", "name")
            circle = db_session.query(Circle).filter(Circle.id==content["circle_id"]).first()
            new_device = Device(name=content["name"], username=content["username"] if "username" in content else None)
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
            device = db_session.query(Device).filter(Device.id==content["device_id"]).first()
            if device is None:
                return FAILED("Device introuvable")
            if not device.circle.hasAdmin(user):
                return FAILED("Privileges insuffisants", 403)
            device.updateContent(name=content['name'] if "name" in content else None)
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class DeviceInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("device_id")
            device = db_session.query(Device).filter(Device.id == content["device_id"]).first()
            if device is not None:
                if not device.circle.hasMember(user):
                    return FAILED("Vous n'appartenez pas au cercle de ce device", 403)
                return jsonify({"success": True, "content": device.getContent()})
            resp = FAILED("Le NEO avec identifiant %s n'existe pas" % content["device_id"])
            resp.status_code = 401
        except Exception as e:
            return FAILED(e)
        return resp

class InforForDevice(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        try:
            return jsonify({"success": True, "content": device.getContent()})
        except Exception as e:
            return FAILED(e)

class DeviceDelete(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content, admin):
        try:
            contentChecker("device_id")
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
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("device_id", "activation_key")
            device = db_session.query(Device).filter(Device.id == content["device_id"]).first()
            if not (device.circle.hasMember(user)):
                return FAILED("Vous n'appartenez pas au cercle de ce device", 403)
            if device is not None:
                res = device.activate(content["activation_key"])
                if res:
                    return SUCCESS()
                else:
                    return FAILED("Clé d'activation invalide")
            resp = FAILED("Le Neo avec identifiant id %s n'existe pas")%content["device_id"]
        except Exception as e:
            return FAILED(e)
        return resp


class DeviceLogin(Resource):
    @checkContent
    def post(self, content):
        try:
            contentChecker("device_username", "device_password")
            device = db_session.query(Device).filter(Device.username==content["device_username"]).first()
            if device is not None:
                res, data = device.Authenticate(content["device_password"])
                if res is True:
                    resp = jsonify({"success": True, "device_token": data})
                    resp.status_code = 200
                else:
                    return FAILED(data)
            else:
                return FAILED("Device introuvable")
            return resp
        except Exception as e:
            return FAILED(e)


class ModifyDevicePassword(Resource):
    @checkContent
    def post(self, content):
        try:
            contentChecker("device_username", "previous_password", "new_password")
            device = db_session.query(Device).filter(Device.username==content["device_username"]).first()
            if device is not None:
                if device.checkPassword(content["previous_password"]):
                    device.updatePassword(content["new_password"])
                    return SUCCESS()
                return FAILED("Ancien mot de passe invalide")
            return FAILED("Device introuvable")
        except Exception as e:
            return FAILED(e)


class CheckDeviceToken(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        return jsonify({"success": True, "message": "Le token json de ce device est valide"})


class DeviceLogout(Resource):
    @checkContent
    def post(self, content):
        try:
            contentChecker("device_token")
            res, data = Device.decodeAuthToken(content["device_token"])
            if res is True:
                data.disconnect()
                return SUCCESS()
            else:
                resp = jsonify({"success": True, "message": data})
                resp.status_code = 403
            return resp
        except Exception as e:
            return FAILED(e)


class UsernameAvailability(Resource):
    @checkContent
    def post(self, content):
        try:
            contentChecker("device_username")
            device = db_session.query(Device).filter(Device.username==content["device_username"]).first()
            if device is not None:
                return FAILED("")
            else:
                return SUCCESS()
        except Exception as e:
            return FAILED(e)


class DeviceCredentials(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content, admin):
        try:
            contentChecker("device_id")
            device = db_session.query(Device).filter(Device.id==content["device_id"]).first()
            if device is None:
                return FAILED("Device Neo introuvable")
            return jsonify({"success": True, "content": {
                                "key": device.key,
                                "username": device.username,
                                "password": device.getPreActivationPassword()
                                }})
        except Exception as e:
            return FAILED(e)