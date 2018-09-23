from flask_restful import Resource
from flask import request
from utils.decorators import secured_route, check_content_old, check_admin_route
from utils.apiUtils import *
from utils.contentChecker import content_checker
from utils.exceptions import ContentNotFound, InvalidAuthentication
from utils.security import get_any_from_header
import core.media as core


class MediaInfo(Resource):
    @check_content_old
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("media_id")
            return core.info(content["media_id"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class GetMediaInfo(Resource):
    def get(self, media_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.info(media_id, client, is_device)
        except InvalidAuthentication as ie:
            return FAILED(ie)


class MediaInfoAdmin(Resource):
    @check_content_old
    @check_admin_route
    def post(self, content):
        try:
            content_checker("media_id")
            return core.admin_info(content["media_id"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class MediaDelete(Resource):
    @check_content_old
    @check_admin_route
    def post(self, content):
        try:
            content_checker("media_id")
            return core.delete(content["media_id"])
        except ContentNotFound as cnf:
            return FAILED(cnf)


class MediaList(Resource):
    @check_content_old
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("message_id")
            return core.media_list(content["message_id"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class GetMediaList(Resource):
    def get(self, message_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.media_list(message_id, client, is_device)
        except InvalidAuthentication as cnf:
            return FAILED(cnf)


class MediaUpdate(Resource):
    @check_content_old
    @check_admin_route
    def post(self, content):
        try:
            content_checker("media_id")
            return core.admin_update(content, content["media_id"])
        except ContentNotFound as cnf:
            return FAILED(cnf)
