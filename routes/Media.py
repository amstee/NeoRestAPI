from flask import request
from flask_restful import Resource
from config.database import db_session
from models.MessageToMedia import MessageToMedia
from models.CircleToMedia import CircleToMedia
from models.DeviceToMedia import DeviceToMedia
from models.UserToMedia import UserToMedia
from models.Message import Message
from models.Media import Media
from utils.decorators import securedRoute, checkContent, securedAdminRoute, securedDeviceRoute
from utils.apiUtils import *
from utils.contentChecker import contentChecker
from utils.security import userHasAccessToMessage, deviceHasAccessToMessage


class MediaInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("media_id")
            media = db_session.query(Media).filter(Media.id==content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            if userHasAccessToMessage(media.message, user):
                return jsonify({"success": True, "content": media.getSimpleContent()})
            return FAILED("Vous n'avez pas access a ce message")
        except Exception as e:
            return FAILED(e)


class DeviceMediaInfo(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        try:
            contentChecker("media_id")
            media = db_session.query(Media).filter(Media.id==content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            if deviceHasAccessToMessage(media.message, device):
                return jsonify({"success": True, "content": media.getSimpleContent()})
            return FAILED("Vous n'avez pas access a ce message")
        except Exception as e:
            return FAILED(e)


class MediaInfoAdmin(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content, admin):
        try:
            contentChecker("media_id")
            media = db_session.query(Media).filter(Media.id==content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            return jsonify({"success": True, "content": media.getContent()})
        except Exception as e:
            return FAILED(e)


class MediaDelete(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content, admin):
        try:
            contentChecker("media_id")
            media = db_session.query(Media).filter(Media.id == content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            db_session.delete(media)
            db_session.commit()
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class MediaList(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("message_id")
            message = db_session.query(Message).filter(Message.id==content["message_id"]).first()
            if message is None:
                return FAILED("Message introuvable")
            if userHasAccessToMessage(message, user):
                return jsonify({"success": True, "content": [media.getContent() for media in message.media_links]})
            return FAILED("Vous n'avez pas access a ce message")
        except Exception as e:
            return FAILED(e)


class DeviceMediaList(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        try:
            contentChecker("message_id")
            message = db_session.query(Message).filter(Message.id==content["message_id"]).first()
            if message is None:
                return FAILED("Message introuvable")
            if deviceHasAccessToMessage(message, device):
                return jsonify({"success": True, "content": [link.media.getSimpleContent() for link in message.media_links]})
            return FAILED("Vous n'avez pas access a ce message")
        except Exception as e:
            return FAILED(e)


class MediaUpdate(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content, admin):
        try:
            contentChecker("media_id")
            media = db_session.query(Media).filter(Media.id==content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            filename = content["filename"] if "filename" in content else None
            extension = content["extension"] if "extension" in content else None
            directory = content["directory"] if "directory" in content else None
            identifier = content["identifier"] if "identifier" in content else None
            media.updateContent(filename=filename, extension=extension, directory=directory, identifier=identifier)
            return SUCCESS()
        except Exception as e:
            return FAILED(e)
