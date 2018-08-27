from classes.SocketUser import SocketUser
from flask import session


class SocketList:
    socket_dic = {}

    def __init__(self):
        pass

    def __str__(self):
        return "<(SocketList='%s')>" % (str(self.socket_dic))

    def add(self, sid):
        self.socket_dic.update({sid: SocketUser(sid)})

    def find_socket(self, sid):
        return self.socket_dic.get(sid, None)

    def remove(self, sid):
        if sid in self.socket_dic:
            self.socket_dic.pop(sid)
            if session.get("socket") is True:
                session.pop("socket")
            if session.get("sid") is True:
                session.pop("sid")
            return True
        return False

    def find_user(self, client, is_device=False):
        try:
            if client is None:
                return False
            if 'sid' in session and session['sid'] is not None:
                socket = self.find_socket(session['sid'])
                if socket is not None and socket.client_id == client.id and socket.is_device == is_device:
                    return socket
            for key, value in self.socket_dic.items():
                if value is not None:
                    if value.client_id == client.id and value.is_device == is_device:
                        return value
            return None
        except Exception as e:
            print(e)
            return None

    def notify_user(self, client, is_device, p1, p2, namespace='/'):
        if client is None or not client.is_online:
            return False
        socket = self.find_user(client, is_device)
        if socket is not None:
            socket.emit(p1, p2, namespace=namespace)
            return True
        return False

    def __len__(self):
        return len(self.socket_dic)
