import uuid
from datetime import datetime, timedelta
from fastapi import FastAPI, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db import get_db
from .models import Job
from .schemas import SubmitRequest, SubmitResponse, StatusResponse
from .queue import queue, redis_conn

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title='Queue LB API')
app.state.limiter = limiter
app.add_exception_handler(Exception, limiter._rate_limit_exceeded_handler)
Instrumentator().instrument(app).expose(app)


@app.post('/submit', response_model=SubmitResponse)
@limiter.limit(settings.rate_limit)
async def submit_job(request: Request, body: SubmitRequest, db: AsyncSession = Depends(get_db)):
    idem = request.headers.get('Idempotency-Key')
    if idem:
        existing = await db.scalar(select(Job).where(Job.idempotency_key == idem))
        if existing:
            return SubmitResponse(job_id=existing.job_id, status=existing.status)

    job_id = str(uuid.uuid4())
    job = Job(job_id=job_id, status='queued', created_at=datetime.utcnow(), idempotency_key=idem)
    db.add(job)
    await db.commit()
    queue.enqueue('worker_app.tasks.process_job', job_id, body.payload, retry=3)
    return SubmitResponse(job_id=job_id, status='queued')


@app.get('/status/{job_id}', response_model=StatusResponse)
async def get_status(job_id: str, db: AsyncSession = Depends(get_db)):
    job = await db.get(Job, job_id)
    if not job:
        raise HTTPException(404, 'Job not found')
    return StatusResponse(job_id=job.job_id, status=job.status, worker=job.assigned_worker, result=job.result)


@app.get('/workers')
async def workers():
    keys = redis_conn.keys('worker:*')
    out = []
    now = datetime.utcnow()
    for key in keys:
        raw = redis_conn.hgetall(key)
        if not raw:
            continue
        last = datetime.fromisoformat(raw[b'last_heartbeat'].decode())
        status = 'alive' if now - last < timedelta(seconds=settings.worker_timeout_seconds) else 'down'
        out.append({
            'worker_id': raw[b'worker_id'].decode(),
            'ip_address': raw[b'ip_address'].decode(),
            'current_load': int(raw[b'current_load']),
            'max_capacity': int(raw[b'max_capacity']),
            'last_heartbeat': raw[b'last_heartbeat'].decode(),
            'status': status,
        })
    return out


@app.get('/metrics-summary')
async def metrics_summary(db: AsyncSession = Depends(get_db)):
    total = await db.scalar(select(func.count()).select_from(Job)) or 0
    grouped = (await db.execute(select(Job.status, func.count()).group_by(Job.status))).all()
    qsize = queue.count
    avg_secs = await db.scalar(select(func.avg(func.extract('epoch', Job.completed_at - Job.started_at))).where(Job.completed_at.is_not(None)))
    return {
        'total_jobs': total,
        'jobs_by_status': {k: v for k, v in grouped},
        'queue_size': qsize,
        'avg_processing_time_seconds': float(avg_secs or 0),
    }
