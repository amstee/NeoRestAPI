from classes.SocketUser import SocketUser


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

    def __len__(self):
        return len(self.socket_dic)