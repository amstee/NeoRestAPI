from classes.DefaultStorage import DefaultStorage
from classes.RedisStorage import RedisStorage
from classes.SocketUser import SocketUser


class StoreWrapper:
    store = DefaultStorage()
    is_redis = False

    def set_conf(self, use_redis, url):
        if use_redis:
            self.store = RedisStorage(url)
        self.is_redis = use_redis

    @staticmethod
    def deconstruct_key(key):
        is_device = True if key[:1] == "d" else False
        client_id = key[1:]
        return client_id, is_device

    def get(self, client_id, is_device=False, default=None):
        key = ("d" if is_device else "u") + str(client_id)
        data = self.store.get(key, default)
        if not self.is_redis:
            return data
        return SocketUser.construct_client(client_id, is_device, data)

    def pop(self, client_id, is_device=False, default=None):
        key = ("d" if is_device else "u") + str(client_id)
        data = self.store.pop(key, default)
        if not self.is_redis:
            return data
        return SocketUser.construct_client(client_id, is_device, data)

    def save(self, key, payload):
        return self.store.save(key, payload)

    def exist(self, key):
        return self.store.exist(key)

    def save_client(self, client):
        key = client.get_key()
        if key is None:
            return False
        if self.is_redis:
            value = client.get_payload()
            self.store.save(key, value)
        else:
            self.store.save(key, client)

    def find_sid(self, sid):
        key, data = self.store.find_sid(sid)
        if key is None or data is None:
            return None
        if self.is_redis:
            client_id, is_device = StoreWrapper.deconstruct_key(key)
            return SocketUser.construct_client(client_id, is_device, data)
        return data

    def remove_sid(self, sid):
        key, data = self.store.find_sid(sid)
        if key is None or data is None:
            return False
        if self.is_redis:
            self.store.pop(sid, None, 1)
        return self.store.pop(key) is not None

    def __len__(self):
        return len(self.store)
