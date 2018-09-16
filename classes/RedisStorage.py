import redis


class RedisStorage:
    def __init__(self, url):
        self.url = url
        self.client = redis.from_url(self.url)
        self.client_sid = redis.from_url(self.url, db=1)

    def get(self, key, default=None, db=0):
        if db == 0:
            res = self.client.hgetall(key)
        else:
            res = self.client_sid.get(key)
        if res:
            if db == 1:
                return res.decode("utf-8")
            dict = {}
            for k, v in res.items():
                dict[k.decode("utf-8")] = v.decode("utf-8")
            return dict
        return default

    def pop(self, key, default=None, db=0):
        res = self.get(key, default, db)
        if res:
            if db == 1:
                self.client_sid.delete(key)
            else:
                self.client.delete(key)
        return res

    def set(self, key, value, db=0):
        if db == 0:
            self.client.set(key, value)
        else:
            self.client_sid.set(key, value)

    def save(self, key, payload):
        self.client.hmset(key, payload)
        self.client_sid.set(payload["sid"], key)

    def exist(self, key):
        return self.get(key, None) is not None

    def find_sid(self, sid):
        key = self.client_sid.get(sid)
        if key:
            key = key.decode("utf-8")
            res = self.client.hgetall(key)
            if res:
                dict = {}
                for k, v in res.items():
                    dict[k.decode("utf-8")] = v.decode("utf-8")
                return key, dict
        return None, None

    def __len__(self):
        return 0
