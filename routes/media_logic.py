from flask import request
from flask_restful import Resource
from utils.decorators import secured_route, check_content
from utils.contentChecker import content_checker
from utils.apiUtils import *
from utils.security import get_any_from_header
from utils.exceptions import ContentNotFound, InvalidAuthentication
import core.media_logic as core


class DeleteMedia(Resource):
    @check_content
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("media_id")
            return core.delete(content["media_id"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class CreateMedia(Resource):
    @check_content
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("medias")
            return core.create(content["medias"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class FindMedia(Resource):
    @check_content
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("purpose")
            return core.find_media(content, content["purpose"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class UploadMedia(Resource):
    def post(self, media_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.upload(media_id, client, is_device)
        except InvalidAuthentication as ie:
            return FAILED(ie)


class MediaRequest(Resource):
    @check_content
    @secured_route
    def post(self, content, client, is_device):
        try:
            content_checker("media_id")
            return core.retrieve(content["media_id"], client, is_device)
        except ContentNotFound as cnf:
            return FAILED(cnf)


class GetMediaRequest(Resource):
    def get(self, media_id):
        try:
            client, is_device = get_any_from_header(request)
            return core.retrieve(media_id, client, is_device)
        except InvalidAuthentication as ie:
            return FAILED(ie)
