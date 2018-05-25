from flask_socketio import Namespace
from flask import request


class ChannelHandler(Namespace):
    users = []

    def on_connect(self):
        self.users.append(request.sid)

    def on_disconnect(self):
        self.users.remove(request.sid)

    def find_user(self, sid):
        try:
            index = self.users.index(sid)
            return self.users[index]
        except ValueError:
            return None
