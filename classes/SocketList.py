from classes.SocketUser import SocketUser
from classes.StoreWrapper import StoreWrapper


class SocketList:
    storage = StoreWrapper()

    def __init__(self):
        pass

    def new_client(self, sid):
        return SocketUser(sid)

    def save_client(self, client):
        self.storage.save_client(client)

    def find_socket(self, sid):
        return self.storage.find_sid(sid)

    def remove(self, sid):
        return self.storage.remove_sid(sid)

    def find_user(self, client, is_device=False):
        return self.storage.get(client.id, is_device)

    def notify_user(self, client, is_device, p1, p2, namespace='/'):
        if client is None or not client.is_online:
            return False
        socket = self.find_user(client, is_device)
        if socket is not None:
            socket.emit(p1, p2, namespace=namespace)
            return True
        return False

    def __len__(self):
        return len(self.storage)
