import redis


class State:
    def __init__(self, redis_host="localhost", redis_port=6379, redis_db=0):
        self.cache = {}
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

    def __getitem__(self, key):
        if key in self.cache:
            return self.cache[key]
        else:
            value = self.redis_client.get(key)
            if value:
                self.cache[key] = value
                self.cache[key] = self.cache[key].decode("utf-8")
            return self.cache.get(key)

    def __setitem__(self, key, value):
        self.cache[key] = value
        self.redis_client.set(key, value)

    def get(self, key, default=None):
        return self.cache.get(key, default)
