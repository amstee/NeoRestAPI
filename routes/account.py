from flask import request
from flask_restful import Resource
from utils.decorators import check_content, route_log
from utils.security import get_any_from_header
from utils.apiUtils import jsonify
from config.log import LOG_ACCOUNT_FILE
from utils.log import logger_set
import core.account as core

logger = logger_set(module=__name__, file=LOG_ACCOUNT_FILE)


class AccountCreate(Resource):
    @route_log(logger)
    @check_content(None, ("email", str(), True), ("password", str(), True), ("first_name", str(), True),
                   ("last_name", str(), True), ("birthday", str(), True))
    def post(self, content):
        core_response = core.create(content["email"], content["password"], content["first_name"],
                           content["last_name"], content["birthday"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class AccountLogin(Resource):
    @route_log(logger)
    @check_content(None, ("email", str(), True), ("password", str(), True))
    def post(self, content):
        core_response = core.login(content["email"], content["password"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class ModifyPassword(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("email", str(), True), ("previous_password", str(), True), ("new_password", str(), True))
    def post(self, content, client, is_device):
        core_response = core.modify_password(content["email"], content["previous_password"], content["new_password"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class CheckToken(Resource):
    @route_log(logger)
    @check_content(None, ("token", str(), True))
    def post(self, content):
        core_response = core.check_token(content["token"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class AccountLogout(Resource):
    @route_log(logger)
    @check_content(None, ("token", str(), True))
    def post(self, content):
        core_response = core.logout(content["token"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class UserInfo(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("user_id", int(), False))
    def post(self, content, client, is_device):
        if "user_id" not in content and is_device is False:
            core_response = core.get_info(client.id, client, is_device)
        else:
            core_response = core.get_info(content["user_id"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class GetUserInfo(Resource):
    @route_log(logger)
    def get(self, user_id):
        client, is_device = get_any_from_header(request)
        return core.get_info(user_id, client, is_device)


class AccountModify(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("email", str(), False), ("first_name", str(), False),
                   ("last_name", str(), False), ("birthday", str(), False))
    def post(self, content, client, is_device):
        core_response = core.update(content, client)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class MailAvailability(Resource):
    @route_log(logger)
    @check_content(None, ("email", str(), True))
    def post(self, content):
        core_response = core.is_email_available(content["email"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class GetMailAvailability(Resource):
    @route_log(logger)
    def get(self, email):
        return core.is_email_available(email)


class PromoteAdmin(Resource):
    @route_log(logger)
    @check_content("ADMIN", ("user_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.promote_admin(content["user_id"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class CreateApiToken(Resource):
    @route_log(logger)
    @check_content("DEFAULT", None)
    def post(self, content, client, is_device):
        core_response = core.create_api_token(client)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response
