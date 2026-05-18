# AlphaTrace Agent

AlphaTrace is an ERC-8004 registered AI market intelligence agent that accepts ERC-8183 research jobs, analyzes Web3 market signals off-chain, submits verifiable report hashes on Arc, and supports USDC-style job settlement flows.

This MVP is optimized for hackathon demo speed. It can run fully locally with mock WCT analysis data, while keeping the chain interaction code isolated so real Arc Testnet contracts can be connected through environment variables.

## Why Arc

AlphaTrace uses Arc as the coordination layer for agent jobs:

- ERC-8004 gives the agent an on-chain identity and reputation surface.
- ERC-8183 turns research requests into job records with lifecycle states.
- The backend keeps full JSON reports off-chain and submits only a stable keccak report hash as the deliverable proof.

## Architecture

```text
frontend/
  Next.js + TypeScript + Tailwind + wagmi + viem + RainbowKit

backend/
  FastAPI + SQLAlchemy + SQLite + web3.py

contracts/abis/
  Minimal ERC-8183 and ERC-8004 ABI files
```

The demo flow is:

```text
Create research job -> sync backend job -> run AlphaTrace worker
-> generate report JSON -> calculate report hash -> submit/mock submit hash
-> display report -> feedback
```

## Local Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload --port 8000
```

Keep `SUBMIT_TO_CHAIN=false` for a local demo. Set it to `true` only after configuring:

```env
ARC_RPC_URL=
ARC_CHAIN_ID=
PRIVATE_KEY_AGENT=
ERC8183_CONTRACT_ADDRESS=
```

### Frontend

```bash
cd frontend
npm install
copy .env.local.example .env.local
npm run dev
```

Open `http://localhost:3000`.

## Demo Flow

1. Open the Agent Profile page and show the ERC-8004 identity fields.
2. Create a WCT research job from `/create-job`.
3. Use `Demo sync` if contracts are not configured yet.
4. Open the generated Job detail page.
5. Click `Run Agent`.
6. The backend reads mock WCT data, generates a structured report, calculates a stable hash, and mock-submits it.
7. Show the report summary, scores, evidence list, recommendation, and hash verification badge.
8. Submit feedback.

## Backend API

```http
POST /api/jobs/sync
POST /api/jobs/{job_id}/run
GET  /api/jobs/{job_id}
GET  /api/reports/{job_id}
POST /api/jobs/{job_id}/feedback
GET  /api/agent/profile
```

## Report Hash

Reports are serialized with sorted keys and compact separators before hashing:

```python
json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
```

The backend then calculates `keccak(text=normalized_json)` and stores the full JSON plus the hash.

## Contract Addresses

Fill these values after registering/deploying on Arc Testnet:

```env
ERC8183_CONTRACT_ADDRESS=
IDENTITY_REGISTRY_ADDRESS=
REPUTATION_REGISTRY_ADDRESS=
VALIDATION_REGISTRY_ADDRESS=
USDC_ADDRESS=
ALPHATRACE_AGENT_ADDRESS=
ALPHATRACE_AGENT_ID=
ALPHATRACE_AGENT_METADATA_URI=
```

## Roadmap

- Replace mock WCT data with indexer/RPC transfer logs.
- Add USDC approve and fund UI.
- Persist reports to IPFS or Supabase.
- Add an event listener for ERC-8183 jobs.
- Record feedback through ERC-8004 ReputationRegistry.
- Add queueing for multiple agent jobs.

