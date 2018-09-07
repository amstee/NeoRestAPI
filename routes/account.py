from flask import request
from flask_restful import Resource
from utils.decorators import secured_route, check_content, check_admin_route, secured_user_route
from utils.contentChecker import content_checker
from utils.security import get_any_from_header
from utils.apiUtils import *
from utils.exceptions import InvalidAuthentication, ContentNotFound
import core.account as core


class AccountCreate(Resource):
    @check_content
    def post(self, content):
        return core.create(content)


class AccountLogin(Resource):
    @check_content
    def post(self, content):
        try:
            content_checker("email", "password")
            return core.login(content["email"], content["password"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class ModifyPassword(Resource):
    @check_content
    def put(self, content):
        try:
            content_checker("email", "previous_password", "new_password")
            return core.modify_password(content["email"], content["previous_password"], content["new_password"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class CheckToken(Resource):
    @check_content
    def post(self, content):
        try:
            content_checker("token")
            return core.check_token(content["token"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class AccountLogout(Resource):
    @check_content
    def post(self, content):
        try:
            content_checker("token")
            return core.logout(content["token"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class UserInfo(Resource):
    @check_content
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
    @check_content
    @secured_user_route
    def put(self, content, user):
        return core.update(content, user)


class MailAvailability(Resource):
    @check_content
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
    @check_content
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
