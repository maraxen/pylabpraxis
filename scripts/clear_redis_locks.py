import redis

r = redis.Redis(host="localhost", port=6379, db=0)

keys = []
for key in r.scan_iter("lock:asset:*"):
    keys.append(key)
for key in r.scan_iter("asset:*"):
    keys.append(key)

if keys:
    r.delete(*keys)
else:
    pass
