from flask_restful import Resource, Api
from utils.decorators import checkContent
from utils.decorators import securedRoute
from models.Device import Device
from flask.ext.jsonpify import jsonify

class DeviceAdd(Resource):
    @checkContent
    @securedRoute
    def post(self, content, user):
        try:
            new_device = Device()
            resp = jsonify({"success": True})
        except Exception as e:
            resp = jsonify({"success": False, "message": str(e)})
        return resp
#
# from routes.utils import *
#
# db_connect = create_engine('sqlite:///database.sqlt')
#
# class AccountDeviceAdd(Resource):
#     def post(self):
#         content = request.get_json()
#         if verify_webtoken(content) == False:
#             resp = jsonify({"success" : False, "error" : "Wrong token or username"})
#         elif 'mid' not in content:
#             resp = jsonify({"success" : False, "error" : "missing machine id"})
#         else:
#             conn = db_connect.connect()
#             query = conn.execute("SELECT * FROM user WHERE email = ?", content['username'])
#             userInfo = {}
#             for elem in query.cursor.fetchall():
#                 userInfo = {"id" : elem[0], "email" : elem[1], "fname" : elem[3], "lname" : elem[4], "birthday" : elem[5]}
#             conn.execute("INSERT INTO device (userid, mid) VALUES (?, ?)", userInfo['id'], content['mid'])
#             resp = jsonify({"success" : True})
#         return resp
#
# class AccountDeviceList(Resource):
#     def post(self):
#         content = request.get_json()
#         if verify_webtoken(content) == False:
#             resp = jsonify({"success" : False, "error" : "Wrong token or username"})
#         else:
#             conn = db_connect.connect()
#             query = conn.execute("SELECT * FROM user WHERE email = ?", content['username'])
#             userInfo = {}
#             for elem in query.cursor.fetchall():
#                 userInfo = {"id" : elem[0], "email" : elem[1], "fname" : elem[3], "lname" : elem[4], "birthday" : elem[5]}
#             query = conn.execute("SELECT * FROM device WHERE userid = ?", userInfo['id'])
#             result = []
#             for elem in query.cursor.fetchall():
#                 result.append({"id" : elem[0], "userid" : elem[1], "mid" : elem[2]})
#             resp = jsonify(result)
#         return resp
