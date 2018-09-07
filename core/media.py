from flask import request
from config.database import db
from models.Message import Message
from models.Media import Media
from utils.apiUtils import *
from utils.security import user_has_access_to_message, device_has_access_to_message
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc
from config.log import LOG_MEDIA_FILE

logger = logger_set(module=__name__, file=LOG_MEDIA_FILE)


def media_list(message_id, client, is_device):
    try:
        message = db.session.query(Message).filter(Message.id == message_id).first()
        if message is None:
            resp = FAILED("Message introuvable")
        elif not is_device and user_has_access_to_message(message, client):
            resp = jsonify({"success": True, "content": [media.get_content() for media in message.media_links]})
        elif is_device and device_has_access_to_message(message, client):
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


def delete(media_id):
    try:
        media = db.session.query(Media).filter(Media.id == media_id).first()
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


def info(media_id, client, is_device):
    try:
        media = db.session.query(Media).filter(Media.id == media_id).first()
        if media is None:
            resp = FAILED("Media introuvable")
        elif not is_device and user_has_access_to_message(media.message, client):
            resp = jsonify({"success": True, "content": media.get_simple_content()})
        elif is_device and device_has_access_to_message(media.message, client):
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


def admin_update(content, media_id):
    try:
        media = db.session.query(Media).filter(Media.id == media_id).first()
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


def admin_info(media_id):
    try:
        media = db.session.query(Media).filter(Media.id == media_id).first()
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
