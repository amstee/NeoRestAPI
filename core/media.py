from config.database import db
from models.Message import Message
from models.Media import Media
from utils.security import user_has_access_to_message, device_has_access_to_message
from utils.security import user_has_access_to_media, device_has_access_to_media
from exceptions import message as e_message
from exceptions import media as e_media


def media_list(message_id, client, is_device):
    try:
        message = db.session.query(Message).filter(Message.id == message_id).first()
        if message is None:
            raise e_message.MessageNotFound
        if (not is_device and not user_has_access_to_message(message, client)) or \
                (is_device and not device_has_access_to_message(message, client)):
            raise e_message.ForbiddenAccess
        response = {
            "data": {"success": True, "content": [media.get_content() for media in message.media_links]},
            "status_code": 200
        }
    except e_message.MessageException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def delete(media_id):
    try:
        media = db.session.query(Media).filter(Media.id == media_id).first()
        if media is None:
            raise e_media.MediaNotFound
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


def info(media_id, client, is_device):
    try:
        media = db.session.query(Media).filter(Media.id == media_id).first()
        if media is None:
            raise e_media.MediaNotFound
        if (not is_device and not user_has_access_to_media(media, client)) or \
                (is_device and not device_has_access_to_media(media, client)):
            raise e_message.ForbiddenAccess
        response = {
            "data": {"success": True, "content": media.get_simple_content()},
            "status_code": 200
        }
    except (e_media.MediaException, e_message.MessageException) as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response


def admin_update(content, media_id):
    try:
        media = db.session.query(Media).filter(Media.id == media_id).first()
        if media is None:
            raise e_media.MediaNotFound
        filename = content["filename"] if "filename" in content else None
        extension = content["extension"] if "extension" in content else None
        directory = content["directory"] if "directory" in content else None
        identifier = content["identifier"] if "identifier" in content else None
        media.update_content(filename=filename, extension=extension, directory=directory, identifier=identifier)
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


def admin_info(media_id):
    try:
        media = db.session.query(Media).filter(Media.id == media_id).first()
        if media is None:
            raise e_media.MediaNotFound
        response = {
            "data": {"success": True, "content": media.get_content()},
            "status_code": 200
        }
    except e_media.MediaException as exception:
        response = {
            "data": {"success": False, "message": exception.message},
            "status_code": exception.status_code
        }
    return response
