# API

## Sync Job

`POST /api/jobs/sync`

Creates or updates a local job after frontend job creation.

## Run Job

`POST /api/jobs/{job_id}/run`

Runs the AlphaTrace worker, stores a report, calculates its hash, and submits or mock-submits the hash.

## Get Job

`GET /api/jobs/{job_id}`

Returns job metadata and report hash fields when available.

## Get Report

`GET /api/reports/{job_id}`

Returns full report JSON, report hash, and hash verification result.

## Feedback

`POST /api/jobs/{job_id}/feedback`

Stores user feedback locally. ERC-8004 reputation submission is stubbed for the MVP.

