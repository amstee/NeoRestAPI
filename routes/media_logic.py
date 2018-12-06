from flask import request
from flask_restful import Resource
from utils.decorators import check_content, route_log
from utils.apiUtils import *
from utils.security import get_any_from_header
from utils.exceptions import InvalidAuthentication
import core.media_logic as core
from utils.log import logger_set
from config.log import LOG_MEDIA_FILE

logger = logger_set(module=__name__, file=LOG_MEDIA_FILE)


class DeleteMedia(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("media_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.delete(content["media_id"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class CreateMedia(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("medias", [], True))
    def post(self, content, client, is_device):
        core_response = core.create(content["medias"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class FindMedia(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("purpose", str(), True))
    def post(self, content, client, is_device):
        core_response = core.find_media(content, content["purpose"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class UploadMedia(Resource):
    @route_log(logger)
    def post(self, media_id):
        try:
            client, is_device = get_any_from_header(request)
            core_response = core.upload(media_id, request.files, client, is_device)
            response = jsonify(core_response['data'])
            response.status_code = core_response['status_code']
            return response
        except InvalidAuthentication as ie:
            return FAILED(ie)


class MediaRequest(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("media_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.retrieve(content["media_id"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class GetMediaRequest(Resource):
    def get(self, media_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.retrieve(media_id, client, is_device)
        except InvalidAuthentication as ie:
            return FAILED(ie)
