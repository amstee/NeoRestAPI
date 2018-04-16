from flask import send_from_directory
from flask_restful import Resource
from config.database import db_session
from models.Media import Media
from utils.decorators import securedRoute, checkContent, securedDeviceRoute
from utils.contentChecker import contentChecker
from utils.apiUtils import *
from utils.security import userHasAccessToMessage, deviceHasAccessToMessage


class MediaRequest(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("media_id")
            media = db_session.query(Media).filter(Media.id==content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            if userHasAccessToMessage(media.message, user):
                return send_from_directory(media.directory, media.filename + media.extension)
            else:
                return FAILED("L'utilisateur ne peut pas acceder a ce media")
        except Exception as e:
            return FAILED(e)


class DeviceMediaRequest(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        try:
            contentChecker("media_id")
            media = db_session.query(Media).filter(Media.id==content["media_id"]).first()
            if media is None:
                return FAILED("Media introuvable")
            if deviceHasAccessToMessage(media.message, device):
                return send_from_directory(media.directory, media.filename + media.extension)
            else:
                return FAILED("L'utilisateur ne peut pas acceder a ce media")
        except Exception as e:
            return FAILED(e)