from flask import send_from_directory
from flask import request
from config.database import db
from models.Media import Media
from models.UserToMedia import UserToMedia
from models.DeviceToMedia import DeviceToMedia
from models.CircleToMedia import CircleToMedia
from models.Circle import Circle
from utils.contentChecker import content_checker
from flask_socketio import emit
from utils.log import logger_set
from config.log import LOG_MEDIA_FILE
from datauri import DataURI
from exceptions import media as e_media
from exceptions import circle as e_circle

logger = logger_set(module=__name__, file=LOG_MEDIA_FILE)


def retrieve(media_id, client, is_device):
    try:
        media = db.session.query(Media).filter(Media.id == media_id).first()
        if media is None or media.uploaded is False:
            raise e_media.MediaNotFound
        if not (not is_device and media.can_be_accessed_by_user(client)) and \
                not (is_device and media.can_be_accessed_by_device(client)):
            raise e_media.ForbiddenAccess
        if not media.file_exist():
            raise e_media.MediaNotFoundInSystem
        data_uri = DataURI.from_file(media.get_full_path())
        response = {
            "data": {"success": True, "data": data_uri},
            "status_code": 200
        }
    except e_media.MediaException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def upload(media_id, client, is_device):
    try:
        media = db.session.query(Media).filter(Media.id == media_id).first()
        if media is None:
            raise e_media.MediaNotFound
        if not (is_device and media.can_be_uploaded_by_device(client)) and \
                not (not is_device and media.can_be_uploaded_by_user(client)):
            raise e_media.ForbiddenUpload
        if 'file' not in request.files:
            raise e_media.MediaNotFoundInRequest
        media.set_content(request.files['file'])
        media.upload(request.files['file'])
        db.session.commit()
        if media.is_attached_to_message():
            message = media.message_link.message
            emit('message', {
                'conversation_id': message.conversation.id,
                'message': message.get_simple_json_compliant_content(),
                'sender': client.get_simple_json_compliant_content(),
                'media': media.get_simple_content(),
                'status': 'done'},
                 room='conversation_' + str(message.conversation.id), namespace='/')
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_media.MediaException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def find_media(content, purpose, client, is_device):
    try:
        if "circle_id" in content:
            medias = db.session.query(CircleToMedia).filter(CircleToMedia.circle_id == content["circle_id"],
                                                            CircleToMedia.purpose == purpose).all()
        elif "user_id" in content:
            medias = db.session.query(UserToMedia).filter(UserToMedia.user_id == content["user_id"],
                                                          UserToMedia.purpose == purpose).all()
        elif "device_id" in content:
            medias = db.session.query(DeviceToMedia).filter(DeviceToMedia.device_id == content["device_id"],
                                                            DeviceToMedia.purpose == purpose).all()
        elif is_device:
            medias = db.session.query(DeviceToMedia).filter(DeviceToMedia.device_id == client.id,
                                                            DeviceToMedia.purpose == purpose).all()
        else:
            medias = db.session.query(UserToMedia).filter(UserToMedia.user_id == client.id,
                                                          UserToMedia.purpose == purpose).all()
        response = {
            "data": {"success": True, "media_list": [media.get_simple_content() for media in medias]},
            "status_code": 200
        }
    except e_media.MediaException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def create(medias, client, is_device):
    try:
        content_checker("medias")
        ml = []
        for media in medias:
            if "purpose" not in media:
                raise e_media.PurposeNotFound
            if "circle_id" in media:
                circle = db.session.query(Circle).filter(Circle.id == media["circle_id"]).first()
                if circle is None:
                    raise e_circle.CircleNotFound
                link = CircleToMedia()
                link.circle = circle
            elif "device_id" in media or is_device:
                link = DeviceToMedia()
                link.device = client
            else:
                link = UserToMedia()
                link.user = client
            link.purpose = media["purpose"]
            m = Media(filename=media["name"])
            link.media = m
            db.session.commit()
            ml.append(m)
        response = {
            "data": {"success": True, "media_list": [me.get_simple_content() for me in ml]},
            "status_code": 200
        }
    except (e_media.MediaException, e_circle.CircleException) as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def delete(media_id, client, is_device):
    try:
        media = db.session.query(Media).filter(Media.id == media_id).first()
        if media is None:
            raise e_media.MediaNotFound
        if not (not is_device and media.can_be_uploaded_by_user(client)) and \
                not (is_device and media.can_be_uploaded_by_device(client)):
            raise e_media.ForbiddenAccess
        db.session.delete(media)
        db.session.commit()
        response = {
            "data": {"success": True},
            "status_code": 200
        }
    except e_media.MediaException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response
