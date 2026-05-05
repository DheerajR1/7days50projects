import threading
import time
from datetime import datetime
from redis import Redis
from .config import settings


redis_conn = Redis.from_url(settings.redis_url)


def run_heartbeat(stop_event: threading.Event, load_getter):
    key = f'worker:{settings.worker_id}'
    while not stop_event.is_set():
        redis_conn.hset(key, mapping={
            'worker_id': settings.worker_id,
            'ip_address': settings.worker_ip,
            'current_load': load_getter(),
            'max_capacity': settings.max_capacity,
            'last_heartbeat': datetime.utcnow().isoformat(),
        })
        time.sleep(3)
