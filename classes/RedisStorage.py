import redis


class RedisStorage:
    def __init__(self, url):
        RedisStorage.clean_databases(url)
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
            cont = {}
            for k, v in res.items():
                cont[k.decode("utf-8")] = v.decode("utf-8")
            return cont
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
        value = self.client.get(key)
        if value:
            self.client.delete(key)
        self.client.hmset(key, payload)
        value = self.client_sid.get(payload["sid"])
        if value:
            self.client_sid.delete(payload["sid"])
        self.client_sid.set(payload["sid"], key)

    def exist(self, key, db=0):
        return self.get(key, None, db) is not None

    def find_sid(self, sid):
        key = self.client_sid.get(sid)
        if key:
            key = key.decode("utf-8")
            res = self.client.hgetall(key)
            if res:
                cont = {}
                for k, v in res.items():
                    cont[k.decode("utf-8")] = v.decode("utf-8")
                return key, cont
        return None, None

    @staticmethod
    def clean_databases(url):
        db = redis.from_url(url)
        db1 = redis.from_url(url, db=1)
        for key in db.scan_iter():
            db.delete(key)
        for key in db1.scan_iter():
            db1.delete(key)
        return True

    def __len__(self):
        c = 0
        for _ in self.client.scan_iter():
            c += 1
        return c
