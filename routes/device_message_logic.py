from flask_restful import Resource
from utils.decorators import check_content, secured_device_route
from utils.contentChecker import content_checker
from utils.apiUtils import *
from utils.exceptions import ContentNotFound
import core.device_message_logic as core


class FirstDeviceMessageSend(Resource):
    @check_content
    @secured_device_route
    def post(self, content, device):
        try:
            content_checker("email")
            return core.first_message_to_user(content, content["email"], device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class DeviceMessageSend(Resource):
    @check_content
    @secured_device_route
    def post(self, content, device):
        try:
            content_checker("conversation_id")
            return core.message_send(content, content["conversation_id"], device)
        except ContentNotFound as cnf:
            return FAILED(cnf)
