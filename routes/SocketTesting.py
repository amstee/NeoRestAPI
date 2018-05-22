from flask_restful import Resource
from flask import send_file

class SocketTest(Resource):
    def get(self):
        return send_file("test/socket.html")
