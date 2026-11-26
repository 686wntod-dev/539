#!/usr/bin/env python3
from __future__ import annotations
import json,re
from pathlib import Path
SHA=re.compile(r"^[0-9a-f]{40}$")
REQUIRED=("run_id","run_attempt","execution_ref","validator_blob_sha","requirements_blob_sha","bundle_blob_sha","result","recorded_at_utc")
def fingerprint(r): return tuple(r[k] for k in ("validator_blob_sha","requirements_blob_sha","bundle_blob_sha"))
def validate_record(r,line_no):
    if not isinstance(r,dict) or r.get("schema_version")!="1": raise ValueError(f"FAIL_CLOSED: invalid schema at ledger line {line_no}")
    if any(k not in r for k in REQUIRED): raise ValueError(f"FAIL_CLOSED: incomplete ledger line {line_no}")
    if not isinstance(r["run_id"],int) or r["run_id"]<=0 or not isinstance(r["run_attempt"],int) or r["run_attempt"]<=0: raise ValueError(f"FAIL_CLOSED: invalid run identity at line {line_no}")
    if r["result"]!="SUCCESS" or not r["recorded_at_utc"]: raise ValueError(f"FAIL_CLOSED: only successful timestamped runs may be recorded (line {line_no})")
    for k in ("execution_ref","validator_blob_sha","requirements_blob_sha","bundle_blob_sha"):
        if not isinstance(r[k],str) or not SHA.fullmatch(r[k]): raise ValueError(f"FAIL_CLOSED: invalid {k} at line {line_no}")
def load_ledger(path):
    p=Path(path)
    if not p.is_file(): raise ValueError(f"FAIL_CLOSED: replay fingerprint ledger missing: {p}")
    rows=[]; fps=set(); runs=set()
    for n,line in enumerate(p.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): raise ValueError(f"FAIL_CLOSED: blank ledger line {n}")
        try: r=json.loads(line)
        except Exception as e: raise ValueError(f"FAIL_CLOSED: invalid JSON at line {n}: {e}")
        validate_record(r,n); fp=fingerprint(r); run=(r["run_id"],r["run_attempt"])
        if fp in fps: raise ValueError(f"FAIL_CLOSED: duplicate fingerprint at ledger line {n}")
        if run in runs: raise ValueError(f"FAIL_CLOSED: duplicate run identity at ledger line {n}")
        fps.add(fp); runs.add(run); rows.append(r)
    if not rows: raise ValueError("FAIL_CLOSED: replay fingerprint ledger is empty")
    return rows
def append_record(path,record):
    rows=load_ledger(path); validate_record(record,"new")
    if fingerprint(record) in {fingerprint(x) for x in rows}: raise ValueError("BLOCKED_DUPLICATE_REPLAY: fingerprint already recorded")
    run=(record["run_id"],record["run_attempt"])
    if run in {(x["run_id"],x["run_attempt"]) for x in rows}: raise ValueError("BLOCKED_DUPLICATE_RUN_IDENTITY: run already recorded")
    with Path(path).open("a",encoding="utf-8",newline="\n") as f: f.write(json.dumps(record,ensure_ascii=False,sort_keys=True,separators=(",",":"))+"\n")
    return len(rows)+1
