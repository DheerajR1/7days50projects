from redis import Redis
from rq import Queue
from .config import settings

redis_conn = Redis.from_url(settings.redis_url)
queue = Queue(settings.queue_name, connection=redis_conn, default_timeout=120)
