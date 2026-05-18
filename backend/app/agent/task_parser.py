import re
from dataclasses import dataclass


@dataclass(frozen=True)
class ParsedTask:
    task_type: str
    target: str | None
    raw_description: str


def extract_wallet_address(description: str) -> str | None:
    match = re.search(r"0x[a-fA-F0-9]{40}", description)
    return match.group(0) if match else None


def extract_project_name(description: str) -> str | None:
    words = re.findall(r"[A-Za-z][A-Za-z0-9_-]{1,30}", description)
    ignored = {"analyze", "research", "project", "airdrop", "token", "wallet", "risk"}
    for word in words:
        if word.lower() not in ignored:
            return word
    return None


def parse_task(description: str) -> ParsedTask:
    text = description.lower()

    if "wct" in text or "token flow" in text or "multisig" in text:
        return ParsedTask("token_flow_analysis", "WCT", description)

    if "wallet" in text or "smart money" in text:
        return ParsedTask("wallet_analysis", extract_wallet_address(description), description)

    if "airdrop" in text or "project" in text:
        return ParsedTask("project_research", extract_project_name(description), description)

    return ParsedTask("generic_market_research", None, description)

