from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agent.worker import run_alpha_trace_job
from app.chain.erc8004_client import ERC8004Client
from app.config import get_settings
from app.database import get_db
from app.models.feedback import Feedback
from app.models.job import AgentJob
from app.models.report import Report
from app.schemas import FeedbackRequest, FeedbackResponse, JobActionResponse, JobResponse, JobSyncRequest, RunJobResponse

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


def serialize_job(job: AgentJob, report: Report | None = None) -> JobResponse:
    return JobResponse(
        chain_job_id=job.chain_job_id,
        client_address=job.client_address,
        provider_address=job.provider_address,
        evaluator_address=job.evaluator_address,
        description=job.description,
        status=job.status,
        budget=job.budget,
        tx_hash=job.tx_hash,
        report_hash=report.report_hash if report else None,
        submit_tx_hash=report.submit_tx_hash if report else None,
    )


@router.post("/sync", response_model=JobResponse)
def sync_job(payload: JobSyncRequest, db: Session = Depends(get_db)):
    job = db.query(AgentJob).filter(AgentJob.chain_job_id == payload.chain_job_id).one_or_none()
    if job:
        job.client_address = payload.client_address
        job.provider_address = payload.provider_address
        job.evaluator_address = payload.evaluator_address
        job.description = payload.description
        job.budget = payload.budget
        job.tx_hash = payload.tx_hash
    else:
        job = AgentJob(
            chain_job_id=payload.chain_job_id,
            client_address=payload.client_address,
            provider_address=payload.provider_address,
            evaluator_address=payload.evaluator_address,
            description=payload.description,
            status="open",
            budget=payload.budget,
            tx_hash=payload.tx_hash,
        )
        db.add(job)

    db.commit()
    db.refresh(job)
    return serialize_job(job)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(AgentJob).filter(AgentJob.chain_job_id == job_id).one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    report = db.query(Report).filter(Report.chain_job_id == job_id).one_or_none()
    return serialize_job(job, report)


@router.post("/{job_id}/run", response_model=RunJobResponse)
async def run_job(job_id: str, db: Session = Depends(get_db)):
    try:
        return await run_alpha_trace_job(db, job_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.post("/{job_id}/fund", response_model=JobActionResponse)
def fund_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(AgentJob).filter(AgentJob.chain_job_id == job_id).one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status in {"submitted", "completed"}:
        raise HTTPException(status_code=409, detail=f"Cannot fund a {job.status} job")

    job.status = "funded"
    db.commit()
    return JobActionResponse(
        chain_job_id=job_id,
        status=job.status,
        tx_hash=f"mock-fund-{job_id}",
    )


@router.post("/{job_id}/complete", response_model=JobActionResponse)
def complete_job(job_id: str, db: Session = Depends(get_db)):
    job = db.query(AgentJob).filter(AgentJob.chain_job_id == job_id).one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    report = db.query(Report).filter(Report.chain_job_id == job_id).one_or_none()
    if report is None or job.status != "submitted":
        raise HTTPException(status_code=409, detail="Job must have a submitted report before completion")

    job.status = "completed"
    db.commit()
    return JobActionResponse(
        chain_job_id=job_id,
        status=job.status,
        tx_hash=f"mock-complete-{job_id}",
    )


@router.post("/{job_id}/feedback", response_model=FeedbackResponse)
def submit_feedback(job_id: str, payload: FeedbackRequest, db: Session = Depends(get_db)):
    job = db.query(AgentJob).filter(AgentJob.chain_job_id == job_id).one_or_none()
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    reputation_tx_hash = ERC8004Client(get_settings()).record_feedback(
        chain_job_id=job_id,
        user_address=payload.user_address,
        score=payload.score,
        comment=payload.comment,
    )
    feedback = Feedback(
        chain_job_id=job_id,
        user_address=payload.user_address,
        score=payload.score,
        comment=payload.comment,
        reputation_tx_hash=reputation_tx_hash,
    )
    db.add(feedback)
    db.commit()

    return FeedbackResponse(
        chain_job_id=job_id,
        score=payload.score,
        reputation_tx_hash=reputation_tx_hash,
    )
