# GPT-generated 539 project artifact inventory — 2026-11-26

## Purpose and handling

This is an append-only inventory of artifacts already created in the 539 project and retained in ChatGPT Library. It exists to prevent repeated requests for the user to supply the same material and to distinguish recovered GPT project artifacts from historical Production identity. No user-side external backup is required for the artifacts listed below.

The inventory records only artifacts actually found in the project Library and/or exact hashes documented by prior GPT-generated manifests. "Rehashed this run" means the exact Library file bytes were materialized and SHA-256 recomputed on 2026-11-26. A manifest-only entry is not represented as a fresh byte-level verification.

## Exact bytes rehashed on 2026-11-26

| Artifact | Bytes | SHA-256 | Validation / qualification |
|---|---:|---|---|
| master_4042.csv | 3,494,048 | d04617018e5c2b97cd76822e7e61576420d6720a9a66e6d2064cd25c1c9d34f6 | 4,042 rows; 2014-01-01–2026-11-21; 34 columns; 0 duplicate dates; 0 rows with row_valid=false. This is the 4,042-row Shadow inference master, not the 4,037-row Formal7 lock input. |
| 539_Formal7_Cleanroom_Runtime_4037_v2.py | 7,877 | fe0d2a5daf11e1be08fec302dff5715bb514fc97cc447ea00ff42840d51ce387 | Compile-only PASS; Cleanroom replacement runtime, not historical Production runtime. |
| train_V1_V2_R3_CR1.py | 1,860 | 9c802d713270599bf839dbf82ad0eb31d5bbf9417049087fe48c9589f34e469c | Compile-only PASS; CR1 replacement trainer, not historical Production trainer. |
| prelock_R3_HGB_NoPP_2026-11-16.py | 5,518 | 47a0749463d91b66b975cd00ac4301b4eabdf4b2e8e8fcd5b736d2504c816e12 | Compile-only PASS; 2026-11-16 Shadow challenger script, not the 2026-11-17 A-line original trainer. |
| R3_HGB_NoPP_2026-11-16_feature_schema.json | 956 | 4231655ed8d98465fec7310ed8f951889eb58b7fef1faa4f383e1f731cb3109a | Exact 32-feature Shadow schema. |
| R3_HGB_NoPP_2026-11-16_prediction_lock.json | 2,563 | fbb7bd88b496367313424e4081370d9afa35e6db2196996572766ee65f79c234 | Existing 2026-11-16 Shadow prediction lock; preserve unchanged. |
| 539_2026-11-17_CR1_正式7賽前預測鎖_v1.json | 18,317 | 37c3be7272548bf41772910d828ed593ec49c8c9037f70d4bfa6e283b1107ca1 | Existing 7-model pre-draw lock; lock ID 539-LOCK-20261117-21218b02fbd6; preserve unchanged. |
| Stage116_SevenModel_Shadow_Prelock_2026-11-23.json | 21,388 | 8a53f56b6d2fc6ccf577a3289e7096aec8b772f0eb651cf0d8a46565a3f8daae | Existing 7-model Shadow prelock; target 2026-11-23; 4,042-row master; Formal7 remains HOLD. |
| 539_CR1_V3_100期前瞻逐期監控_v2_追加11-16官方結果與11-17鎖.csv | 377,198 | 118702e4d3a7baab939effaf17206185b1b28f16e6f8f8222dcdca73835dc41a | 1,200 rows = 100 draw indices × 12 model slots; only 24 rows have non-empty Pool10/lock ID in the actual bytes. Do not call this 100 fully completed prospective predictions. |
| SHA256_manifest_v2.csv | 3,868 | e6a0ae97cff9d9d55d4c0132108f19af2a25bcde15d287262e27229c50bb9ba3 | GPT-generated artifact manifest for 4037/CR1 recovery package. |
| Stage171_status.json | 2,324 | 79ea195dba5bf78e4d92f5361807b9e8a944c42aadfe60949ecc59d3e3ec1dec | 39,000-sample ET/HGB/LOGIT challengers; SHADOW_ONLY; no new lock or consensus. |
| Stage171_manifest.csv | 2,485 | 98a9233bdc1f7255f9888e255c8064e102ee7de705b2370dd0ad30a124bf3f4d | Manifest bytes rehashed; records source and challenger artifact hashes. |
| Stage142_2026-11-23_CleanroomV10工件恢復與鎖定重播報告.md | 6,471 | 376a163496874554e5d3d740966a65774c2c1c80a5aae51fdf3b47e121f48530 | GPT-generated report: 7/7 Shadow replay and exact model artifact recovery within the Cleanroom v10 scope; not Production recovery. |
| task3_code_provenance_matrix_v1.csv | 3,609 | ce66f0d149d4c3ee7551a1b324e7abf4d0c2472ccb3076e57f89b571770fef44 | GPT-generated provenance matrix; differentiates Cleanroom replacements, Shadow artifacts and historical Production originals. |

## Prior GPT manifests: recorded hash/size, not rehashed in this run

| Artifact | Recorded bytes | Recorded SHA-256 | Qualification |
|---|---:|---|---|
| R3_HGB_NoPP_2026-11-16_model.joblib | 29,496 | 80ea63669eabe924708b16467bd6faff466b6ba6c360e283c4e25f5ddc0b92b7 | Recorded in GPT-generated R3 SHA256 manifest and provenance matrix; 32-feature Shadow challenger. Exact model bytes were not materialized in this run. |
| Formal7 4037 master used by 2026-11-17 lock | — | 6c18084eab2966e4afc37e45fa916ad4a77414f07733a2947e321851c56e1628 | Hash and 4,037-row identity recorded in the formal lock and QA report; not interchangeable with master_4042.csv. |
| Tracker v1 | 275,107 | ece44f9bdc2f6af3885b846c14fac7b00be7d0b1f585c93aa6e687e27699137c | Prior GPT recovery report; 1,200 rows / 100 draw indices / 12 model slots; distinct from v2. |

## Validation performed this run

- Python compile-only checks: Formal7 Cleanroom Runtime v2, V1/V2/R3 CR1 trainer, and R3-HGB-NoPP 2026-11-16 script all PASS.
- master_4042.csv: exact SHA match to Stage116 source declaration; 4,042 rows, chronological range 2014-01-01 through 2026-11-21, no duplicate dates, no invalid rows.
- Stage116 Shadow lock declares the same 4,042-row master SHA and seven model entries.
- The 2026-11-17 Formal7 lock references a different 4,037-row master SHA. This is an expected version boundary, not a mismatch to be overwritten.
- Tracker v2 actual bytes contain 1,200 model slots but only 24 populated Pool10/lock ID rows; existing Stage201 audit restrictions remain applicable.
- No model retraining, historical replay, historical draw audit, prediction generation, or lock modification was performed in this inventory pass.

## Required interpretation

1. GPT-created Cleanroom/Shadow files are real project artifacts and should be reused as such; do not repeatedly ask the user to supply them.
2. A recovered Cleanroom replacement is not the same thing as the historical Production original. Preserve that provenance distinction.
3. R3-HGB-NoPP is a separate Shadow challenger and does not replace the original Formal7 R3-New-1 CR1 source or the specified 2026-11-17 A/B trainer/backtest/lock.
4. The 4,037-row Formal7 master, 4,042-row Shadow master, and 4,043-row append-only candidate are distinct data versions. Never overwrite or silently substitute them.
5. Keep existing Stage/lock/manifest evidence append-only. Do not rerun already accepted replay or audit scopes.
6. Continue internal GPT Library artifact recovery and reconstruction first. Do not send the user back to external backup searches as the default next action.

## Next internal work

- Build a version-aware artifact map linking Stage, Library artifact, SHA256 manifest, model ID, lock ID, master version and permitted use.
- Continue locating exact GPT Library bytes for the remaining manifest-referenced serialized model artifacts and formal master versions.
- Use existing Cleanroom/Shadow assets for scoped analysis only; keep Formal7 Production and R3 90% target gated by their existing validation requirements.


## Second recovery pass — exact master versions and Stage179/181 lineage (2026-11-26)

### Exact master bytes recovered and rehashed

| Artifact | Bytes | SHA-256 | Scope and status |
|---|---:|---|---|
| AI3_Legacy_Full4037_Rebuilt_v2.csv | 3,489,427 | 6c18084eab2966e4afc37e45fa916ad4a77414f07733a2947e321851c56e1628 | Exact 4,037-row master, 2014-01-01–2026-11-16; matches the master hash in the 2026-11-17 Formal7 lock. Recovered from GPT Library and rehashed this pass. |
| 539_Stage169_master_4043_2026-11-23_append_only_candidate.csv | 3,494,965 | 778214d7906c45d8dfd886eb5a52653868c6a4d874cdfb474d8aeb8199df0ce3 | Exact 4,043-row append-only candidate, 2014-01-01–2026-11-23; matches Stage179/181 source hash. Not canonical master. |
| master_4043_2026-11-23_official_evidence_appended.csv | 3,519,609 | 24abd0b9388b48bb0ce07e395673feadefa39491a0682b2fb2adb532ac0499c3 | Exact 4,043-row enriched candidate, 40 columns; append-only evidence overlay. Last row remains USER_CONFIRMED for base source/period ID, with a separate OFFICIAL_RESULT_CROSSCHECKED field using CTBC Bank and CNA cross-checks. Not a Taiwan Lottery raw response archive and not canonical. |

Both 4,043-row files have unique dates and issue IDs. The last row is 2026-11-23 / 115000283 / 04 07 22 30 34. The enriched candidate does not overwrite its parent or change the base source trust grade.

### Stage179 / Stage181 evidence recovered

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Stage179_report.md | 3,203 | dbddc3f8aab0bf86a93862916b163e435437a202b4178b20aecffcd8f5d93a46 |
| Stage179_predictions_and_metadata.json | 19,918 | 5ffe840ab488323dd7bffb274b78b5af92804a19a3cefd63fa7b1ad83af302c7 |
| Stage179_model_summary.csv | 1,566 | 06d0132d54d22c625c413872f18c8c74b444798feb7c29d83bb3ef2802fe6399 |
| Stage179_all_model_rankings.csv | 32,923 | b0c67d61ee3d53e8c0a258ded97521229a1d1096639327bb250fd7601cc1f780 |
| Stage179_SHA256_manifest.csv | 1,117 | bc13035165e8d33ef6de3df90e9e73d4c1928b6c1b83597048d43ffb8ed21041 |
| Stage182_corrected_per_model_metadata.csv | 1,800 | 0d02fa78b3915f00cf641c1973697c1931571033b46deaf0bc061c712eee96b9 |
| Stage181_final_audit.json | 13,473 | c1992cfc5603d21a6605aa77dd50c437498b7a6a46761de1ebd85e61f487ae5 |
| Stage173_2026-11-24_official_result_sync_manifest.json | 1,749 | 42c5c74562e9c04bf33fa21662388dce07dcdc92fc8cf1e12cb15c982413ff97 |

Stage179 recorded eight Shadow model outputs and 312 rankings (8 × 39), with 4,043-row input SHA matching the recovered append-only candidate. Stage182 corrected the method metadata: V1/V2/R3 and AI2 proxies are supervised classifiers; AI-1 Legacy/TieSeed are 20-draw deterministic frequency rankers with zero supervised fit rows; AI-3 is a full-history K=2000 transition-count model with 4,042 adjacent transitions, not a 39,000-row supervised fit. AI2 17F remains a challenger, not proven superior to 19F.

Stage181 reports structural checks PASS for all eight Stage180 model outputs, but keeps the entire release SHADOW_ONLY. It records the Stage179 training-source packaging gap (AUD-01), method metadata correction (AUD-02), V2 tie-at-cutoff (AUD-03), overlap-order normalization (AUD-04), AI2 proxy limitations (AUD-05), R3 90% not proven (AUD-06), no strict paired historical comparison (AUD-07), and the 2026-11-23 source evidence qualification (AUD-08). These are existing audit findings, not newly invented defects; do not open duplicate problem IDs.

### Distinct model artifact generations — do not merge

Stage175 and Stage179 manifests describe different artifact snapshots:
- Stage175 ET/HGB/LOGIT: 676,009 / 42,208 / 1,905 bytes, hashes 0dc76123... / e2b56311... / 01b72acf...
- Stage179 ET/HGB/LOGIT: 685,945 / 31,312 / 1,905 bytes, hashes d1678a76... / 21070b18... / 428fe622...
- Stage175 AI2 19F: 239,529 bytes, SHA 4f9fefa0...
- Stage179 AI2 19F: 228,809 bytes, SHA 38f382ab...

The manifests and model output metadata are recovered, but the Stage179 serialized joblib raw bytes and the exact Stage179 trainer/source package were not materialized in this pass. Stage181 AUD-01 explicitly records that the Stage179 bundle omitted the executed training script and complete arguments. Therefore Stage179 predictions/rankings are recoverable as GPT-created historical records, while exact trainer-to-model reproducibility is not established. Do not substitute Stage175 artifacts for Stage179 artifacts or vice versa.

### Version-aware recovery classification

- **A — exact bytes + matching SHA recovered:** 4037 master; 4042 Shadow master; 4043 append-only candidate; 4043 evidence-enriched candidate; Cleanroom Runtime v2; CR1 trainer; R3-HGB-NoPP 2026-11-16 script/schema/lock; 2026-11-17 Formal7 lock; Stage116 Shadow lock and listed report/tracker artifacts.
- **B — GPT historical records/manifests recovered, serialized raw bytes or execution source incomplete:** Stage179 model artifacts and training source; Stage175/179 artifact generation linkage; Stage179 run package.
- **C — reproducible Cleanroom/Shadow replacement from retained code/config/data, new identity only:** CR1 replacement runtime/trainer and the explicitly identified successor/proxy challengers. This does not restore historical Production identity.
- **D — not established from current GPT Library evidence:** Canonical Registry v3 Active original; historical Production runtime/trainer originals; exact 2026-11-17 R3 A/B original trainer/backtest/lock bytes; external TSA/WORM and actual Production deployment receipts.

### No execution scope repeated

This pass did not retrain models, replay Stage179/181, regenerate predictions, score any draw, change historical locks, rerun the Cleanroom Run #19 or R3 300-row audit, or promote any candidate to canonical/Production. It is a recovery and lineage reconciliation only.


Additional byte-content reconciliation: the 4,043-row parent candidate and its 4,043-row evidence-enriched child have identical values in all 34 parent columns; the child adds exactly six evidence columns (`official_evidence_status`, `official_evidence_source`, `official_evidence_url`, `official_evidence_checked_at`, `secondary_crosscheck_source`, `secondary_crosscheck_url`). This confirms the Stage173 evidence enrichment is append-only at the column level and did not rewrite any parent master values.
