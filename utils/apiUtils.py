from flask.ext.jsonpify import jsonify

def SUCCESS():
    return (jsonify({"success": True}))

def FAILED(error):
    return (jsonify({"success": False, "message": str(error)}))