from flask_restful import Resource
from flask import request
from utils.decorators import secured_route, check_content_old, check_admin_route
from utils.contentChecker import content_checker
from utils.apiUtils import *
from utils.exceptions import ContentNotFound, InvalidAuthentication
from utils.security import get_any_from_header
import core.conversation as core


class ConversationCreate(Resource):
    @check_content_old
    @check_admin_route
    def post(self, content):
        try:
            content_checker("conversation_name", "circle_id")
            return core.admin_create(content["conversation_name"], content["circle_id"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class ConversationDelete(Resource):
    @check_content_old
    @check_admin_route
    def post(self, content):
        try:
            content_checker("conversation_id")
            return core.admin_delete(content["conversation_id"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class ConversationInfo(Resource):
    @check_content_old
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("conversation_id")
            return core.info(content["conversation_id"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class GetConversationInfo(Resource):
    def get(self, conversation_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.info(conversation_id, client, is_device)
        except InvalidAuthentication as ia:
            return FAILED(ia)


class ConversationList(Resource):
    @check_content_old
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("circle_id")
            return core.conversation_list(content["circle_id"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class GetConversationList(Resource):
    def get(self, circle_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.conversation_list(circle_id, client, is_device)
        except InvalidAuthentication as ia:
            return FAILED(ia)


class ConversationUpdate(Resource):
    @check_content_old
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("conversation_id")
            return core.update(content, content["conversation_id"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)
