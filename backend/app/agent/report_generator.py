from datetime import UTC, datetime
from typing import Any

from app.agent.task_parser import ParsedTask
from app.analysis.risk_analysis import score_risk
from app.models.job import AgentJob


async def generate_report(job: AgentJob, task: ParsedTask, raw_data: dict[str, Any]) -> dict[str, Any]:
    labels = raw_data.get("labels", {})
    metrics = raw_data.get("metrics", {})
    observations = raw_data.get("observations", [])
    scores = score_risk(raw_data)

    target = task.target or raw_data.get("token") or raw_data.get("wallet") or "unknown"
    summary = (
        f"{target} shows elevated token-flow and custody risk signals, including "
        f"{metrics.get('top_10_holder_share', 'unknown')}% top-holder concentration "
        f"and {metrics.get('multisig_controlled_supply', 'unknown')}% multisig-linked supply."
        if task.task_type == "token_flow_analysis"
        else "AlphaTrace generated an MVP market intelligence report from available mock signals."
    )

    return {
        "job_id": job.chain_job_id,
        "agent": {
            "name": "AlphaTrace Agent",
            "type": "market_intelligence",
            "version": "0.1.0",
        },
        "task": {
            "raw_description": task.raw_description,
            "task_type": task.task_type,
            "target": target,
        },
        "summary": summary,
        "evidence": observations,
        "analysis": {
            "token_flow": "Distribution wallet -> bridge-linked address -> multisig or treasury wallet.",
            "holder_concentration": labels.get("holder_concentration", "Unknown"),
            "multisig_risk": labels.get("multisig_risk", "Unknown"),
            "market_signal": labels.get("market_signal", "Research"),
        },
        "scores": scores,
        "recommendation": {
            "action": "Monitor" if scores["risk_score"] >= 65 else "Research",
            "reason": "Large supply movement and custody concentration require further tracking before action.",
        },
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }

