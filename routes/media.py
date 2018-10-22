from flask_restful import Resource
from flask import request
from utils.decorators import check_content, route_log
from utils.apiUtils import *
from utils.exceptions import InvalidAuthentication
from utils.security import get_any_from_header
import core.media as core
from utils.log import logger_set
from config.log import LOG_MEDIA_FILE

logger = logger_set(module=__name__, file=LOG_MEDIA_FILE)


class MediaInfo(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("media_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.info(content["media_id"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class GetMediaInfo(Resource):
    def get(self, media_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.info(media_id, client, is_device)
        except InvalidAuthentication as ie:
            return FAILED(ie)


class MediaInfoAdmin(Resource):
    @route_log(logger)
    @check_content("ADMIN", ("media_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.admin_info(content["media_id"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class MediaDelete(Resource):
    @route_log(logger)
    @check_content("ADMIN", ("media_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.delete(content["media_id"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class MediaList(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("message_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.media_list(content["message_id"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class GetMediaList(Resource):
    def get(self, message_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.media_list(message_id, client, is_device)
        except InvalidAuthentication as cnf:
            return FAILED(cnf)


class MediaUpdate(Resource):
    @route_log(logger)
    @check_content("ADMIN", ("media_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.admin_update(content, content["media_id"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response
