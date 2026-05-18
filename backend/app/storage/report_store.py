import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.report import Report


def save_report(
    db: Session,
    chain_job_id: str,
    report_json: dict[str, Any],
    report_hash: str,
    submit_tx_hash: str | None = None,
) -> Report:
    scores = report_json.get("scores", {})
    existing = db.query(Report).filter(Report.chain_job_id == chain_job_id).one_or_none()
    payload = json.dumps(report_json, ensure_ascii=False)

    if existing:
        existing.report_json = payload
        existing.report_hash = report_hash
        existing.submit_tx_hash = submit_tx_hash
        existing.summary = report_json.get("summary")
        existing.confidence = scores.get("confidence")
        existing.risk_score = scores.get("risk_score")
        db.commit()
        db.refresh(existing)
        return existing

    report = Report(
        chain_job_id=chain_job_id,
        report_json=payload,
        report_hash=report_hash,
        submit_tx_hash=submit_tx_hash,
        summary=report_json.get("summary"),
        confidence=scores.get("confidence"),
        risk_score=scores.get("risk_score"),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def load_report_json(report: Report) -> dict[str, Any]:
    return json.loads(report.report_json)

