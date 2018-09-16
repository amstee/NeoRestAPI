class DefaultStorage:
    store = {}

    def save(self, key, value):
        self.store.update({key: value})

    def get(self, key, default=None):
        return self.store.get(key, default)

    def pop(self, key, default=None):
        return self.store.pop(key, default)

    def exist(self, key):
        return key in self.store

    def find_sid(self, sid):
        for k, v in self.store.items():
            if v.sid == sid:
                return k, v
        return None, None

    def __len__(self):
        return len(self.store)
