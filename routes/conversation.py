from flask_restful import Resource
from flask import request
from utils.apiUtils import *
from utils.exceptions import InvalidAuthentication
from utils.security import get_any_from_header
from utils.decorators import check_content, route_log
import core.conversation as core
from config.log import LOG_CONVERSATION_FILE
from utils.log import logger_set

logger = logger_set(module=__name__, file=LOG_CONVERSATION_FILE)


class ConversationCreate(Resource):
    @route_log(logger)
    @check_content("ADMIN", ("conversation_name", str(), True), ("circle_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.admin_create(content["conversation_name"], content["circle_id"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class ConversationDelete(Resource):
    @route_log(logger)
    @check_content("ADMIN", ("conversation_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.admin_delete(content["conversation_id"])
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class ConversationInfo(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("conversation_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.info(content["conversation_id"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class GetConversationInfo(Resource):
    def get(self, conversation_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.info(conversation_id, client, is_device)
        except InvalidAuthentication as ia:
            return FAILED(ia)


class ConversationList(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("circle_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.conversation_list(content["circle_id"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class GetConversationList(Resource):
    def get(self, circle_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.conversation_list(circle_id, client, is_device)
        except InvalidAuthentication as ia:
            return FAILED(ia)


class ConversationUpdate(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("conversation_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.update(content, content["conversation_id"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response
