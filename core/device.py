from flask import request
from models.Device import Device
from models.Circle import Circle
from models.User import User
from config.database import db
from utils.apiUtils import *
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc
from config.log import LOG_DEVICE_FILE

logger = logger_set(module=__name__, file=LOG_DEVICE_FILE)


def is_username_available(username):
    try:
        device = db.session.query(Device).filter(Device.username == username).first()
        if device is not None:
            resp = FAILED("Le nom de device existe déja.")
        else:
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


def logout(device_token):
    try:
        res, data = Device.decode_auth_token(device_token)
        if res is True:
            data.disconnect()
            data.circle.notify_users(p2={'event': 'device', 'type': 'disconnect', 'device_id': data.id})
            resp = SUCCESS()
        else:
            resp = jsonify({"success": True, "message": data})
            resp.status_code = 403
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def check_token(_, __):
    try:
        resp = jsonify({"success": True, "message": "Le token json de ce device est valide"})
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def modify_password(username, prev, new):
    try:
        device = db.session.query(Device).filter(Device.username == username).first()
        if device is not None:
            if device.check_password(prev):
                device.update_password(new)
                resp = SUCCESS()
            else:
                resp = FAILED("Ancien mot de passe invalide")
        else:
            resp = FAILED("Device introuvable")
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def login(username, password):
    try:
        device = db.session.query(Device).filter(Device.username == username).first()
        if device is not None:
            res, data = device.authenticate(password)
            if res is True:
                resp = jsonify({"success": True, "device_token": data})
                resp.status_code = 200
                device.circle.notify_users(p2={'event': 'device', 'type': 'connect', 'device_id': device.id})
            else:
                resp = FAILED(data)
        else:
            resp = FAILED("Device introuvable")
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def info(device_id, client, is_device):
    try:
        device = db.session.query(Device).filter(Device.id == device_id).first()
        if device is not None:
            if not is_device and not device.circle.has_member(client):
                resp = FAILED("Vous n'appartenez pas au cercle de ce device", 403)
            elif is_device and device.id != client.id:
                resp = FAILED("Vous n'appartenez pas au cercle de ce device", 403)
            else:
                resp = jsonify({"success": True, "content": device.get_content()})
        else:
            resp = FAILED("Le NEO avec identifiant %s n'existe pas" % str(device_id))
            resp.status_code = 401
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def update(content, device_id, client, is_device):
    try:
        device = db.session.query(Device).filter(Device.id == device_id).first()
        if device is None:
            resp = FAILED("Device introuvable")
        elif not is_device and not device.circle.has_admin(client):
            resp = FAILED("Privileges insuffisants", 403)
        elif is_device and device_id != client.id:
            resp = FAILED("Vous ne pouvez pas modifier un autre device", 403)
        else:
            device.update_content(name=content['name'] if "name" in content else None)
            device.circle.notify_users(p2={'event': 'device', 'type': 'update', 'device_id': device.id})
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


def admin_credentials(device_id):
    try:
        device = db.session.query(Device).filter(Device.id == device_id).first()
        if device is None:
            resp = FAILED("Device Neo introuvable")
        else:
            resp = jsonify({"success": True, "content": {
                "key": device.key,
                "username": device.username,
                "password": device.get_pre_activation_password()
            }})
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def admin_activate(device_id, activation_key):
    try:
        device = db.session.query(Device).filter(Device.id == device_id).first()
        if device is not None:
            res = device.activate(activation_key)
            if res:
                resp = SUCCESS()
            else:
                resp = FAILED("Clé d'activation invalide")
        else:
            resp = FAILED("Le Neo avec identifiant id %s n'existe pas" % str(device_id))
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def admin_add(content, circle_id, name):
    try:
        circle = db.session.query(Circle).filter(Circle.id == circle_id).first()
        new_device = Device(name=name, username=content["username"] if "username" in content else None)
        new_device.circle = circle
        db.session.commit()
        circle.notify_users('device created')
        resp = SUCCESS()
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        resp.status_code = 409
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def admin_delete(device_id):
    try:
        device = db.session.query(Device).filter(Device.id == device_id).first()
        if device is not None:
            db.session.delete(device)
            db.session.commit()
            resp = SUCCESS()
        else:
            resp = FAILED("Le NEO avec identifiant id %s n'existe pas" % str(device_id))
            resp.status_code = 401
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def admin_list(email):
    try:
        user = db.session.query(User).filter(User.email == email).first()
        if user is not None:
            if len(user.circle_link) > 0:
                for link in user.circle_link:
                    if link.privilege == "ADMIN":
                        devices = db.session.query(Device).filter(Device.circle_id == link.circle_id)
                        resp = jsonify({"success": True, "devices": [device.get_simple_content() for device in devices]})
                    else:
                        resp = FAILED("Aucun NEO n'appartient à cet utilisateur")
            else:
                resp = FAILED("L'utilisateur n'appartient à aucun cercle")
        else:
            resp = FAILED("Le NEO avec l'email %s n'existe pas" % str(email))
            resp.status_code = 401
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp
