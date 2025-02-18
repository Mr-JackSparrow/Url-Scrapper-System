from upstash_redis import Redis

redis = Redis(url="https://intimate-lacewing-16779.upstash.io", token="AUGLAAIjcDFiMzU1YjgyNWQ4Yjk0ZjhhYjUxZDlhZTRlYmQyMTI3NXAxMA")

redis.set("foo", "bar")
value = redis.get("foo")

print(value)