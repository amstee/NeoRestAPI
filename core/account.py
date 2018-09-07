from flask import request
from config.database import db
from models.User import User as UserModel
from utils.contentChecker import content_checker
from utils.apiUtils import *
from utils.log import logger_set
from traceback import format_exc as traceback_format_exc
from config.log import LOG_ACCOUNT_FILE

logger = logger_set(module=__name__, file=LOG_ACCOUNT_FILE)


def create(content):
    try:
        content_checker("email", "password", "first_name", "last_name", "birthday")
        UserModel(email=content['email'], password=content['password'], first_name=content['first_name'],
                  last_name=content['last_name'], birthday=content["birthday"])
        db.session.commit()
        resp = jsonify({"success": True})
        resp.status_code = 201
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = jsonify({"success": False, "message": str(e)})
        resp.status_code = 409
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def login(email, password):
    try:
        user = db.session.query(UserModel).filter_by(email=email).first()
        if user is not None:
            res, data = user.authenticate(password)
            if res is True:
                resp = jsonify({"success": True, "token": data})
                resp.status_code = 200
                user.notify_circles({'event': 'connect', 'user': user.email})
            else:
                resp = jsonify({"success": False, "message": data})
                resp.status_code = 401
        else:
            resp = jsonify({"succes": False, "message": "Utilisateur introuvable"})
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


def modify_password(email, prev, new):
    try:
        user = db.session.query(UserModel).filter_by(email=email).first()
        if user is not None:
            if user.check_password(prev):
                user.update_password(new)
                resp = SUCCESS()
            else:
                resp = FAILED("Le mot de passe de correspond pas")
        else:
            resp = FAILED("Utilisateur introuvable")
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def check_token(json_token):
    try:
        res, data = UserModel.decode_auth_token(json_token)
        if res is True:
            resp = jsonify({"success": True, "message": "Le token json est valide"})
        else:
            resp = jsonify({"success": False, "message": data})
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = jsonify({"success": False, "message": str(e)})
        resp.status_code = 500
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def logout(token):
    try:
        res, data = UserModel.decode_auth_token(token)
        if res:
            disco_res, message = data.disconnect()
            if disco_res is True:
                resp = jsonify({"success": True})
                data.notify_circles({'event': 'disconnect', 'user': data.email})
            else:
                resp = jsonify({"success": False, "message": message})
                resp.status_code = 403
        else:
            resp = jsonify({"success": False, "message": data})
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


def get_info(user_id, client, is_device):
    try:
        user = db.session.query(UserModel).filter(UserModel.id == user_id).first()
        if user is None:
            resp = FAILED("Utilisateur introuvable")
        elif is_device and not client.circle.has_member(user):
            resp = FAILED("Vous ne pouvez pas voir cet utilisateur")
        else:
            resp = jsonify({"success": True, "content": user.get_content()})
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def update(content, user):
    try:
        email = None if 'email' not in content else content['email']
        first_name = None if 'first_name' not in content else content['first_name']
        last_name = None if 'last_name' not in content else content['last_name']
        birthday = None if 'birthday' not in content else content['birthday']
        user.update_content(email=email,
                            first_name=first_name,
                            last_name=last_name,
                            birthday=birthday)
        resp = jsonify({"success": True})
        resp.status_code = 200
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def is_email_available(email):
    try:
        user = db.session.query(UserModel).filter(UserModel.email == email).first()
        if user is not None:
            resp = jsonify({"success": False})
        else:
            resp = jsonify({"success": True})
        resp.status_code = 200
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def promote_admin(user_id):
    try:
        user = db.session.query(UserModel).filter(UserModel.id == user_id).first()
        if user is not None:
            user.promote_admin()
            resp = SUCCESS()
        else:
            resp = FAILED("Utilisateur introuvable")
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp


def create_api_token(user):
    try:
        token = user.encode_api_token()
        resp = jsonify({
            "success": True,
            "apiToken": token
        })
        resp.status_code = 200
        logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                    request.method, request.host, request.path,
                    request.content_type, request.data, resp.status_code)
    except Exception as e:
        resp = FAILED(e)
        logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                       request.method, request.host, request.path,
                       request.content_type, request.data, resp.status_code, traceback_format_exc())
    return resp
