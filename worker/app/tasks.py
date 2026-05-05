import time
from datetime import datetime
from rq import get_current_job
from redis import Redis
from .config import settings
from .db import SessionLocal

redis_conn = Redis.from_url(settings.redis_url)


def process_job(job_id: str, payload: dict):
    job = get_current_job()
    retries = job.meta.get('retry_count', 0) if job else 0
    with SessionLocal() as db:
        rec = db.execute(f"SELECT * FROM jobs WHERE job_id='{job_id}'").mappings().first()
        if not rec:
            return
        db.execute(f"UPDATE jobs SET status='running', assigned_worker='{settings.worker_id}', started_at=NOW(), retry_count={retries} WHERE job_id='{job_id}'")
        db.commit()
    try:
        time.sleep(min(int(payload.get('duration', 2)), 10))
        result = {'ok': True, 'echo': payload}
        with SessionLocal() as db:
            db.execute(f"UPDATE jobs SET status='success', completed_at=NOW(), result='{result}'::json WHERE job_id='{job_id}'")
            db.commit()
    except Exception as e:
        retries += 1
        with SessionLocal() as db:
            status = 'failed' if retries >= 3 else 'queued'
            db.execute(f"UPDATE jobs SET status='{status}', retry_count={retries}, result='{{\"error\": \"{str(e)}\"}}'::json WHERE job_id='{job_id}'")
            db.commit()
        if retries < 3:
            backoff = 2 ** retries
            time.sleep(backoff)
            raise
