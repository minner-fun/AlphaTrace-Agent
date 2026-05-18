from sqlalchemy.orm import Session

from app.agent.report_generator import generate_report
from app.agent.task_parser import parse_task
from app.analysis.token_flow import analyze_token_flow_task
from app.analysis.wallet_analysis import analyze_wallet_task
from app.chain.erc8183_client import ERC8183Client
from app.config import get_settings
from app.models.job import AgentJob
from app.storage.hash import hash_report
from app.storage.report_store import save_report


async def run_alpha_trace_job(db: Session, chain_job_id: str):
    job = db.query(AgentJob).filter(AgentJob.chain_job_id == chain_job_id).one_or_none()
    if job is None:
        raise ValueError(f"Job {chain_job_id} was not synced to the local database")

    task = parse_task(job.description)
    if task.task_type == "token_flow_analysis":
        raw_data = await analyze_token_flow_task(task)
    elif task.task_type == "wallet_analysis":
        raw_data = await analyze_wallet_task(task)
    else:
        raw_data = {
            "observations": [
                {
                    "type": "market_research",
                    "title": "Generic research task",
                    "description": "MVP fallback report generated without external data sources.",
                    "source": "mock_agent",
                    "severity": "low",
                }
            ],
            "metrics": {},
            "labels": {"market_signal": "Research"},
        }

    report_json = await generate_report(job, task, raw_data)
    report_hash = hash_report(report_json)
    submit_tx_hash = ERC8183Client(get_settings()).submit_deliverable(chain_job_id, report_hash)
    report = save_report(db, chain_job_id, report_json, report_hash, submit_tx_hash)

    job.status = "submitted"
    db.commit()
    db.refresh(job)

    return {
        "chain_job_id": chain_job_id,
        "status": job.status,
        "report_hash": report_hash,
        "report_id": report.id,
        "submit_tx_hash": submit_tx_hash,
    }

