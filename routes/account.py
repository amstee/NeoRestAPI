from flask import request
from flask_restful import Resource
from utils.decorators import secured_route, check_content_old, check_content, check_admin_route
from utils.decorators import secured_user_route, route_log
from utils.contentChecker import content_checker
from utils.security import get_any_from_header
from utils.apiUtils import *
from utils.exceptions import InvalidAuthentication, ContentNotFound
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
    @check_content_old
    @secured_route
    def post(self, content, client, is_device):
        if "user_id" not in content and is_device is False:
            return core.get_info(client.id, client, is_device)
        try:
            content_checker("user_id")
            return core.get_info(content["user_id"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class GetUserInfo(Resource):
    def get(self, user_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.get_info(user_id, client, is_device)
        except InvalidAuthentication as ia:
            return FAILED(ia)


class AccountModify(Resource):
    @check_content_old
    @secured_user_route
    def post(self, content, user):
        return core.update(content, user)


class MailAvailability(Resource):
    @check_content_old
    def post(self, content):
        try:
            content_checker("email")
            return core.is_email_available(content["email"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class GetMailAvailability(Resource):
    def get(self, email):
        return core.is_email_available(email)


class PromoteAdmin(Resource):
    @check_content_old
    @check_admin_route
    def post(self, content):
        try:
            content_checker("user_id")
            core.promote_admin(content["user_id"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class CreateApiToken(Resource):
    @secured_user_route
    def post(self, user):
        return core.create_api_token(user)
