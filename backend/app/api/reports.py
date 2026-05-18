from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.report import Report
from app.schemas import ReportResponse
from app.storage.hash import verify_report_hash
from app.storage.report_store import load_report_json

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/{job_id}", response_model=ReportResponse)
def get_report(job_id: str, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.chain_job_id == job_id).one_or_none()
    if report is None:
        raise HTTPException(status_code=404, detail="Report not found")

    report_json = load_report_json(report)
    return ReportResponse(
        chain_job_id=job_id,
        report=report_json,
        report_hash=report.report_hash,
        verified=verify_report_hash(report_json, report.report_hash),
        submit_tx_hash=report.submit_tx_hash,
    )

