import json
from typing import Any

from eth_utils import keccak


def normalize_report(report: dict[str, Any]) -> str:
    return json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def hash_report(report: dict[str, Any]) -> str:
    return "0x" + keccak(text=normalize_report(report)).hex()


def verify_report_hash(report: dict[str, Any], report_hash: str) -> bool:
    return hash_report(report).lower() == report_hash.lower()

