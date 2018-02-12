from flask import request
from flask.ext.jsonpify import jsonify
from models.User import User

def securedRoute(func):
    def func_wrapper(*args, **kwargs):
        content = request.get_json()
        jsonToken = content["token"]
        res, data = User.decodeAuthToken(jsonToken)
        if (res is True):
            kwargs['user'] = data
            return (func(*args, **kwargs))
        else:
            return (jsonify({"success": False, "message": data}))
    return func_wrapper

def checkContent(func):
    def func_wrapper(*args, **kwargs):
        content = request.get_json()
        if content is None:
            return (jsonify({"success": False, "message": "No json body found"}))
        else:
            kwargs['content'] = content
            return (func(*args, **kwargs))
    return func_wrapper