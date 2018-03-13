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
            new_device = Device(user=user, name=content["name"])
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
            for device in user.device:
                if device.id == content["device_id"]:
                    content['name'] = None if 'name' not in content else content['name']
                    device.updateContent(name=content['name'])
                    return SUCCESS()
            resp = FAILED("Le NEO avec identifiant %s n'existe pas" + str(content["device_id"]))
            resp.status_code = 401
        except Exception as e:
            return FAILED(e)
        return resp

class DeviceInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            for device in user.device:
                if device.id == content["device_id"]:
                    return jsonify({"success": True, "content": device.getNonSensitiveContent()})
            resp = FAILED("Le NEO avec identifiant %s n'existe pas" % content["device_id"])
            resp.status_code = 401
        except Exception as e:
            return FAILED(e)
        return resp

class DeviceList(Resource):
    @securedRoute
    def post(self, user):
        arr = []
        try:
            for device in user.device:
                arr.append(device.getNonSensitiveContent())
            resp = jsonify({"success": True, "content": arr})
        except Exception as e:
            return FAILED(e)
        return resp

class DeviceDelete(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            for device in user.device:
                if device.id == content["device_id"]:
                    Device.query.filter(Device.id == content['device_id']).delete()
                    db_session.commit()
                    return SUCCESS()
            resp = FAILED("Le NEO avec identifiant id %s n'existe pas" % content["device_id"])
            resp.status_code = 401
        except Exception as e:
            return FAILED(e)
        return resp