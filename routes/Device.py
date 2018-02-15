from flask_restful import Resource
from utils.decorators import checkContent
from utils.decorators import securedRoute
from models.Device import Device
from source.database import db_session
from utils.apiUtils import *

class DeviceAdd(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            new_device = Device(user=user)
            db_session.commit()
            resp = SUCCESS()
        except Exception as e:
            resp = FAILED(e)
        return resp

class DeviceUpdate(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            for device in user.devices:
                if device.id == content["device_id"]:
                    device.updateContent(content["created"], content["updated"])
                    return SUCCESS()
            resp = FAILED("Device with id %s not found" + str(content["device_id"]))
        except Exception as e:
            resp = FAILED(e)
        return resp

class DeviceInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            for device in user.devices:
                if device.id == content["device_id"]:
                    return jsonify({"success": True, "content": device.getNonSensitiveContent()})
            resp = FAILED("Device not with id %s found" % content["device_id"])
        except Exception as e:
            resp = FAILED(e)
        return resp

class AccountDevices(Resource):
    @securedRoute
    def post(self, user):
        arr = []
        try:
            for device in user.devices:
                arr.append(device.getNonSensitiveContent())
            resp = jsonify({"success": True, "content": arr})
        except Exception as e:
            resp = FAILED(e)
        return resp

class DeviceDelete(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            for device in user.devices:
                if device.id == content["device_id"]:
                    device.delete()
                    db_session.commit()
                    return SUCCESS()
            resp = FAILED("device with id %s not found" % content["device_id"])
        except Exception as e:
            return FAILED(e)
        return resp