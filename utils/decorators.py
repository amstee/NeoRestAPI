from flask import request
from flask.ext.jsonpify import jsonify
from models.User import User

def securedRoute(func):
    def func_wrapper(*args, **kwargs):
        try:
            content = request.get_json()
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
