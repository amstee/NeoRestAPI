from flask import send_from_directory
from flask import request
from flask_restful import Resource
from config.database import db_session
from models.Media import Media
from models.Message import Message
from utils.decorators import securedRoute, checkContent, securedDeviceRoute
from utils.contentChecker import contentChecker
from utils.apiUtils import *
from utils.security import userHasAccessToMessage, deviceHasAccessToMessage, userIsOwnerOfMessage, deviceIsOwnerOfMessage
from flask_socketio import emit


class UploadMedia(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            contentChecker("message_id", "media_list")
            medias = content["media_list"]
            message = db_session.query(Message).filter(Message.id == content["message_id"]).first()
            if userIsOwnerOfMessage(message, user):
                for info in medias:
                    media = db_session.query(Media).filter(Media.id == info.id).first()
                    if media is None:
                        return FAILED("Media introuvable")
                    if info.filename in request.files:
                        media.set_content(request.files[info.filename], "conversation_" + str(message.conversation.id))
                        media.upload(request.files[info.filename])
                        db_session.commit()
                emit('message', {
                    'conversation_id': message.conversation.id,
                    'message': message.getSimpleContent(),
                    'time': message.sent,
                    'sender': user.getSimpleContent(),
                    'media_list': medias,
                    'status': 'done'},
                     room='conversation_' + message.conversation.id, namespace='/')
                return SUCCESS()
            return FAILED('Vous ne pouvez pas upload de media pour ce message')
        except Exception as e:
            return FAILED(e)


class DeviceUploadMedia(Resource):
    @checkContent
    @securedDeviceRoute
    def post(self, content, device):
        try:
            contentChecker("message_id", "media_list")
            medias = content["media_list"]
            message = db_session.query(Message).filter(Message.id == content["message_id"]).first()
            if deviceIsOwnerOfMessage(message, device):
                for info in medias:
                    media = db_session.query(Media).filter(Media.id == info.id).first()
                    if media is None:
                        return FAILED("Media introuvable")
                    if info.filename in request.files:
                        media.set_content(request.files[info.filename], "conversation_" + str(message.conversation.id))
                        media.upload(request.files[info.filename])
                        db_session.commit()
                emit('message', {
                    'conversation_id': message.conversation.id,
                    'message': message.getSimpleContent(),
                    'time': message.sent,
                    'sender': device.getSimpleContent(),
                    'media_list': medias,
                    'status': 'done'},
                     room='conversation_' + message.conversation.id, namespace='/')
                return SUCCESS()
            return FAILED("Vous ne pouvez pas upload de media pour ce message")
        except Exception as e:
            return FAILED(e)


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
                return send_from_directory(media.getDirectory(), media.getFullName())
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
                return send_from_directory(media.getDirectory(), media.getFullName())
            else:
                return FAILED("L'utilisateur ne peut pas acceder a ce media")
        except Exception as e:
            return FAILED(e)