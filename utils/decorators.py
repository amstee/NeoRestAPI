from flask import request
from flask_jsonpify import jsonify
from models.User import User
from models.Device import Device
from .security import get_user_from_header, get_device_from_header
from .exceptions import InvalidAuthentication
from exceptions.content import JsonNotFound, JsonParameterFormatError, JsonParameterNotFound, JsonUnreadable
from exceptions.content import ContentException
from functools import wraps
from traceback import format_exc
import json


def secured_from_header(func):
    def func_wrapper(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            try:
                user = get_user_from_header(request)
                kwargs["client"] = user
                kwargs["is_device"] = False
                return func(*args, **kwargs)
            except InvalidAuthentication:
                try:
                    device = get_device_from_header(request)
                    kwargs["client"] = device
                    kwargs["is_device"] = True
                    return func(*args, **kwargs)
                except InvalidAuthentication as ie:
                    resp = jsonify({"success": False, "message": str(ie)})
                    resp.status_code = 500
                    return resp
        if token is None or token == "":
            if "neo_user_token" in request.cookies:
                token = request.headers.get("neo_user_token")
                res, data = User.decode_auth_token_old(token)
                if res is True:
                    kwargs['client'] = data
                    kwargs["is_device"] = False
                    return func(*args, **kwargs)
                else:
                    resp = jsonify({"success": False, "message": data})
                    resp.status_code = 401
                    return resp
            if "neo_device_token" in request.cookies:
                token = request.headers.get("neo_device_token")
                res, data = Device.decode_auth_token(token)
                if res is True:
                    kwargs['client'] = data
                    kwargs["is_device"] = True
                    return func(*args, **kwargs)
                else:
                    resp = jsonify({"success": False, "message": data})
                    resp.status_code = 401
                    return resp
        resp = jsonify({"success": False, "message": "Token introuvable"})
        return resp
    return func_wrapper


def secured_user_route(func):
    def func_wrapper(*args, **kwargs):
        try:
            content = request.get_json()
            if "token" in content and content["token"] != "" or "neo_user_token" in request.cookies:
                if "token" in content:
                    json_token = content["token"]
                else:
                    json_token = request.cookies.get("neo_user_token")
                res, data = User.decode_auth_token_old(json_token)
                if res is True:
                    kwargs['user'] = data
                    return func(*args, **kwargs)
                else:
                    resp = jsonify({"success": False, "message": data})
                    resp.status_code = 401
                    return resp
        except Exception as e:
            resp = jsonify({"success": False, "message": str(e)})
            resp.status_code = 500
            return resp
    return func_wrapper


def secured_device_route(func):
    def func_wrapper(*args, **kwargs):
        try:
            content = request.get_json()
            if "device_token" in content and content["device_token"] != "" or "neo_device_token" in request.cookies:
                if "device_token" in content:
                    json_token = content["device_token"]
                else:
                    json_token = request.cookies.get("neo_device_token")
                res, data = Device.decode_auth_token(json_token)
                if res is True:
                    kwargs['device'] = data
                    return func(*args, **kwargs)
                else:
                    resp = jsonify({"success": False, "message": data})
                    resp.status_code = 401
                    return resp
            else:
                resp = jsonify({"success": False, "message": "Aucun jwt trouvé dans le contenu de la requete"})
                return resp
        except Exception as e:
            resp = jsonify({"success": False, "message": str(e)})
            resp.status_code = 500
            return resp
    return func_wrapper


def secured_route(func):
    def func_wrapper(*args, **kwargs):
        try:
            content = request.get_json()
            if "token" in content and content["token"] != "" or "neo_user_token" in request.cookies:
                if "token" in content:
                    json_token = content["token"]
                else:
                    json_token = request.cookies.get("neo_user_token")
                res, data = User.decode_auth_token_old(json_token)
                if res is True:
                    kwargs['client'] = data
                    kwargs["is_device"] = False
                    return func(*args, **kwargs)
                else:
                    resp = jsonify({"success": False, "message": data})
                    resp.status_code = 401
                    return resp
            elif "device_token" in content and content["device_token"] != "" or "neo_device_token" in request.cookies:
                if "device_token" in content:
                    json_token = content["device_token"]
                else:
                    json_token = request.cookies.get("neo_device_token")
                res, data = Device.decode_auth_token(json_token)
                if res is True:
                    kwargs['client'] = data
                    kwargs["is_device"] = True
                    return func(*args, **kwargs)
                else:
                    resp = jsonify({"success": False, "message": data})
                    resp.status_code = 401
                    return resp
            else:
                resp = jsonify({"success": False, "message": "Aucun jwt trouvé dans le contenu de la requete"})
                return resp
        except Exception as e:
            resp = jsonify({"success": False, "message": str(e)})
            resp.status_code = 500
            return resp
    return func_wrapper


def secured_admin_route(func):
    def func_wrapper(*args, **kwargs):
        try:
            content = request.get_json()
            if "token" not in content and content["token"] == "":
                resp = jsonify({"success": False, "message": "Aucun jwt trouvé dans le contenu de la requete"})
                return resp
            json_token = content["token"]
            res, data = User.decode_auth_token_old(json_token)
            if res:
                if data.type == "ADMIN":
                    kwargs['admin'] = data
                    return func(*args, **kwargs)
                else:
                    resp = jsonify({"success": False,
                                    "message": "Les droits de cet utilisateur ne permettent pas d'appeller cette route"
                                    })
                    resp.status_code = 403
                    return resp
            else:
                resp = jsonify({"success": False, "message": data})
                resp.status_code = 401
                return resp
        except Exception as e:
            resp = jsonify({"success": False, "message": str(e)})
            resp.status_code = 500
            return resp
    return func_wrapper


def check_admin_route(func):
    def func_wrapper(*args, **kwargs):
        try:
            content = request.get_json()
            if "token" not in content and content["token"] == "":
                resp = jsonify({"success": False, "message": "Aucun jwt trouvé dans le contenu de la requete"})
                return resp
            json_token = content["token"]
            res, data = User.decode_auth_token_old(json_token)
            if res:
                if data.type == "ADMIN":
                    return func(*args, **kwargs)
                else:
                    resp = jsonify({"success": False,
                                    "message": "Les droits de cet utilisateur ne permettent pas d'appeller cette route"
                                    })
                    resp.status_code = 403
                    return resp
            else:
                resp = jsonify({"success": False, "message": data})
                resp.status_code = 401
                return resp
        except Exception as e:
            resp = jsonify({"success": False, "message": str(e)})
            resp.status_code = 500
            return resp
    return func_wrapper


def check_content_old(func):
    def func_wrapper(*args, **kwargs):
        try:
            content = request.get_json()
            if content is None:
                resp = jsonify({"success": False, "message": "Pas de JSON body dans la requete"})
                resp.status_code = 405
                return resp
            else:
                kwargs['content'] = content
                return func(*args, **kwargs)
        except Exception as e:
            resp = jsonify({"success": False, "message": str(e)})
            resp.status_code = 500
            return resp
    return func_wrapper


def parametrized(dec):
    def layer(*args, **kwargs):
        def repl(f):
            return dec(f, *args, **kwargs)
        return repl
    return layer


@parametrized
def route_log(f, logger):
    @wraps(f)
    def wrapped(*args, **kwargs):
        try:
            response = f(*args, **kwargs)
            logger.info("[%s] [%s] [%s] [%s] [%s] [%d]",
                        request.method, request.host, request.path,
                        request.content_type, request.data, response.status_code)
        except Exception:
            response = jsonify({"success": False})
            response.status_code = 500
            logger.warning("[%s] [%s] [%s] [%s] [%s] [%d]\n%s",
                           request.method, request.host, request.path,
                           request.content_type, request.data, response.status_code, format_exc())
        return response
    return wrapped


@parametrized
def check_content(func, *definer):
    def func_wrapper(*args, **kwargs):
        try:
            content = json.loads(request.data)
            if content is None:
                raise JsonNotFound
            for elem in definer:
                if elem[2] and elem[0] not in content:
                    raise JsonParameterNotFound(elem[0])
                if elem[0] in content and type(content[elem[0]]) is not type(elem[1]):
                    raise JsonParameterFormatError(elem[0], type(elem[1]))
            kwargs['content'] = content
            return func(*args, **kwargs)
        except ContentException:
            response = jsonify({"success": False, "message": ContentException.message})
            response.status_code = ContentException.status_code
            return response
        except json.decoder.JSONDecodeError:
            response = jsonify({"success": False, "message": JsonUnreadable.message})
            response.status_code = JsonUnreadable.status_code
            return response
    return func_wrapper
