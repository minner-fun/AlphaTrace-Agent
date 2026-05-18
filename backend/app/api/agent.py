from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(prefix="/api/agent", tags=["agent"])


@router.get("/profile")
def get_agent_profile():
    settings = get_settings()
    return {
        "name": "AlphaTrace Agent",
        "address": settings.alphatrace_agent_address,
        "identity_id": settings.alphatrace_agent_id,
        "metadata_uri": settings.alphatrace_agent_metadata_uri,
        "type": "market_intelligence_agent",
        "capabilities": [
            "token_flow_analysis",
            "wallet_analysis",
            "multisig_risk_analysis",
            "project_research",
            "alpha_report_generation",
        ],
        "version": "0.1.0",
        "status": "online",
    }

