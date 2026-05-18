from typing import Any


def score_risk(raw_data: dict[str, Any]) -> dict[str, int]:
    metrics = raw_data.get("metrics", {})
    concentration = int(metrics.get("top_10_holder_share", 20))
    multisig_supply = int(metrics.get("multisig_controlled_supply", 15))
    flow_usd = int(metrics.get("bridge_related_flow_usd", 0))

    risk_score = min(95, 35 + concentration // 2 + multisig_supply // 2 + min(flow_usd // 250_000, 12))
    confidence = 82 if raw_data.get("token") == "WCT" else 58
    alpha_score = max(40, 100 - risk_score // 2)
    return {
        "confidence": confidence,
        "risk_score": risk_score,
        "alpha_score": alpha_score,
    }

