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
            return True
        return False

    def find_user(self, user):
        try:
            if 'socket' in session and session['socket'] is not None:
                socket = session['socket']
                if socket.sid in self.socket_dic:
                    return socket
                else:
                    session.pop('socket')
                    if 'sid' in session:
                        session.pop('sid')
                    return None
            for key, value in self.socket_dic.items():
                if value.user.id == user.id:
                    session['socket'] = value
                    session['sid'] = key
                    return value
            return None
        except Exception:
            return None

    def notify_user(self, user, p1, p2, namespace='/'):
        if not user.is_online:
            return False
        socket = self.find_user(user)
        if socket is not None:
            socket.emit(p1, p2, namespace)
            return True
        return False

    def __len__(self):
        return len(self.socket_dic)