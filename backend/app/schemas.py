from typing import Any

from pydantic import BaseModel, Field


class JobSyncRequest(BaseModel):
    chain_job_id: str
    client_address: str
    provider_address: str
    evaluator_address: str | None = None
    description: str
    budget: str | None = None
    tx_hash: str | None = None


class JobResponse(BaseModel):
    chain_job_id: str
    client_address: str
    provider_address: str
    evaluator_address: str | None = None
    description: str
    status: str
    budget: str | None = None
    tx_hash: str | None = None
    report_hash: str | None = None
    submit_tx_hash: str | None = None


class RunJobResponse(BaseModel):
    chain_job_id: str
    status: str
    report_hash: str
    report_id: int
    submit_tx_hash: str | None = None


class ReportResponse(BaseModel):
    chain_job_id: str
    report: dict[str, Any]
    report_hash: str
    verified: bool
    submit_tx_hash: str | None = None


class FeedbackRequest(BaseModel):
    user_address: str
    score: int = Field(ge=0, le=100)
    comment: str | None = None


class FeedbackResponse(BaseModel):
    chain_job_id: str
    score: int
    reputation_tx_hash: str | None = None

