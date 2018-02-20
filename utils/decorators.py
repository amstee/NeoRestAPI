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
        except Exception as e:
            resp = jsonify({"success": False, "message": str(e)})
            resp.status_code = 500
    return func_wrapper

def checkContent(func):
    def func_wrapper(*args, **kwargs):
        try:
            content = request.get_json()
            if content is None:
                resp = jsonify({"success": False, "message": "No json body found"})
                resp.status_code = 405
            else:
                kwargs['content'] = content
                return (func(*args, **kwargs))
        except Exception as e:
            resp = jsonify({"success": False, "message": str(e)})
            resp.status_code = 500
            return resp
    return func_wrapper