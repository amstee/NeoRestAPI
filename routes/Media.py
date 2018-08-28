from flask_restful import Resource
from flask import request
from config.database import db
from models.Message import Message
from models.Media import Media
from utils.decorators import secured_route, check_content, secured_admin_route
from utils.apiUtils import *
from utils.contentChecker import content_checker
from utils.security import user_has_access_to_message, device_has_access_to_message
from config.log import logger_set
from traceback import format_exc as traceback_format_exc

logger = logger_set(__name__)


class MediaInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("media_id")
            media = db.session.query(Media).filter(Media.id == content["media_id"]).first()
            if media is None:
                resp = FAILED("Media introuvable")
            elif user_has_access_to_message(media.message, user):
                resp = jsonify({"success": True, "content": media.get_simple_content()})
            else:
                resp = FAILED("Vous n'avez pas access a ce message")
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class DeviceMediaInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("media_id")
            media = db.session.query(Media).filter(Media.id == content["media_id"]).first()
            if media is None:
                resp = FAILED("Media introuvable")
            elif device_has_access_to_message(media.message, device):
                resp = jsonify({"success": True, "content": media.get_simple_content()})
            else:
                resp = FAILED("Vous n'avez pas access a ce message")
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class MediaInfoAdmin(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("media_id")
            media = db.session.query(Media).filter(Media.id == content["media_id"]).first()
            if media is None:
                resp = FAILED("Media introuvable")
            else:
                resp = jsonify({"success": True, "content": media.get_content()})
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class MediaDelete(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("media_id")
            media = db.session.query(Media).filter(Media.id == content["media_id"]).first()
            if media is None:
                resp = FAILED("Media introuvable")
            else:
                db.session.delete(media)
                db.session.commit()
                resp = SUCCESS()
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class MediaList(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("message_id")
            message = db.session.query(Message).filter(Message.id == content["message_id"]).first()
            if message is None:
                resp = FAILED("Message introuvable")
            elif user_has_access_to_message(message, user):
                resp = jsonify({"success": True, "content": [media.get_content() for media in message.media_links]})
            else:
                resp = FAILED("Vous n'avez pas access a ce message")
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class DeviceMediaList(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("message_id")
            message = db.session.query(Message).filter(Message.id == content["message_id"]).first()
            if message is None:
                resp = FAILED("Message introuvable")
            elif device_has_access_to_message(message, device):
                resp = jsonify({"success": True, "content": [link.media.get_simple_content() for
                                                             link in message.media_links]})
            else:
                resp = FAILED("Vous n'avez pas access a ce message")
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp


class MediaUpdate(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("media_id")
            media = db.session.query(Media).filter(Media.id == content["media_id"]).first()
            if media is None:
                resp = FAILED("Media introuvable")
            else:
                filename = content["filename"] if "filename" in content else None
                extension = content["extension"] if "extension" in content else None
                directory = content["directory"] if "directory" in content else None
                identifier = content["identifier"] if "identifier" in content else None
                media.update_content(filename=filename, extension=extension, directory=directory, identifier=identifier)
                resp = SUCCESS()
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
        except Exception as e:
            resp = FAILED(e)
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, resp.status_code, traceback_format_exc())
        return resp
