from flask_restful import Resource
from utils.decorators import checkContent
from utils.decorators import securedRoute
from models.DeviceUser import DeviceUser
from models.Device import Device
from source.database import db_session
from utils.apiUtils import *

class DeviceUserCreate(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            device = db_session.query(Device).filter(Device.id == content["device"]).first()
            if device is not None:
                device_user = DeviceUser(first_name=content["first_name"], last_name=content["last_name"],
                                    birthday=content["birthday"], device=device)
                db_session.commit()
                resp = SUCCESS()
            else:
                resp = FAILED("Device with id %d not found" % content["device_id"])
        except Exception as e:
            resp = FAILED(e)
        return resp

class DeviceUserUpdate(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            device_user = db_session.query(DeviceUser).filter(DeviceUser.id == content["device_user_id"]).first()
            if device_user is not None:
                device = db_session.query(Device).filter(Device.id == content["device"]).first()
                device.updateContent(first_name=content["first_name"], last_name=content["last_name"],
                                     birthday=content["birthday"], device=device)
                resp = SUCCESS()
            else:
                resp = FAILED("DeviceUser with id %d not found" % content["device_user_id"])
        except Exception as e:
            resp = FAILED(e)
        return resp

class DeviceUserInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            device_user = db_session.query(DeviceUser).filter(DeviceUser.id == content["device_user_id"]).first()
            if device_user is not None:
                resp = jsonify({"success": True, "content": device_user.getNonSensitiveContent()})
            else:
                resp = FAILED("DeviceUser with id %d could not be found" % content["device_user_id"])
        except Exception as e:
            resp = FAILED(e)
        return resp

class DeviceUserDelete(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            device_user = db_session.query(DeviceUser).filter(DeviceUser.id == content["device_user_id"]).first()
            if device_user is not None:
                device_user.delete()
                resp = SUCCESS()
            else:
                resp = FAILED("DeviceUser with id %d could not be found" % content["device_user_id"])
        except Exception as e:
            resp = FAILED(e)
        return resp