from flask import request
from flask_jsonpify import jsonify
from models.User import User
from models.Device import Device

def securedRoute(func):
    def func_wrapper(*args, **kwargs):
        try:
            content = request.get_json()
            if "token" not in content or content["token"] == "":
                resp = jsonify({"success": False, "message": "Aucun jwt trouvé dans le contenu de la requete"})
                return resp
            jsonToken = content["token"]
            res, data = User.decodeAuthToken(jsonToken)
            if (res is True):
                kwargs['user'] = data
                return (func(*args, **kwargs))
            else:
                resp = jsonify({"success": False, "message": data})
                resp.status_code = 401
                return resp
        except Exception as e:
            resp = jsonify({"success": False, "message": str(e)})
            resp.status_code = 500
            return resp
    return func_wrapper

def securedDeviceRoute(func):
    def func_wrapper(*args, **kwargs):
        try:
            content = request.get_json()
            if "device_token" not in content or content["device_token"] == "":
                resp = jsonify({"success": False, "message": "Aucun jwt trouvé dans le contenu de la requete"})
                return resp
            jsonToken = content["device_token"]
            res, data = Device.decodeAuthToken(jsonToken)
            if res is True:
                kwargs['device'] = data
                return func(*args, **kwargs)
            else:
                resp = jsonify({"success": False, "message": data})
                resp .status_code = 401
                return resp
        except Exception as e:
            resp = jsonify({"success": False, "message": str(e)})
            resp.status_code = 500
            return resp
    return func_wrapper

def securedAdminRoute(func):
    def func_wrapper(*args, **kwargs):
        try:
            content = request.get_json()
            if "token" not in content and content["token"] == "":
                resp = jsonify({"success": False, "message": "Aucun jwt trouvé dans le contenu de la requete"})
                return resp
            jsonToken = content["token"]
            res, data = User.decodeAuthToken(jsonToken)
            if (res is True):
                if data.type == "ADMIN":
                    kwargs['admin'] = data
                    return (func(*args, **kwargs))
                else:
                    resp = jsonify({"success": False, "message": "Les droits de cet utilisateur ne permettent pas d'appeller cette route"})
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

def checkContent(func):
    def func_wrapper(*args, **kwargs):
        try:
            content = request.get_json()
            if content is None:
                resp = jsonify({"success": False, "message": "Pas de JSON body dans la requete"})
                resp.status_code = 405
                return resp
            else:
                kwargs['content'] = content
                return (func(*args, **kwargs))
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
