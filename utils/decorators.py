from flask import request
from flask_jsonpify import jsonify
from models.User import User
from models.Device import Device
from .security import get_user_from_header, get_device_from_header
from .exceptions import InvalidAuthentication


def secured_from_header(func):
    def func_wrapper(*args, **kwargs):
        token = None
        if "Authorization" in request.headers:
            try:
                user = get_user_from_header(request)
                kwargs["user"] = user
                return func(*args, **kwargs)
            except InvalidAuthentication:
                try:
                    device = get_device_from_header(request)
                    kwargs["device"] = device
                    return func(*args, **kwargs)
                except InvalidAuthentication as ie:
                    resp = jsonify({"success": False, "message": str(ie)})
                    resp.status_code = 500
                    return resp
        if token is None or token == "":
            if "neo_user_token" in request.cookies:
                token = request.headers.get("neo_user_token")
                res, data = User.decode_auth_token(token)
                if res is True:
                    kwargs['user'] = data
                    return func(*args, **kwargs)
                else:
                    resp = jsonify({"success": False, "message": data})
                    resp.status_code = 401
                    return resp
            if "neo_device_token" in request.cookies:
                token = request.headers.get("neo_device_token")
                res, data = Device.decode_auth_token(token)
                if res is True:
                    kwargs['device'] = data
                    return func(*args, **kwargs)
                else:
                    resp = jsonify({"success": False, "message": data})
                    resp.status_code = 401
                    return resp
        resp = jsonify({"success": False, "message": "Token introuvable"})
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
                res, data = User.decode_auth_token(json_token)
                if res is True:
                    kwargs['user'] = data
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


def secured_admin_route(func):
    def func_wrapper(*args, **kwargs):
        try:
            content = request.get_json()
            if "token" not in content and content["token"] == "":
                resp = jsonify({"success": False, "message": "Aucun jwt trouvé dans le contenu de la requete"})
                return resp
            json_token = content["token"]
            res, data = User.decode_auth_token(json_token)
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


def check_content(func):
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

# def getContent(func):
#     def func_wrapper(*args, **kwargs):
#         try:
#             content = request.get_json()
#             if content is None:
#                 resp = jsonify({"success": False, "message": "Pas de JSON body dans la requete"})
#                 resp.status_code = 405
#                 return resp
#             else:
#                 print(kwargs)
#                 kwargs['content'] = content
#                 return (func(*args, **kwargs))
#         except Exception as e:
#             resp = jsonify({"success": False, "message": str(e)})
#             resp.status_code = 500
#             return resp
#     return func_wrapper
