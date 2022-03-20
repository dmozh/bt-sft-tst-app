import redis

from settings import settings

r = redis.Redis(settings.redis_host, db=0)

