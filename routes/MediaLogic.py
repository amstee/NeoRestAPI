from flask import send_from_directory
from flask import request
from flask_restful import Resource
from config.database import db
from models.Media import Media
from models.UserToMedia import UserToMedia
from models.DeviceToMedia import DeviceToMedia
from models.CircleToMedia import CircleToMedia
from models.Circle import Circle
from utils.decorators import secured_route, check_content
from utils.contentChecker import content_checker
from utils.apiUtils import *
from utils.security import get_user_from_header, get_device_from_header
from flask_socketio import emit
from config.log import logger_set

logger = logger_set(__name__)


class CreateMedia(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            content_checker("medias")
            ml = []
            for media in content["medias"]:
                if "purpose" not in media:
                    return FAILED("Purpose not specified")
                if "circle_id" in media:
                    circle = db.session.query(Circle).filter(Circle.id == media["circle_id"]).first()
                    if circle is None:
                        return FAILED("Cercle introuvable")
                    link = CircleToMedia()
                    link.circle = circle
                elif "device_id" in media:
                    link = DeviceToMedia()
                else:
                    link = UserToMedia()
                    link.user = user
                link.purpose = media["purpose"]
                m = Media(filename=media["name"])
                link.media = m
                db.session.commit()
                ml.append(m)
            return jsonify({"success": True, "media_list": [me.get_simple_content() for me in ml]})
        except Exception as e:
            return FAILED(e)


class DeviceCreateMedia(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            content_checker("medias")
            ml = []
            for media in content["medias"]:
                if "purpose" not in media:
                    return FAILED("Purpose not specified")
                if "circle_id" in media:
                    circle = db.session.query(Circle).filter(Circle.id == media["circle_id"]).first()
                    if circle is None:
                        return FAILED("Cercle introuvable")
                    link = CircleToMedia()
                    link.circle = circle
                else:
                    link = DeviceToMedia()
                    link.device = device
                link.purpose = media["purpose"]
                m = Media(filename=media["name"])
                link.media = m
                db.session.commit()
                ml.append(m)
            return jsonify({"success": True, "media_list": [me.get_simple_content() for me in ml]})
        except Exception as e:
            return FAILED(e)


class DeviceFindMedia(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            content_checker("purpose")
            if "circle_id" in content:
                medias = db.session.query(CircleToMedia).filter(CircleToMedia.circle_id == content["circle_id"],
                                                                CircleToMedia.purpose == content["purpose"]).all()
            elif "user_id" in content:
                medias = db.session.query(UserToMedia).filter(UserToMedia.user_id == content["user_id"],
                                                              UserToMedia.purpose == content["purpose"]).all()
            else:
                medias = db.session.query(DeviceToMedia).filter(DeviceToMedia.device_id == device.id,
                                                                DeviceToMedia.purpose == content["purpose"]).all()
            return jsonify({"success": True, "medias": [media.get_content() for media in medias]})
        except Exception as e:
            return FAILED(e)


class FindMedia(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            content_checker("purpose")
            if "circle_id" in content:
                medias = db.session.query(CircleToMedia).filter(CircleToMedia.circle_id == content["circle_id"],
                                                                CircleToMedia.purpose == content["purpose"]).all()
            elif "device_id" in content:
                medias = db.session.query(DeviceToMedia).filter(DeviceToMedia.device_id == content["device_id"],
                                                                DeviceToMedia.purpose == content["purpose"]).all()
            else:
                medias = db.session.query(UserToMedia).filter(UserToMedia.user_id == user.id,
                                                              UserToMedia.purpose == content["purpose"]).all()
            return jsonify({"success": True, "medias": [media.get_content() for media in medias]})
        except Exception as e:
            return FAILED(e)


class DeviceUploadMedia(Resource):
    def post(self, media_id):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            device = get_device_from_header(request)
            media = db.session.query(Media).filter(Media.id == media_id).first()
            if media is None:
                return FAILED("Media introuvable")
            if media.can_be_uploaded_by_device(device):
                if 'file' in request.files:
                    media.set_content(request.files['file'])
                    media.upload(request.files['file'])
                    db.session.commit()
                    if media.is_attached_to_message():
                        message = media.message_link.message
                        emit('message', {
                            'conversation_id': message.conversation.id,
                            'message': message.get_simple_json_compliant_content(),
                            'sender': device.get_simple_json_compliant_content(),
                            'media': media.get_simple_content(),
                            'status': 'done'},
                             room='conversation_' + str(message.conversation.id), namespace='/')
                    return SUCCESS()
                return FAILED("Fichier introuvable dans la requete")
            return FAILED("Vous ne pouvez pas upload ce media")
        except Exception as e:
            return FAILED(e)


class UploadMedia(Resource):
    def post(self, media_id):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            user = get_user_from_header(request)
            media = db.session.query(Media).filter(Media.id == media_id).first()
            if media is None:
                return FAILED("Media introuvable")
            if media.can_be_uploaded_by_user(user):
                if 'file' in request.files:
                    media.set_content(request.files['file'])
                    media.upload(request.files['file'])
                    db.session.commit()
                    if media.is_attached_to_message():
                        message = media.message_link.message
                        emit('message', {
                            'conversation_id': message.conversation.id,
                            'message': message.get_simple_json_compliant_content(),
                            'sender': user.get_simple_json_compliant_content(),
                            'media': media.get_simple_content(),
                            'status': 'done'},
                             room='conversation_' + str(message.conversation.id), namespace='/')
                    return SUCCESS()
                return FAILED("Fichier introuvable dans la requete")
            return FAILED("Vous ne pouvez pas upload ce media")
        except Exception as e:
            return FAILED(e)


class MediaRequest(Resource):
    @check_content
    @secured_route
    def post(self, content, user):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            content_checker("media_id")
            media = db.session.query(Media).filter(Media.id == content["media_id"]).first()
            if media is None or media.uploaded is False:
                return FAILED("Media introuvable")
            if media.can_be_accessed_by_user(user):
                if media.file_exist():
                    return send_from_directory(media.get_directory(), media.get_full_name())
                else:
                    return FAILED("Le media est introuvable sur le FS")
            else:
                return FAILED("L'utilisateur ne peut pas acceder a ce media")
        except Exception as e:
            return FAILED("E1 : " + str(e))


class DeviceMediaRequest(Resource):
    @check_content
    @secured_route
    def post(self, content, device):
        logger.info("[%s] [%s] [%s] [%s] [%s]",
                    request.method, request.host, request.path, request.content_type, request.data)
        try:
            content_checker("media_id")
            media = db.session.query(Media).filter(Media.id == content["media_id"]).first()
            if media is None or media.uploaded is False:
                return FAILED("Media introuvable")
            if media.can_be_accessed_by_device(device):
                if media.file_exist():
                    return send_from_directory(media.get_directory(), media.get_full_name())
                else:
                    return FAILED("Le media est introuvable sur le FS")
            else:
                return FAILED("L'utilisateur ne peut pas acceder a ce media")
        except Exception as e:
            return FAILED(e)
