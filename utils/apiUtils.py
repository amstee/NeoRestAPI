from flask_jsonpify import jsonify


def SUCCESS():
    resp = jsonify({"success": True})
    resp.status_code = 200
    return resp


def FAILED(error, error_code=400):
    resp = jsonify({"success": False, "message": str(error)})
    resp.status_code = error_code
    return resp
