from flask import request
from flask_restful import Resource
from utils.decorators import check_content, route_log
from utils.security import get_any_from_header
from utils.apiUtils import *
from utils.exceptions import InvalidAuthentication
import core.device as core
from utils.log import logger_set
from config.log import LOG_DEVICE_FILE

logger = logger_set(module=__name__, file=LOG_DEVICE_FILE)


class DeviceAdd(Resource):
    @route_log(logger)
    @check_content("ADMIN", ("circle_id", int(), True), ("name", str(), True))
    def post(self, content, client, is_device):
        core_response = core.admin_add(content, content["circle_id"], content["name"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class DeviceUpdate(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("device_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.update(content, content["device_id"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class DeviceInfo(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("device_id", int(), True))
    def post(self, content, client, is_device):
        if is_device:
            core_response = core.info(client.id, client, is_device)
        else:
            core_response = core.info(content["device_id"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class GetDeviceInfo(Resource):
    def get(self, device_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.info(device_id, client, is_device)
        except InvalidAuthentication as ie:
            return FAILED(ie)


class DeviceDelete(Resource):
    @route_log(logger)
    @check_content("ADMIN", ("device_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.admin_delete(content["device_id"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class DeviceActivate(Resource):
    @route_log(logger)
    @check_content("ADMIN", ("device_id", int(), True), ("activation_key", str(), True))
    def post(self, content, client, is_device):
        core_response = core.admin_activate(content["device_id"], content["activation_key"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class DeviceLogin(Resource):
    @route_log(logger)
    @check_content(None, ("device_username", str(), True), ("device_password", str(), True))
    def post(self, content):
        core_response = core.login(content["device_username"], content["device_password"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class ModifyDevicePassword(Resource):
    @route_log(logger)
    @check_content(None, ("device_username", str(), True), ("previous_password", str(), True),
                   ("new_password", str(), True))
    def post(self, content):
        core_response = core.modify_password(content["device_username"],
                                             content["previous_password"], content["new_password"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class CheckDeviceToken(Resource):
    @route_log(logger)
    @check_content("DEFAULT", None)
    def post(self, content, client, is_device):
        core_response = core.check_token(content, client)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class DeviceLogout(Resource):
    @route_log(logger)
    @check_content(None, ("device_token", str(), True))
    def post(self, content):
        core_response = core.logout(content["device_token"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class UsernameAvailability(Resource):
    @route_log(logger)
    @check_content(None, ("device_username", str(), True))
    def post(self, content):
        core_response = core.is_username_available(content["device_username"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class GetUsernameAvailability(Resource):
    def get(self, username):
        core_response = core.is_username_available(username)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class DeviceCredentials(Resource):
    @route_log(logger)
    @check_content("ADMIN", ("device_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.admin_credentials(content["device_id"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class DeviceList(Resource):
    @route_log(logger)
    @check_content("ADMIN", ("email", str(), True))
    def post(self, content, client, is_device):
        core_response = core.admin_list(content["email"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response
