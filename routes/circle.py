from flask_restful import Resource
from flask import request
from utils.decorators import secured_route, check_content, check_admin_route, secured_user_route
from utils.security import get_any_from_header
from utils.contentChecker import content_checker
from utils.apiUtils import *
from utils.exceptions import ContentNotFound, InvalidAuthentication
import core.circle as core


class CircleCreate(Resource):
    @check_content
    @secured_user_route
    def post(self, content, user):
        try:
            content_checker("name")
            return core.create(content["name"], user)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class CircleDelete(Resource):
    @check_content
    @check_admin_route
    def delete(self, content):
        try:
            content_checker("circle_id")
            return core.delete(content["circle_id"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class CircleUpdate(Resource):
    @check_content
    @secured_route
    def put(self, content, client, is_device):
        return core.update(content, client, is_device)


class CircleInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, client, is_device):
        try:
            if not is_device:
                content_checker("circle_id")
                return core.get_info(content["circle_id"], client, is_device)
            else:
                return core.get_info(client.circle.id, client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class GetCircleInfo(Resource):
    def get(self, circle_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.get_info(circle_id, client, is_device)
        except InvalidAuthentication as ia:
            return FAILED(ia)


class CircleList(Resource):
    @secured_user_route
    def post(self, user):
        return core.get_list(user)
