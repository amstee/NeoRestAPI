from flask import request
from flask_restful import Resource
from utils.decorators import check_content_old, check_admin_route, secured_route, secured_device_route
from utils.security import get_any_from_header
from utils.apiUtils import *
from utils.contentChecker import content_checker
from utils.exceptions import ContentNotFound, InvalidAuthentication
import core.device as core


class DeviceAdd(Resource):
    @check_content_old
    @check_admin_route
    def post(self, content):
        try:
            content_checker("circle_id", "name")
            return core.admin_add(content, content["circle_id"], content["name"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class DeviceUpdate(Resource):
    @check_content_old
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("device_id")
            return core.update(content, content["device_id"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class DeviceInfo(Resource):
    @check_content_old
    @secured_route
    def post(self, content, client, is_device):
        try:
            if is_device:
                return core.info(client.id, client, is_device)
            else:
                content_checker("device_id")
                return core.info(content["device_id"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class GetDeviceInfo(Resource):
    def get(self, device_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.info(device_id, client, is_device)
        except InvalidAuthentication as ie:
            return FAILED(ie)


class DeviceDelete(Resource):
    @check_content_old
    @check_admin_route
    def post(self, content):
        try:
            content_checker("device_id")
            return core.admin_delete(content["device_id"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class DeviceActivate(Resource):
    @check_content_old
    @check_admin_route
    def post(self, content):
        try:
            content_checker("device_id", "activation_key")
            return core.admin_activate(content["device_id"], content["activation_key"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class DeviceLogin(Resource):
    @check_content_old
    def post(self, content):
        try:
            content_checker("device_username", "device_password")
            return core.login(content["device_username"], content["device_password"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class ModifyDevicePassword(Resource):
    @check_content_old
    def post(self, content):
        try:
            content_checker("device_username", "previous_password", "new_password")
            return core.modify_password(content["device_username"], content["previous_password"], content["new_password"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class CheckDeviceToken(Resource):
    @check_content_old
    @secured_device_route
    def post(self, content, device):
        return core.check_token(content, device)


class DeviceLogout(Resource):
    @check_content_old
    def post(self, content):
        try:
            content_checker("device_token")
            return core.logout(content["device_token"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class UsernameAvailability(Resource):
    @check_content_old
    def post(self, content):
        try:
            content_checker("device_username")
            return core.is_username_available(content["device_username"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class GetUsernameAvailability(Resource):
    def get(self, username):
        return core.is_username_available(username)


class DeviceCredentials(Resource):
    @check_content_old
    @check_admin_route
    def post(self, content):
        try:
            content_checker("device_id")
            return core.admin_credentials(content["device_id"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class DeviceList(Resource):
    @check_content_old
    @check_admin_route
    def post(self, content):
        try:
            content_checker("email")
            return core.admin_list(content["email"])
        except ContentNotFound as cnf:
            return FAILED(cnf)

