from flask import send_from_directory
from flask import request
from flask_restful import Resource
from config.database import db_session
from models.Media import Media
from models.Message import Message
from utils.decorators import securedRoute, checkContent, securedDeviceRoute
from utils.contentChecker import contentChecker
from utils.apiUtils import *
from utils.security import userHasAccessToMedia, deviceHasAccessToMedia, userIsOwnerOfMedia, deviceIsOwnerOfMessage
from utils.security import getUserFromHeader, getDeviceFromHeader, deviceIsOwnerOfMedia
from flask_socketio import emit


class UploadMedia(Resource):
    def post(self, media_id):
        try:
            user = getUserFromHeader(request)
            media = db_session.query(Media).filter(Media.id == media_id).first()
            if media is None:
                return FAILED("Media introuvable")
            if userIsOwnerOfMedia(media, user):
                if 'file' in request.files:
                    message = media.message_link.message
                    media.set_content(request.files['file'], "conversation_" + str(message.conversation.id))
                    media.upload(request.files['file'])
                    db_session.commit()
                    emit('message', {
                        'conversation_id': message.conversation.id,
                        'message': message.getSimpleContent(),
                        'time': message.sent,
                        'sender': user.getSimpleContent(),
                        'media': media.getSimpleContent(),
                        'status': 'done'},
                         room='conversation_' + str(message.conversation.id), namespace='/')
                    return SUCCESS()
                return FAILED("Fichier introuvable dans la requete")
            return FAILED('Vous ne pouvez pas upload de media pour ce message')
        except Exception as e:
            return FAILED(e)


class DeviceUploadMedia(Resource):
    def post(self, media_id):
        try:
            device = getDeviceFromHeader(request)
            media = db_session.query(Media).filter(Media.id == media_id).first()
            if media is None:
                return FAILED("Media introuvable")
            if deviceIsOwnerOfMedia(media, device):
                if 'file' in request.files:
                    message = media.message_link.message
                    media.set_content(request.files['file'], "conversation_" + str(message.conversation.id))
                    media.upload(request.files['file'])
                    db_session.commit()
                    emit('message', {
                        'conversation_id': message.conversation.id,
                        'message': message.getSimpleContent(),
                        'time': message.sent,
                        'sender': device.getSimpleContent(),
                        'media': media.getSimpleContent(),
                        'status': 'done'},
                         room='conversation_' + str(message.conversation.id), namespace='/')
                    return SUCCESS()
                return FAILED("Fichier introuvable dans la requete")
            return FAILED('Vous ne pouvez pas upload de media pour ce message')
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
            if userHasAccessToMedia(media, user):
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
            if deviceHasAccessToMedia(media, device):
                return send_from_directory(media.getDirectory(), media.getFullName())
            else:
                return FAILED("L'utilisateur ne peut pas acceder a ce media")
        except Exception as e:
            return FAILED(e)