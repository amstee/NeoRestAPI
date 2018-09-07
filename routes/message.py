from flask_restful import Resource
from flask import request
from utils.decorators import secured_route, check_content
from utils.contentChecker import content_checker
from utils.apiUtils import *
from utils.security import get_any_from_header
from utils.exceptions import ContentNotFound, InvalidAuthentication
import core.message as core


class MessageDelete(Resource):
    @check_content
    @secured_route
    def delete(self, content, client, is_device):
        try:
            content_checker("message_id")
            return core.delete(content["message_id"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class MessageInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("message_id")
            return core.info(content["message_id"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class GetMessageInfo(Resource):
    def get(self, message_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.info(message_id, client, is_device)
        except InvalidAuthentication as ia:
            return FAILED(ia)


class MessageList(Resource):
    @check_content
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("conversation_id", "quantity")
            return core.message_list(content["conversation_id"], content["quantity"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class GetMessageList(Resource):
    def get(self, conversation_id, quantity):
        try:
            client, is_device = get_any_from_header(request)
            return core.message_list(conversation_id, quantity, client, is_device)
        except InvalidAuthentication as ia:
            return FAILED(ia)


class MessageUpdate(Resource):
    @check_content
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("message_id", "text_content")
            return core.update(content["message_id"], content["text_content"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)
