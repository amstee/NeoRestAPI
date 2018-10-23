from flask_restful import Resource
from utils.apiUtils import *
from utils.decorators import check_content, route_log
import core.conversation_logic as core
from config.log import LOG_CONVERSATION_FILE
from utils.log import logger_set

logger = logger_set(module=__name__, file=LOG_CONVERSATION_FILE)


class ConversationInvite(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("conversation_id", int(), True), ("email", str(), True))
    def post(self, content, client, is_device):
        core_response = core.invite(content["conversation_id"], content["email"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class ConversationUserPromote(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("conversation_id", int(), True), ("email", str(), True))
    def post(self, content, client, is_device):
        core_response = core.user_promote(content["conversation_id"], content["email"], client)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class ConversationKick(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("conversation_id", int(), True), ("email", str(), True))
    def post(self, content, client, is_device):
        core_response = core.conversation_kick(content["conversation_id"], content["email"], client)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class ConversationQuit(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("conversation_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.conversation_quit(content["conversation_id"], client)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class ConversationSetDevice(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("conversation_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.set_device(content["conversation_id"], client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response

