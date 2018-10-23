from flask_restful import Resource
from utils.decorators import check_content_old
from flask_jsonpify import jsonify
from utils.apiUtils import FAILED


class SetCookies(Resource):
    @staticmethod
    def set_token(token, is_device=False):
        resp = jsonify({"success": True})
        if is_device:
            resp.set_cookie("neo_device_token", token)
        else:
            resp.set_cookie("neo_user_token", token)
        return resp

    @check_content_old
    def put(self, content):
        if "token" in content:
            return self.set_token(content["token"])
        elif "device_token" in content:
            return self.set_token(content["device_token"], True)
        else:
            return FAILED("Token introuvable")

    @check_content_old
    def post(self, content):
        if "token" in content:
            return self.set_token(content["token"])
        elif "device_token" in content:
            return self.set_token(content["device_token"], True)
        else:
            return FAILED("Token introuvable")
