# 539 Cleanroom Replay CI

This branch adds an actual replay runner to the existing governance-only CI.

## Required input bundle

Place the SHA-locked ZIP at:

`gpt_rebuild/replay_bundle.zip`

Expected ZIP SHA-256 (verified in the local replay environment on 2026-11-26):

`02fd9ff8b17f2eaa57d1b29dcec45a09f789d810b8a6aba7bf068666ebc7d17a`

Expected size: 1,224,781 bytes. The ZIP must contain the root-level `bundle_manifest.json`, `formal7/`, `shadow4/`, `r3_hgb/`, and `data/` paths.

The workflow intentionally fails closed when this bundle is absent. It must not report a successful replay based only on a JSON PASS declaration.

## Replay procedure

1. Verify the bundle SHA and manifest before execution.
2. Extract to `gpt_rebuild/replay/`.
3. Install the pinned environment in `requirements-replay.txt`.
4. Run `validate_rebuild.py`.
5. Upload `validation_result.json` as a workflow artifact.

The validator replays Formal7 (7), Full4034 Shadow (4), and R3-HGB-NoPP Shadow (1) against their retained locks. This is historical replay, not forward blind testing or Production authorization.

## Governance boundaries

- Formal7 is a Cleanroom replacement lineage, not recovered historical Production source.
- Shadow4 and R3-HGB remain Shadow-only.
- AI-1 Legacy and TieSeed count as one family vote.
- No claim of predictive superiority to random or 90% R3 exclusion performance.
- No external TSA, WORM, scheduler, or Production deployment is asserted.
