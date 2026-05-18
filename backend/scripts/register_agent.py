#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from web3 import Web3


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_ENV = ROOT_DIR / "backend" / ".env"
FRONTEND_ENV = ROOT_DIR / "frontend" / ".env.local"

ARC_TESTNET_CHAIN_ID = 5042002
ARC_TESTNET_IDENTITY_REGISTRY = "0x8004A818BFB912233c491871b3d84c89A494BD9e"

IDENTITY_REGISTRY_ABI: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "register",
        "stateMutability": "nonpayable",
        "inputs": [{"name": "metadataURI", "type": "string"}],
        "outputs": [],
    },
    {
        "type": "function",
        "name": "getAgent",
        "stateMutability": "view",
        "inputs": [{"name": "agentId", "type": "uint256"}],
        "outputs": [
            {"name": "owner", "type": "address"},
            {"name": "metadataURI", "type": "string"},
        ],
    },
    {
        "type": "event",
        "name": "Transfer",
        "anonymous": False,
        "inputs": [
            {"name": "from", "type": "address", "indexed": True},
            {"name": "to", "type": "address", "indexed": True},
            {"name": "tokenId", "type": "uint256", "indexed": True},
        ],
    },
]


def read_env(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    values: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def require(name: str, value: str | None) -> str:
    if value:
        return value
    raise SystemExit(f"Missing required config: {name}")


def signed_raw_transaction(signed: Any) -> bytes:
    raw = getattr(signed, "raw_transaction", None)
    if raw is not None:
        return raw
    return signed.rawTransaction


def add_fee_fields(web3: Web3, tx: dict[str, Any]) -> dict[str, Any]:
    latest_block = web3.eth.get_block("latest")
    base_fee = latest_block.get("baseFeePerGas")
    if base_fee is None:
        tx["gasPrice"] = web3.eth.gas_price
        return tx

    priority_fee = web3.to_wei(1, "gwei")
    tx["maxPriorityFeePerGas"] = priority_fee
    tx["maxFeePerGas"] = int(base_fee * 2) + priority_fee
    return tx


def update_env_value(path: Path, key: str, value: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines() if path.exists() else []
    next_lines: list[str] = []
    replaced = False

    for line in lines:
        if line.startswith(f"{key}="):
            next_lines.append(f"{key}={value}")
            replaced = True
        else:
            next_lines.append(line)

    if not replaced:
        next_lines.append(f"{key}={value}")

    path.write_text("\n".join(next_lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register AlphaTrace as a real ERC-8004 agent on Arc Testnet.")
    parser.add_argument(
        "--metadata-uri",
        help="Agent metadata URI. Defaults to ALPHATRACE_AGENT_METADATA_URI from backend/.env.",
    )
    parser.add_argument(
        "--write-env",
        action="store_true",
        help="Write the registered owner address and token id back to backend/.env and frontend/.env.local.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print resolved config without sending a transaction.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    backend_env = read_env(BACKEND_ENV)
    frontend_env = read_env(FRONTEND_ENV)

    rpc_url = backend_env.get("ARC_RPC_URL") or frontend_env.get("NEXT_PUBLIC_ARC_RPC_URL")
    chain_id = int(backend_env.get("ARC_CHAIN_ID") or frontend_env.get("NEXT_PUBLIC_ARC_CHAIN_ID") or ARC_TESTNET_CHAIN_ID)
    private_key = backend_env.get("PRIVATE_KEY_AGENT")
    registry_address = backend_env.get("IDENTITY_REGISTRY_ADDRESS") or ARC_TESTNET_IDENTITY_REGISTRY
    metadata_uri = args.metadata_uri or backend_env.get("ALPHATRACE_AGENT_METADATA_URI") or "ipfs://alphatrace-demo-agent"

    rpc_url = require("ARC_RPC_URL or NEXT_PUBLIC_ARC_RPC_URL", rpc_url)
    private_key = require("PRIVATE_KEY_AGENT", private_key)

    web3 = Web3(Web3.HTTPProvider(rpc_url))
    if not web3.is_connected():
        raise SystemExit(f"Could not connect to RPC: {rpc_url}")

    account = web3.eth.account.from_key(private_key)
    registry = web3.eth.contract(
        address=Web3.to_checksum_address(registry_address),
        abi=IDENTITY_REGISTRY_ABI,
    )

    print("AlphaTrace ERC-8004 registration")
    print(f"  Chain id:          {chain_id}")
    print(f"  IdentityRegistry:  {registry_address}")
    print(f"  Agent owner:       {account.address}")
    print(f"  Metadata URI:      {metadata_uri}")

    if args.dry_run:
        print("\nDry run only. No transaction sent.")
        return

    tx = registry.functions.register(metadata_uri).build_transaction(
        {
            "from": account.address,
            "nonce": web3.eth.get_transaction_count(account.address),
            "chainId": chain_id,
        }
    )
    tx["gas"] = int(web3.eth.estimate_gas(tx) * 1.2)
    tx = add_fee_fields(web3, tx)

    signed = account.sign_transaction(tx)
    tx_hash = web3.eth.send_raw_transaction(signed_raw_transaction(signed))
    tx_hex = web3.to_hex(tx_hash)
    print(f"\nSubmitted registration tx: {tx_hex}")
    print(f"Explorer: https://testnet.arcscan.app/tx/{tx_hex}")

    receipt = web3.eth.wait_for_transaction_receipt(tx_hash, timeout=180)
    if receipt.status != 1:
        raise SystemExit(f"Registration transaction reverted: {tx_hex}")

    transfer_events = registry.events.Transfer().process_receipt(receipt)
    minted_events = [
        event
        for event in transfer_events
        if event["args"]["from"].lower() == "0x0000000000000000000000000000000000000000"
        and event["args"]["to"].lower() == account.address.lower()
    ]
    agent_id = str(minted_events[-1]["args"]["tokenId"]) if minted_events else ""

    print("\nRegistered AlphaTrace Agent")
    print(f"  ALPHATRACE_AGENT_ADDRESS={account.address}")
    if agent_id:
        print(f"  ALPHATRACE_AGENT_ID={agent_id}")
        owner, stored_metadata_uri = registry.functions.getAgent(int(agent_id)).call()
        print(f"  On-chain owner:    {owner}")
        print(f"  On-chain metadata: {stored_metadata_uri}")
    else:
        print("  ALPHATRACE_AGENT_ID could not be found from Transfer logs.")

    if args.write_env:
        update_env_value(BACKEND_ENV, "ARC_CHAIN_ID", str(chain_id))
        update_env_value(BACKEND_ENV, "IDENTITY_REGISTRY_ADDRESS", registry_address)
        update_env_value(BACKEND_ENV, "ALPHATRACE_AGENT_ADDRESS", account.address)
        update_env_value(BACKEND_ENV, "ALPHATRACE_AGENT_METADATA_URI", metadata_uri)
        if agent_id:
            update_env_value(BACKEND_ENV, "ALPHATRACE_AGENT_ID", agent_id)
        update_env_value(FRONTEND_ENV, "NEXT_PUBLIC_ALPHATRACE_AGENT_ADDRESS", account.address)
        print("\nUpdated backend/.env and frontend/.env.local.")


if __name__ == "__main__":
    main()
