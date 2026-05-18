from typing import Any

from app.agent.task_parser import ParsedTask


async def analyze_wallet_task(task: ParsedTask) -> dict[str, Any]:
    return {
        "wallet": task.target,
        "observations": [
            {
                "type": "wallet_activity",
                "title": "Wallet analysis queued",
                "description": "MVP uses mock wallet intelligence until a real indexer is connected.",
                "source": "mock_agent",
                "severity": "low",
            }
        ],
        "metrics": {"known_labels": 0, "recent_transactions": 0},
    }

