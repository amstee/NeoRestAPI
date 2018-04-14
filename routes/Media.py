from flask import request
from flask_restful import Resource
from config.database import db_session
from models.Message import Message
from models.Media import Media
from utils.decorators import securedRoute, checkContent, securedAdminRoute
from utils.apiUtils import *
from werkzeug.utils import secure_filename
import os


class MediaCreate(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content):
        try:
            message = db_session.query(Message).filter(Message.id==content["message_id"]).first()
            if message is None:
                return FAILED("Message auquel attacher le media introuvable")
            file_list = content["files"]
            for file in file_list:
                if file in request.files:
                    new_file = Media().setContent(request.files[file], content["directory_name"], message)
                    message.medias.append(new_file)
            db_session.commit()
        except Exception as e:
            return FAILED(e)


class MediaInfo(Resource):
    @checkContent
    @securedRoute
    def post(self, content):
        try:
            media = db_session.query(Media).filter(Media.id==content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            return jsonify({"success": True, "content": media.getSimpleContent()})
        except Exception as e:
            return FAILED(e)


class MediaInfoAdmin(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content):
        try:
            media = db_session.query(Media).filter(Media.id==content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            return jsonify({"success": True, "content": media.getContent()})
        except Exception as e:
            return FAILED(e)


class MediaDelete(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content):
        try:
            media = db_session.query(Media).filter(Media.id == content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            db_session.delete(media)
            return SUCCESS()
        except Exception as e:
            return FAILED(e)


class MediaList(Resource):
    @checkContent
    @securedRoute
    def post(self, content):
        try:
            message = db_session.query(Message).filter(Message.id==content["message_id"]).first()
            if message is None:
                return FAILED("Message introuvable")
            return jsonify({"success": True, "content": [media.getSimpleContent() for media in message.medias]})
        except Exception as e:
            return FAILED(e)


class MediaUpdate(Resource):
    @checkContent
    @securedAdminRoute
    def post(self, content):
        try:
            media = db_session.query(Media).filter(Media.id==content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            media.updateContent(filename=content["filename"], extension=content["extension"], directory=content["directory"])
            return SUCCESS()
        except Exception as e:
            return FAILED(e)
