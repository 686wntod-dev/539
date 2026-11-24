# v10 Run 7 — final capture and reconciliation validation (2026-11-24)

## Run identity
- Repository: 686wntod-dev/539
- Workflow run: 45401866581 (Run #7)
- Commit: 77ca0f2d579a386a94885c43d0e6f5db8a6469f5
- Workflow conclusion: success
- Artifact: 539-v10-official-api-evidence-45401866581
- Artifact ID: 14923702362
- Artifact SHA-256: 300ab24ebce769d525c6d9ad27200f7060595accf981a4064b902718a5fdeb09

## Capture validation
- Mode: full
- Requested/captured months: 35/35 (2024-01 through 2026-11)
- HTTP 200: 35/35
- Valid schema: 35/35
- Raw response bytes: 35
- Metadata records: 35
- Raw SHA256 and content-length against metadata: 35/35 PASS
- Parsed API rows: 913
- Unique dates / unique periods: 913 / 913
- Sorted date sequence: PASS
- Each draw has five distinct values in 01–39: PASS
- Network failures: 0

## Candidate reconciliation
- Candidate input rows: 906
- Exact date + five-number matches: 905
- Candidate rows without exact API match: 1
- API-only or conflicting rows: 8
  - API-only new dates: 7 (2026-11-14, 2026-11-17, 2026-11-18, 2026-11-19, 2026-11-20, 2026-11-21, 2026-11-23)
  - Same-date number conflict: 1 (2026-10-23)
- candidate_reconciliation_status: REVIEW_REQUIRED_DIFFERENCES

## Secondary cross-check
The 2026-10-23 third-party historical listing shows 115000257 as 03 07 14 17 27, matching the website-internal API rather than the candidate master row 03 14 17 27 37. Seven API-only dates also match secondary historical listings. These are secondary corroborations only; no official historical-page raw capture has been archived in this run.

## Safe disposition
- Capture/raw-byte integrity for Run #7: PASS.
- Reconciliation differences: REVIEW_REQUIRED; recorded in append-only evidence files.
- Canonical master / Registry / historical prediction locks: NOT MODIFIED.
- Formal7 production source restoration and SRC-01..SRC-06 Production P0 gate: NOT RESOLVED by this run.
- This run does not prove any model performance target, including R3 90% exclusion or positive-pool lift.
