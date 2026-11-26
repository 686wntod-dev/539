#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys,tempfile
from pathlib import Path
from replay_ledger import append_record,fingerprint,load_ledger
PASS={"PASS_CLOSED","PASS_RETAINED_NO_RERUN"}
VALID=PASS|{"OPEN_SOURCE_NOT_RECOVERED","NOT_ACCESSIBLE_IN_THIS_RUN","NEW_EVIDENCE_REQUIRED","REGRESSION_CONFIRMED"}
def load(p):
    if not p.is_file(): raise ValueError(f"FAIL_CLOSED: index missing: {p}")
    d=json.loads(p.read_text(encoding="utf-8"))
    if d.get("index_id")!="539-UNIQUE-ACCEPTANCE-INDEX-V1" or d.get("production_authorized") is not False or d.get("policy",{}).get("execution_preflight_required") is not True: raise ValueError("FAIL_CLOSED: index identity/policy invalid")
    seen=set()
    for x in d.get("locked_items",[]):
        pid=x.get("problem_id")
        if not pid or pid in seen or x.get("status") not in VALID or not x.get("scope") or not x.get("evidence_pointer"): raise ValueError(f"FAIL_CLOSED: invalid/duplicate index item {pid!r}")
        seen.add(pid)
    if not seen: raise ValueError("FAIL_CLOSED: empty index")
    return d
def item_for(d,pid):
    m=[x for x in d["locked_items"] if x["problem_id"]==pid]
    if len(m)!=1: raise ValueError(f"FAIL_CLOSED: problem_id must match exactly one entry: {pid}")
    return m[0]
def check(d,pid,action,location,ref,code_sha,requirements_sha,bundle_sha,ledger):
    x=item_for(d,pid); s=x["status"]
    if action=="rerun" and s in PASS: raise ValueError(f"BLOCKED_DUPLICATE_RERUN: {pid} is {s}; retain accepted evidence")
    if action=="replay-ci":
        if s not in PASS: raise ValueError(f"BLOCKED_INVALID_REPLAY_CI: {pid} is {s}")
        if not all((ref,code_sha,requirements_sha,bundle_sha)): raise ValueError("FAIL_CLOSED: replay-ci requires execution ref and all three blob fingerprints")
        if (code_sha,requirements_sha,bundle_sha) in {fingerprint(r) for r in ledger}: raise ValueError(f"BLOCKED_DUPLICATE_REPLAY: {pid}; fingerprint already exists in append-only ledger")
        return f"ALLOW_NEW_REPLAY_CI: {pid}; fingerprint absent from accepted ledger at {ref}"
    if action=="source-search":
        if s!="OPEN_SOURCE_NOT_RECOVERED" or not location or not location.strip(): raise ValueError("FAIL_CLOSED: source-search requires open item and new source locator")
        if location.strip()==x.get("evidence_pointer",""): raise ValueError("BLOCKED_DUPLICATE_SOURCE_SEARCH")
    if action=="incremental" and s in PASS: return f"ALLOW_INCREMENTAL_ONLY: {pid}"
    return f"ALLOW_{action.upper()}: {pid} [{s}]"
def self_test(d,ledger):
    assert d["production_authorized"] is False
    r19=item_for(d,"CI-CLEANROOM-REPLAY-20261126-RUN19")
    assert len(ledger)==1 and ledger[0]["run_id"]==45777147538
    assert fingerprint(ledger[0])==(r19["accepted_code_blob_sha"],r19["accepted_requirements_blob_sha"],r19["accepted_bundle_blob_sha"])
    r3=item_for(d,"R3-API-AUDIT-300-20261126-RUN3")
    assert r3.get("accepted_run_id")==45777143838
    assert r3.get("accepted_scope",{}).get("rows")==300
    try: check(d,"CI-CLEANROOM-REPLAY-20261126-RUN19","replay-ci",None,"5cfd2ce9cb1867be55458aee32336bc0257ce26a",*fingerprint(ledger[0]),ledger)
    except ValueError as e: assert "BLOCKED_DUPLICATE_REPLAY" in str(e)
    else: raise AssertionError("accepted fingerprint replay allowed")
    assert "ALLOW_NEW_REPLAY_CI" in check(d,"CI-CLEANROOM-REPLAY-20261126-RUN19","replay-ci",None,"4"*40,"1"*40,"2"*40,"3"*40,ledger)
    try: check(d,"R3-API-AUDIT-300-20261126-RUN3","rerun",None,None,None,None,None,ledger)
    except ValueError as e: assert "BLOCKED_DUPLICATE_RERUN" in str(e)
    else: raise AssertionError("R3 rerun allowed")
    with tempfile.TemporaryDirectory() as td:
        p=Path(td)/"ledger.jsonl"; p.write_text(Path("governance/replay_fingerprint_ledger.jsonl").read_text(encoding="utf-8"),encoding="utf-8")
        fresh={"schema_version":"1","run_id":99999999999,"run_attempt":1,"execution_ref":"4"*40,"validator_blob_sha":"5"*40,"requirements_blob_sha":"6"*40,"bundle_blob_sha":"7"*40,"result":"SUCCESS","recorded_at_utc":"2026-11-26T00:00:00Z"}
        assert append_record(p,fresh)==2
        try: append_record(p,fresh)
        except ValueError as e: assert "BLOCKED_DUPLICATE_REPLAY" in str(e)
        else: raise AssertionError("duplicate append accepted")
        assert len(load_ledger(p))==2
    incident=r19.get("duplicate_trigger_incident",{})
    assert incident.get("run_id")==45804846897 and incident.get("artifact_id")==15108698201
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--index",default="governance/539_unique_acceptance_index_v1.json")
    p.add_argument("--ledger",default="governance/replay_fingerprint_ledger.jsonl")
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--problem-id")
    p.add_argument("--action",choices=("inspect","rerun","source-search","incremental","replay-ci"),default="inspect")
    p.add_argument("--new-source-location"); p.add_argument("--execution-ref"); p.add_argument("--code-blob-sha"); p.add_argument("--requirements-blob-sha"); p.add_argument("--bundle-blob-sha")
    a=p.parse_args()
    try:
        d=load(Path(a.index)); ledger=load_ledger(a.ledger)
        if a.self_test: self_test(d,ledger); print(f"PASS: {len(d['locked_items'])} unique IDs; {len(ledger)} accepted replay fingerprints; append-only duplicate guards passed"); return 0
        if a.problem_id: print(check(d,a.problem_id,a.action,a.new_source_location,a.execution_ref,a.code_blob_sha,a.requirements_blob_sha,a.bundle_blob_sha,ledger))
        else: print(f"PASS_PREFLIGHT: {len(d['locked_items'])} unique IDs; {len(ledger)} accepted replay fingerprints; production_authorized=false")
        return 0
    except (ValueError,AssertionError) as e: print(str(e),file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())
