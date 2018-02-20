from flask.ext.jsonpify import jsonify

def SUCCESS():
    resp = jsonify({"success": True})
    resp.status_code = 200
    return resp

def FAILED(error):
    resp = jsonify({"success": False, "message": str(error)})
    resp.status_code = 400
    return resp