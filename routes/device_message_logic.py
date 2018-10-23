from flask_restful import Resource
from utils.decorators import check_content, route_log
from utils.apiUtils import jsonify
import core.device_message_logic as core
from utils.log import logger_set
from config.log import LOG_DEVICE_FILE

logger = logger_set(module=__name__, file=LOG_DEVICE_FILE)


class FirstDeviceMessageSend(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("email", str(), True))
    def post(self, content, client, is_device):
        core_response = core.first_message_to_user(content, content["email"], client)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response


class DeviceMessageSend(Resource):
    @route_log(logger)
    @check_content("DEFAULT", ("conversation_id", int(), True))
    def post(self, content, client, is_device):
        core_response = core.message_send(content, content["conversation_id"], client)
        response = jsonify(core_response['data'])
        response.status_code = core_response['status_code']
        return response
