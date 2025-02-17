import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# Test the connection
print(r.ping())