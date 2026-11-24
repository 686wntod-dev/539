# v10 Run 10 — hardened capture and candidate validation (2026-11-24)

- Workflow run: 45402478097 (Run #10)
- Workflow commit: 0adc3f19d9bb4ca11e6756e24eff6cf9393efeed
- Workflow conclusion: SUCCESS
- Full capture: 2024-01 through 2026-11, 35/35 months, HTTP 200, valid schema, no network or schema failures.
- API rows: 913; unique dates: 913; unique periods: 913.
- Parser self-test: PASS, including malformed response rejection.
- Parser hardening: rtCode=0 required; totalSize must equal rows returned; malformed date/period/numbers, duplicate dates/periods and truncated responses are rejected.
- Candidate validation: 906/906 rows validated; dates/numbers valid; duplicate dates rejected.
- Candidate reconciliation: 905 exact date+five-number matches; 1 same-date conflict; 7 API dates absent from candidate input. Status REVIEW_REQUIRED_DIFFERENCES.
- Raw bytes/metadata pairs independently rehashed in downloaded artifact: 35/35 PASS.
- Artifact ID: 14923353141
- Artifact SHA256: 536184221df36b2fac03e2d1e416fccbdb997fa733ed0096efbfdec883079dec
- Artifact retention expires: 2027-02-22T13:20:50Z

This validates the capture/parser/candidate-input pipeline only. The 8 reconciliation differences remain in append-only review; no official historical-page raw evidence was archived here. No canonical master, Registry, historical prediction lock, Formal7 model source, or Production deployment artifact was modified or restored. SRC-01..SRC-06 remain blocked.
