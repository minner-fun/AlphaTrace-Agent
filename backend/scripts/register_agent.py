#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

import httpx
from web3 import Web3
from web3.exceptions import ContractLogicError


ROOT_DIR = Path(__file__).resolve().parents[2]
BACKEND_ENV = ROOT_DIR / "backend" / ".env"
FRONTEND_ENV = ROOT_DIR / "frontend" / ".env.local"

ARC_TESTNET_CHAIN_ID = 5042002
ARC_TESTNET_IDENTITY_REGISTRY = "0x8004A818BFB912233c491871b3d84c89A494BD9e"
PINATA_PIN_JSON_URL = "https://api.pinata.cloud/pinning/pinJSONToIPFS"

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
        "name": "ownerOf",
        "stateMutability": "view",
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "outputs": [{"name": "", "type": "address"}],
    },
    {
        "type": "function",
        "name": "tokenURI",
        "stateMutability": "view",
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "outputs": [{"name": "", "type": "string"}],
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
        value = value.strip()
        if not (value.startswith('"') or value.startswith("'")) and " #" in value:
            value = value.split(" #", 1)[0].strip()
        values[key.strip()] = value.strip('"').strip("'")
    return values


def require(name: str, value: str | None) -> str:
    if value:
        return value
    raise SystemExit(f"Missing required config: {name}")


def require_private_key(name: str, value: str | None) -> str:
    private_key = require(name, value).strip()
    if private_key.startswith(("0X", "0x")):
        private_key = "0x" + private_key[2:]
    else:
        private_key = f"0x{private_key}"

    if not re.fullmatch(r"0x[0-9a-fA-F]{64}", private_key):
        raise SystemExit(
            f"Invalid {name}. It must be a 32-byte hex private key, like 0x + 64 hex chars. "
            "Do not paste a wallet address, contract address, mnemonic phrase, or Chinese placeholder text."
        )
    return private_key


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


def write_agent_env(
    backend_env_path: Path,
    frontend_env_path: Path,
    chain_id: int,
    registry_address: str,
    agent_address: str,
    metadata_uri: str,
    agent_id: str,
) -> None:
    update_env_value(backend_env_path, "ARC_CHAIN_ID", str(chain_id))
    update_env_value(backend_env_path, "IDENTITY_REGISTRY_ADDRESS", registry_address)
    update_env_value(backend_env_path, "ALPHATRACE_AGENT_ADDRESS", agent_address)
    update_env_value(backend_env_path, "ALPHATRACE_AGENT_METADATA_URI", metadata_uri)
    update_env_value(backend_env_path, "ALPHATRACE_AGENT_ID", agent_id)
    update_env_value(frontend_env_path, "NEXT_PUBLIC_ALPHATRACE_AGENT_ADDRESS", agent_address)


def build_default_metadata(agent_address: str) -> dict[str, Any]:
    return {
        "name": "AlphaTrace Agent",
        "description": (
            "AlphaTrace is an ERC-8004 registered Web3 market intelligence agent "
            "that accepts ERC-8183 research jobs and submits verifiable report hashes on Arc."
        ),
        "type": "market_intelligence",
        "version": "0.1.0",
        "owner": agent_address,
        "network": "Arc Testnet",
        "frameworks": ["ERC-8004", "ERC-8183"],
        "capabilities": [
            "token_flow_analysis",
            "wallet_intelligence",
            "multisig_risk_review",
            "structured_json_reports",
            "report_hash_delivery",
        ],
        "endpoints": {
            "api": "http://localhost:8000",
        },
    }


def load_metadata(path: str | None, agent_address: str) -> dict[str, Any]:
    if not path:
        return build_default_metadata(agent_address)

    metadata_path = Path(path).expanduser()
    if not metadata_path.is_absolute():
        metadata_path = ROOT_DIR / metadata_path
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def pinata_headers(env: dict[str, str]) -> dict[str, str]:
    jwt = env.get("PINATA_JWT")
    if jwt:
        return {"Authorization": f"Bearer {jwt}"}

    api_key = env.get("PINATA_API_KEY")
    secret_api_key = env.get("PINATA_SECRET_API_KEY")
    if api_key and secret_api_key:
        return {
            "pinata_api_key": api_key,
            "pinata_secret_api_key": secret_api_key,
        }

    raise SystemExit("Missing Pinata credentials: set PINATA_JWT or PINATA_API_KEY + PINATA_SECRET_API_KEY")


def upload_metadata_to_pinata(env: dict[str, str], metadata: dict[str, Any], name: str, trust_env: bool) -> str:
    payload = {
        "pinataMetadata": {"name": name},
        "pinataContent": metadata,
    }
    try:
        response = httpx.post(
            PINATA_PIN_JSON_URL,
            headers=pinata_headers(env),
            json=payload,
            timeout=60,
            trust_env=trust_env,
        )
    except ImportError as exc:
        raise SystemExit(
            "Pinata upload failed because your environment uses a SOCKS proxy, but socksio is not installed. "
            "Run `python -m pip install socksio` or retry with `--ignore-proxy`."
        ) from exc
    if response.status_code >= 400:
        raise SystemExit(f"Pinata upload failed: {response.status_code} {response.text}")

    result = response.json()
    cid = result.get("IpfsHash") or result.get("cid")
    if not cid:
        raise SystemExit(f"Pinata upload response did not include a CID: {result}")
    return f"ipfs://{cid}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Register AlphaTrace as a real ERC-8004 agent on Arc Testnet.")
    parser.add_argument(
        "--existing-agent-id",
        help="Recover an already registered ERC-8004 agent by token id and optionally write it to env files.",
    )
    parser.add_argument(
        "--metadata-uri",
        help="Agent metadata URI. Defaults to ALPHATRACE_AGENT_METADATA_URI from backend/.env.",
    )
    parser.add_argument(
        "--pinata-upload",
        action="store_true",
        help="Upload agent metadata JSON to Pinata and use the returned ipfs:// CID as metadataURI.",
    )
    parser.add_argument(
        "--metadata-file",
        help="Optional JSON file to upload with --pinata-upload. Defaults to a generated AlphaTrace metadata JSON.",
    )
    parser.add_argument(
        "--pinata-name",
        default="alphatrace-agent-metadata.json",
        help="Name stored in Pinata pin metadata when using --pinata-upload.",
    )
    parser.add_argument(
        "--ignore-proxy",
        action="store_true",
        help="Ignore HTTP_PROXY/HTTPS_PROXY/ALL_PROXY environment variables for Pinata upload.",
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
    private_key = require_private_key("PRIVATE_KEY_AGENT", private_key)

    web3 = Web3(Web3.HTTPProvider(rpc_url))
    if not web3.is_connected():
        raise SystemExit(f"Could not connect to RPC: {rpc_url}")

    account = web3.eth.account.from_key(private_key)
    metadata_json = load_metadata(args.metadata_file, account.address)

    if args.pinata_upload and not args.dry_run:
        print("Uploading agent metadata to Pinata...")
        metadata_uri = upload_metadata_to_pinata(
            backend_env,
            metadata_json,
            args.pinata_name,
            trust_env=not args.ignore_proxy,
        )

    registry = web3.eth.contract(
        address=Web3.to_checksum_address(registry_address),
        abi=IDENTITY_REGISTRY_ABI,
    )

    if args.existing_agent_id:
        agent_id = str(args.existing_agent_id)
        owner = registry.functions.ownerOf(int(agent_id)).call()
        stored_metadata_uri = registry.functions.tokenURI(int(agent_id)).call()
        metadata_uri = args.metadata_uri or stored_metadata_uri

        print("Recovered existing AlphaTrace Agent")
        print(f"  Chain id:          {chain_id}")
        print(f"  IdentityRegistry:  {registry_address}")
        print(f"  ALPHATRACE_AGENT_ADDRESS={owner}")
        print(f"  ALPHATRACE_AGENT_ID={agent_id}")
        print(f"  Metadata URI:      {metadata_uri}")

        if args.write_env:
            write_agent_env(
                BACKEND_ENV,
                FRONTEND_ENV,
                chain_id,
                registry_address,
                owner,
                metadata_uri,
                agent_id,
            )
            print("\nUpdated backend/.env and frontend/.env.local.")
        return

    print("AlphaTrace ERC-8004 registration")
    print(f"  Chain id:          {chain_id}")
    print(f"  IdentityRegistry:  {registry_address}")
    print(f"  Agent owner:       {account.address}")
    print(f"  Metadata URI:      {metadata_uri}")
    if args.pinata_upload and args.dry_run:
        print("  Pinata upload:     dry run only")
        print("  Metadata preview:")
        print(json.dumps(metadata_json, indent=2, ensure_ascii=False))

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
        try:
            owner = registry.functions.ownerOf(int(agent_id)).call()
            stored_metadata_uri = registry.functions.tokenURI(int(agent_id)).call()
            print(f"  On-chain owner:    {owner}")
            print(f"  On-chain metadata: {stored_metadata_uri}")
        except ContractLogicError as exc:
            print(f"  On-chain readback warning: {exc}")
            print("  Registration succeeded, but ownerOf/tokenURI readback failed. Env can still be written from tx logs.")
    else:
        print("  ALPHATRACE_AGENT_ID could not be found from Transfer logs.")

    if args.write_env:
        if agent_id:
            write_agent_env(
                BACKEND_ENV,
                FRONTEND_ENV,
                chain_id,
                registry_address,
                account.address,
                metadata_uri,
                agent_id,
            )
        else:
            update_env_value(BACKEND_ENV, "ARC_CHAIN_ID", str(chain_id))
            update_env_value(BACKEND_ENV, "IDENTITY_REGISTRY_ADDRESS", registry_address)
            update_env_value(BACKEND_ENV, "ALPHATRACE_AGENT_ADDRESS", account.address)
            update_env_value(BACKEND_ENV, "ALPHATRACE_AGENT_METADATA_URI", metadata_uri)
            update_env_value(FRONTEND_ENV, "NEXT_PUBLIC_ALPHATRACE_AGENT_ADDRESS", account.address)
        print("\nUpdated backend/.env and frontend/.env.local.")


if __name__ == "__main__":
    main()
