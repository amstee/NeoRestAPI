from flask_restful import Resource
from utils.decorators import check_content, secured_user_route
from utils.contentChecker import content_checker
from utils.apiUtils import *
from utils.exceptions import ContentNotFound
import core.user_message_logic as core


class FirstMessageToDeviceSend(Resource):
    @check_content
    @secured_user_route
    def post(self, content, user):
        try:
            content_checker("circle_id")
            return core.first_message_to_device(content, content["circle_id"], user)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class FirstMessageSend(Resource):
    @check_content
    @secured_user_route
    def post(self, content, user):
        try:
            content_checker("email", "circle_id")
            return core.first_message_to_user(content, content["email"], content["circle_id"], user)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class MessageSend(Resource):
    @check_content
    @secured_user_route
    def post(self, content, user):
        try:
            content_checker("conversation_id")
            return core.message_send(content, content["conversation_id"], user)
        except ContentNotFound as cnf:
            return FAILED(cnf)
