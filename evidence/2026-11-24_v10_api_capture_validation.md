# v10 official-site API reconciliation review — 2026-11-24

- GitHub Actions run: 45401057001
- Commit: b30ea7c649a76904db0698bde272be4e9f9cffbe
- Artifact: 539-v10-official-api-evidence-45401057001
- Artifact SHA-256: 1dfb52a046a96d95299290dcb287e4e2eb37d869e7ec6997bcec38b987132ff0
- Endpoint classification: Taiwan Lottery website-internal API; not a published/stable API contract.
- Captured months: 35/35 (2024-01 through 2026-11), HTTP 200: 35/35, schema valid: 35/35.
- Raw response files: 35; metadata files: 35; raw-byte SHA-256 and content-length checks: 35/35 PASS.
- Parsed records: 913; unique dates: 913; unique periods: 913; date order: PASS; five distinct values in 01–39: PASS.
- Candidate rows: 906; exact date+five-number matches: 905.
- Differences: seven API-only records and one known 2026-10-23 number conflict. See adjacent CSV.
- Important: API period values are candidates from a website-internal endpoint, not yet independently verified official issue IDs. This report is evidence-only; do not promote into canonical master, Registry, or prediction locks.
- No model source, production runtime, R3 A/B original artifacts, or deployment receipts are included in this artifact.

## Disposition
Capture and byte-integrity checks are CLOSED for this run. The seven API-only rows and 2026-10-23 conflict remain REVIEW_REQUIRED until checked against archived official historical pages or independently authoritative draw records. Formal production remains blocked by the six existing SRC-01..SRC-06 gates.
