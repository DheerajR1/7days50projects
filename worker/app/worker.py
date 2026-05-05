import os
import signal
import threading
from redis import Redis
from rq import Queue, Worker
from .config import settings
from .heartbeat import run_heartbeat


def main():
    redis_conn = Redis.from_url(settings.redis_url)
    queue = Queue(settings.queue_name, connection=redis_conn)
    stop_event = threading.Event()
    current_load = {'n': 0}

    def load_getter():
        return current_load['n']

    hb_thread = threading.Thread(target=run_heartbeat, args=(stop_event, load_getter), daemon=True)
    hb_thread.start()

    worker = Worker([queue], connection=redis_conn, name=settings.worker_id)

    def shutdown(*_):
        stop_event.set()
        os._exit(0)

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    worker.work(with_scheduler=True)


if __name__ == '__main__':
    main()
