from flask_restful import Resource
from flask import request
from utils.decorators import check_content, route_log
from utils.apiUtils import *
from utils.security import get_any_from_header
from utils.exceptions import InvalidAuthentication
import core.message as core
from utils.log import logger_set
from config.log import LOG_MESSAGE_FILE

logger = logger_set(module=__name__, file=LOG_MESSAGE_FILE)


class MessageDelete(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("message_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.delete(content["message_id"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class MessageInfo(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("message_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.info(content["message_id"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class GetMessageInfo(Resource):
    def get(self, message_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.info(message_id, client, is_device)
        except InvalidAuthentication as ia:
            return FAILED(ia)


class MessageList(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("conversation_id", int(), True), ("quantity", int(), True))
    def post(self, content, client, is_device):
        core_response = core.message_list(content["conversation_id"], content["quantity"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class GetMessageList(Resource):
    def get(self, conversation_id, quantity):
        try:
            client, is_device = get_any_from_header(request)
            return core.message_list(conversation_id, quantity, client, is_device)
        except InvalidAuthentication as ia:
            return FAILED(ia)


class MessageUpdate(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("message_id", int(), True), ("text_content", str(), True))
    def post(self, content, client, is_device):
        core_response = core.update(content["message_id"], content["text_content"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response
