from flask_restful import Resource
from utils.apiUtils import jsonify
from utils.decorators import check_content, route_log
import core.circle_logic as core
from config.log import LOG_CIRCLE_FILE
from utils.log import logger_set

logger = logger_set(module=__name__, file=LOG_CIRCLE_FILE)


class CircleInvite(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("circle_id", int(), True), ("email", str(), True))
    def post(self, content, client, is_device):
        core_response = core.invite(content["circle_id"], content["email"],  client, is_device)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class CircleJoin(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("invite_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.join(content["invite_id"], client)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class CircleReject(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("invite_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.refuse_invite(content["invite_id"], client)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class CircleQuit(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("circle_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.quit_circle(content["circle_id"], client)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class CircleKick(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("email", str(), True), ("circle_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.kick_user(content["email"], content["circle_id"], client)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response
