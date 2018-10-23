from flask_restful import Resource
from flask import request
from utils.decorators import check_content, route_log
from utils.security import get_any_from_header, get_user_from_header
from utils.apiUtils import jsonify
from utils.exceptions import InvalidAuthentication
import core.circle as core
from config.log import LOG_CIRCLE_FILE
from utils.log import logger_set

logger = logger_set(module=__name__, file=LOG_CIRCLE_FILE)


class CircleCreate(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("name", str(), True))
    def post(self, content, client, is_device):
        core_response = core.create(content['name'], client)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class CircleDelete(Resource):
    @route_log(logger)
    @check_content("ADMIN", ("circle_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.delete(content["circle_id"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class CircleUpdate(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("circle_id", int(), True), ("name", str(), False))
    def post(self, content, client, is_device):
        core_response = core.update(content, client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class CircleInfo(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("circle_id", int(), False))
    def post(self, content, client, is_device):
        if not is_device:
            core_response = core.get_info(content["circle_id"], client, is_device)
        else:
            core_response = core.get_info(client.circle.id, client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class GetCircleInfo(Resource):
    def get(self, circle_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.get_info(circle_id, client, is_device)
        except InvalidAuthentication as ia:
            return FAILED(ia)


class CircleList(Resource):
    @route_log(logger)
    @check_content("DEFAULT", None)
    def post(self, content, client, is_device):
        core_response = core.get_list(client)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class GetCircleList(Resource):
    def get(self):
        try:
            user = get_user_from_header(request)
            return core.get_list(user)
        except InvalidAuthentication as ie:
            return FAILED(ie)
