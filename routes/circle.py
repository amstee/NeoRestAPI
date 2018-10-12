from flask_restful import Resource
from flask import request
from utils.decorators import check_content, route_log
from utils.security import get_any_from_header, get_user_from_header
from utils.apiUtils import *
from utils.exceptions import InvalidAuthentication
import core.circle as core
from config.log import LOG_CIRCLE_FILE
from utils.log import logger_set

logger = logger_set(module=__name__, file=LOG_CIRCLE_FILE)


class CircleCreate(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("name", str(), True))
    def post(self, content, client, is_device):
        return core.create(content['name'], client)


class CircleDelete(Resource):
    @route_log(logger)
    @check_content("ADMIN", ("circle_id", int(), True))
    def post(self, content, client, is_device):
        return core.delete(content["circle_id"])


class CircleUpdate(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("circle_id", int(), True), ("name", str(), False))
    def post(self, content, client, is_device):
        return core.update(content, client, is_device)


class CircleInfo(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("circle_id", int(), False))
    def post(self, content, client, is_device):
        if not is_device:
            return core.get_info(content["circle_id"], client, is_device)
        else:
            return core.get_info(client.circle.id, client, is_device)


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
        return core.get_list(client)


class GetCircleList(Resource):
    def get(self):
        try:
            user = get_user_from_header(request)
            return core.get_list(user)
        except InvalidAuthentication as ie:
            return FAILED(ie)
