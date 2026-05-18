# Architecture

AlphaTrace is split into a frontend console and a backend agent runtime.

## Frontend

The frontend owns wallet connection, job creation, job inspection, report display, and feedback submission. Chain calls are wrapped in `frontend/lib/chain.ts` and ABI definitions live in `frontend/config/erc8183.ts`.

## Backend

The backend owns local job sync, worker execution, mock analysis, report generation, report hashing, and deliverable submission. Chain calls are wrapped in `backend/app/chain`.

## Data

SQLite is the default local database. The core tables are:

- `agent_jobs`
- `reports`
- `feedbacks`

## MVP Boundary

The MVP keeps WCT analysis mocked so the demo is reliable. Real indexer, RPC log, The Graph, Dune, or Covalent integrations can replace `backend/app/analysis/token_flow.py` later.

