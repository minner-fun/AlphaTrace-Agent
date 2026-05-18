import json
from pathlib import Path
from typing import Any

from app.agent.task_parser import ParsedTask


async def analyze_token_flow_task(task: ParsedTask) -> dict[str, Any]:
    if task.target == "WCT":
        data_path = Path(__file__).resolve().parents[1] / "data" / "mock_wct_data.json"
        return json.loads(data_path.read_text(encoding="utf-8"))

    return {
        "token": task.target or "unknown",
        "network": "mock dataset",
        "observations": [],
        "metrics": {},
        "labels": {
            "holder_concentration": "Unknown",
            "multisig_risk": "Unknown",
            "market_signal": "Research",
        },
    }

