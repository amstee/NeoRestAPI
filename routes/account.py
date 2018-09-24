from flask import request
from flask_restful import Resource
from utils.decorators import secured_route_old, check_content, check_admin_route, secured_user_route, route_log
from utils.security import get_any_from_header
from config.log import LOG_ACCOUNT_FILE
from utils.log import logger_set
import core.account as core

logger = logger_set(module=__name__, file=LOG_ACCOUNT_FILE)


class AccountCreate(Resource):
    @route_log(logger)
    @check_content(("email", str(), True), ("password", str(), True), ("first_name", str(), True),
                   ("last_name", str(), True), ("birthday", str(), True))
    def post(self, content):
        return core.create(content["email"], content["password"], content["first_name"],
                           content["last_name"], content["birthday"])


class AccountLogin(Resource):
    @route_log(logger)
    @check_content(("email", str(), True), ("password", str(), True))
    def post(self, content):
            return core.login(content["email"], content["password"])


class ModifyPassword(Resource):
    @route_log(logger)
    @check_content(("email", str(), True), ("previous_password", str(), True), ("new_password", str(), True))
    def post(self, content):
        return core.modify_password(content["email"], content["previous_password"], content["new_password"])


class CheckToken(Resource):
    @route_log(logger)
    @check_content(("token", str(), True))
    def post(self, content):
        return core.check_token(content["token"])


class AccountLogout(Resource):
    @route_log(logger)
    @check_content(("token", str(), True))
    def post(self, content):
        return core.logout(content["token"])


class UserInfo(Resource):
    @route_log(logger)
    @check_content(("user_id", int(), False))
    @secured_route_old
    def post(self, content, client, is_device):
        if "user_id" not in content and is_device is False:
            return core.get_info(client.id, client, is_device)
        return core.get_info(content["user_id"], client, is_device)


class GetUserInfo(Resource):
    @route_log(logger)
    def get(self, user_id):
        client, is_device = get_any_from_header(request)
        return core.get_info(user_id, client, is_device)


class AccountModify(Resource):
    @route_log(logger)
    @check_content(("email", str(), False), ("first_name", str(), False),
                   ("last_name", str(), False), ("birthday", str(), False))
    @secured_user_route
    def post(self, content, user):
        return core.update(content, user)


class MailAvailability(Resource):
    @route_log(logger)
    @check_content(("email", str(), True))
    def post(self, content):
        return core.is_email_available(content["email"])


class GetMailAvailability(Resource):
    @route_log(logger)
    def get(self, email):
        return core.is_email_available(email)


class PromoteAdmin(Resource):
    @route_log(logger)
    @check_content(("user_id", int(), True))
    @check_admin_route
    def post(self, content):
        core.promote_admin(content["user_id"])


class CreateApiToken(Resource):
    @route_log(logger)
    @secured_user_route
    def post(self, user):
        return core.create_api_token(user)
