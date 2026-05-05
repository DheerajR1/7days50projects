from pydantic import BaseModel
from typing import Any


class SubmitRequest(BaseModel):
    payload: dict[str, Any]


class SubmitResponse(BaseModel):
    job_id: str
    status: str


class StatusResponse(BaseModel):
    job_id: str
    status: str
    worker: str | None
    result: dict | None
