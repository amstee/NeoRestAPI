from flask import send_from_directory
from flask import request
from config.database import db
from models.Media import Media
from models.UserToMedia import UserToMedia
from models.DeviceToMedia import DeviceToMedia
from models.CircleToMedia import CircleToMedia
from models.Circle import Circle
from utils.contentChecker import content_checker
from utils.apiUtils import *
from flask_socketio import emit
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc
from config.log import LOG_MEDIA_FILE
from datauri import DataURI

logger = logger_set(module=__name__, file=LOG_MEDIA_FILE)


def retrieve(media_id, client, is_device):
    try:
        media = db.session.query(Media).filter(Media.id == media_id).first()
        if media is None or media.uploaded is False:
            resp = FAILED("Media introuvable")
        elif (not is_device and media.can_be_accessed_by_user(client)) or \
                (is_device and media.can_be_accessed_by_device(client)):
            if media.file_exist():
                data_uri = DataURI.from_file(media.get_full_path())
                resp = jsonify({"success": True, "data": data_uri})
            else:
                resp = FAILED("Le media est introuvable sur le FS")
        else:
            resp = FAILED("L'utilisateur ne peut pas acceder a ce media")
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def upload(media_id, client, is_device):
    try:
        media = db.session.query(Media).filter(Media.id == media_id).first()
        if media is None:
            resp = FAILED("Media introuvable")
        elif (is_device and media.can_be_uploaded_by_device(client)) or \
                (not is_device and media.can_be_uploaded_by_user(client)):
            if 'file' in request.files:
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
                resp = SUCCESS()
            else:
                resp = FAILED("Fichier introuvable dans la requete")
        else:
            resp = FAILED("Vous ne pouvez pas upload ce media")
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


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
        resp = jsonify({"success": True, "media_list": [media.get_simple_content() for media in medias]})
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def create(medias, client, is_device):
    logger.info("[%s] [%s] [%s] [%s] [%s]",
                request.method, request.host, request.path, request.content_type, request.data)
    try:
        content_checker("medias")
        ml = []
        for media in medias:
            if "purpose" not in media:
                resp = FAILED("Purpose not specified")
                logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                            request.method, request.host, request.path,
                            request.content_type, request.data, resp.status_code)
                return resp
            if "circle_id" in media:
                circle = db.session.query(Circle).filter(Circle.id == media["circle_id"]).first()
                if circle is None:
                    resp = FAILED("Cercle introuvable")
                    logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                                request.method, request.host, request.path,
                                request.content_type, request.data, resp.status_code)
                    return resp
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
        resp = jsonify({"success": True, "media_list": [me.get_simple_content() for me in ml]})
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def delete(media_id, client, is_device):
    logger.info("[%s] [%s] [%s] [%s] [%s]",
                request.method, request.host, request.path, request.content_type, request.data)
    try:
        media = db.session.query(Media).filter(Media.id == media_id).first()
        if media is None:
            resp = FAILED("Media introuvable")
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, resp.status_code)
            return resp
        if (not is_device and media.can_be_uploaded_by_user(client)) or \
                (is_device and media.can_be_uploaded_by_device(client)):
            db.session.delete(media)
            db.session.commit()
            resp = SUCCESS()
        else:
            resp = FAILED("Vous n'avez pas les droits necessaires")
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp
