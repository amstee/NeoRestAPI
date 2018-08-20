from flask_restful import Resource
from config.database import db
from models.Message import Message
from models.Media import Media
from utils.decorators import secured_route, check_content, secured_admin_route
from utils.apiUtils import *
from utils.contentChecker import content_checker
from utils.security import user_has_access_to_message, device_has_access_to_message


class MediaInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("media_id")
            media = db.session.query(Media).filter(Media.id == content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            if user_has_access_to_message(media.message, user):
                return jsonify({"success": True, "content": media.get_simple_content()})
            return FAILED("Vous n'avez pas access a ce message")
        except Exception as e:
            return FAILED(e)


class DeviceMediaInfo(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("media_id")
            media = db.session.query(Media).filter(Media.id == content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            if device_has_access_to_message(media.message, device):
                return jsonify({"success": True, "content": media.get_simple_content()})
            return FAILED("Vous n'avez pas access a ce message")
        except Exception as e:
            return FAILED(e)


class MediaInfoAdmin(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("media_id")
            media = db.session.query(Media).filter(Media.id == content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            return jsonify({"success": True, "content": media.get_content()})
        except Exception as e:
            return FAILED(e)


class MediaDelete(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("media_id")
            media = db.session.query(Media).filter(Media.id == content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            db.session.delete(media)
            db.session.commit()
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class MediaList(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        try:
            content_checker("message_id")
            message = db.session.query(Message).filter(Message.id == content["message_id"]).first()
            if message is None:
                return FAILED("Message introuvable")
            if user_has_access_to_message(message, user):
                return jsonify({"success": True, "content": [media.get_content() for media in message.media_links]})
            return FAILED("Vous n'avez pas access a ce message")
        except Exception as e:
            return FAILED(e)


class DeviceMediaList(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        try:
            content_checker("message_id")
            message = db.session.query(Message).filter(Message.id == content["message_id"]).first()
            if message is None:
                return FAILED("Message introuvable")
            if device_has_access_to_message(message, device):
                return jsonify({"success": True, "content": [link.media.get_simple_content() for
                                                             link in message.media_links]})
            return FAILED("Vous n'avez pas access a ce message")
        except Exception as e:
            return FAILED(e)


class MediaUpdate(Resource):
    @check_content
    @secured_admin_route
    def post(self, content, admin):
        try:
            content_checker("media_id")
            media = db.session.query(Media).filter(Media.id == content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            filename = content["filename"] if "filename" in content else None
            extension = content["extension"] if "extension" in content else None
            directory = content["directory"] if "directory" in content else None
            identifier = content["identifier"] if "identifier" in content else None
            media.update_content(filename=filename, extension=extension, directory=directory, identifier=identifier)
            return SUCCESS()
        except Exception as e:
            return FAILED(e)
