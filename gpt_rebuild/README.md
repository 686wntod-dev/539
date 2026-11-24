# GPT Rebuilt 539 Registry v1

This branch records the reproducible ChatGPT clean-room / Shadow reconstruction of the 539 model project.

## Validation completed locally (2026-11-24)

- Formal7 clean-room replay: 7/7 retained 2026-11-17 lock outputs reproduced exactly (A/B/Pool10 and 39-number ranking); all 8 artifact SHA-256 values and the runtime SHA-256 were checked.
- Full4034 Shadow: 4/4 retained 2026-11-16 locks reproduced exactly.
- R3-HGB-NoPP Shadow: 2026-11-16 exclusion-10 list and all 39 scores reproduced exactly; max absolute score difference 0.
- Total retained model locks replayed: 12/12.
- Feature prefix-invariance checks passed at four cutoffs.
- This is historical replay validation, not a new forecast, not proof of superiority to random, and not a 90% R3 result.

## Important status boundaries

- `GPT_REBUILT_REGISTRY_V1` is a new GPT-generated reconstruction registry. It is not Canonical Registry v3.
- Formal7 is a Cleanroom replacement lineage, not recovered historical Production source.
- The four Full4034 models and R3-HGB remain Shadow-only.
- AI-1 Legacy and TieSeed are one family vote.
- Production authorization remains false. No external deployment is asserted.
- A fresh retraining attempt in the current environment did not reproduce archived model artifact bytes/rankings for ET/HGB/LOGIT/AI-2. Those new candidates were not promoted; the archived SHA-verified artifacts remain the replay source.
- The 11/17 R3-HGB A-line trainer and B-line backtest/lock originals remain missing. The R3-HGB replay in this package is the separate 11/16 Shadow challenger.
- The R3 fixed-10 exclusion 90% target remains unproven.

The full 1.22 MB reproducibility bundle and local validator are retained in the ChatGPT project handoff. This branch's CI is a governance/schema guard only; it does not claim to rerun the binary-model replay without the bundle.
