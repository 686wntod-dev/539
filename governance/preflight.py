#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,sys
from pathlib import Path
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
def check(d,pid,action,location,ref,code_sha,requirements_sha,bundle_sha):
    x=item_for(d,pid); s=x["status"]
    if action=="rerun" and s in PASS: raise ValueError(f"BLOCKED_DUPLICATE_RERUN: {pid} is {s}; retain accepted evidence")
    if action=="replay-ci":
        if s not in PASS: raise ValueError(f"BLOCKED_INVALID_REPLAY_CI: {pid} is {s}")
        if not ref or not code_sha or not requirements_sha or not bundle_sha: raise ValueError("FAIL_CLOSED: replay-ci requires execution ref, validator blob SHA, pinned requirements blob SHA and bundle blob SHA")
        if code_sha==x.get("accepted_code_blob_sha") and requirements_sha==x.get("accepted_requirements_blob_sha") and bundle_sha==x.get("accepted_bundle_blob_sha"):
            raise ValueError(f"BLOCKED_DUPLICATE_REPLAY: {pid}; replay code and immutable bundle are unchanged")
        return f"ALLOW_NEW_REPLAY_CI: {pid}; code/bundle fingerprint changed at {ref}"
    if action=="source-search":
        if s!="OPEN_SOURCE_NOT_RECOVERED" or not location or not location.strip(): raise ValueError("FAIL_CLOSED: source-search requires open item and new source locator")
        if location.strip()==x.get("evidence_pointer",""): raise ValueError("BLOCKED_DUPLICATE_SOURCE_SEARCH")
    if action=="incremental" and s in PASS: return f"ALLOW_INCREMENTAL_ONLY: {pid}"
    return f"ALLOW_{action.upper()}: {pid} [{s}]"
def self_test(d):
    assert d["production_authorized"] is False
    tests=[("CI-CLEANROOM-REPLAY-20261126-RUN19","5cfd2ce9cb1867be55458aee32336bc0257ce26a","eb7ee81ab8f065f15585bf5c6a0fa6d57f0b25a3","9a3f037574e7bfbc380e9a5101328dfb01c4b3fc","a3b55848501d9674c622ab99e0225a711c99385a"),("R3-API-AUDIT-300-20261126-RUN3","c15044cb175372fe01427cb5d2a5ef3e36c8a481",None,None,None)]
    r3=item_for(d,"R3-API-AUDIT-300-20261126-RUN3")
    assert r3.get("accepted_scope")=={"start_date":"2025-12-04","end_date":"2026-11-14","rows":300,"bundle_sha256":"02fd9ff8b17f2eaa57d1b29dcec45a09f789d810b8a6aba7bf068666ebc7d17a","result":"300 accounted; 299 exact; 1 closed accepted snapshot exception; 0 unresolved"}
    assert r3.get("accepted_run_id")==45777143838
    for pid,ref,code,requirements,bundle in tests:
        try: check(d,pid,"rerun",None,None,None,None,None)
        except ValueError as e: assert "BLOCKED_DUPLICATE_RERUN" in str(e)
        else: raise AssertionError("duplicate rerun allowed")
        if code:
            try: check(d,pid,"replay-ci",None,ref,code,requirements,bundle)
            except ValueError as e: assert "BLOCKED_DUPLICATE_REPLAY" in str(e)
            else: raise AssertionError("unchanged replay fingerprint allowed")
            assert "ALLOW_NEW_REPLAY_CI" in check(d,pid,"replay-ci",None,"new-run","new-code","new-requirements","same-bundle")
    incident=item_for(d,"CI-CLEANROOM-REPLAY-20261126-RUN19").get("duplicate_trigger_incident",{})
    assert incident.get("run_id")==45804846897 and incident.get("artifact_id")==15108698201
    assert incident.get("artifact_digest")=="2b643635898b631f4bb4f4e686298acfd1edc37265fdff4378ebf2ff28fd1288"
    open_item=next(x for x in d["locked_items"] if x["status"]=="OPEN_SOURCE_NOT_RECOVERED")
    try: check(d,open_item["problem_id"],"source-search",None,None,None,None,None)
    except ValueError as e: assert "source-search requires" in str(e)
    else: raise AssertionError("source search without locator allowed")
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--index",default="governance/539_unique_acceptance_index_v1.json")
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--problem-id")
    p.add_argument("--action",choices=("inspect","rerun","source-search","incremental","replay-ci"),default="inspect")
    p.add_argument("--new-source-location"); p.add_argument("--execution-ref"); p.add_argument("--code-blob-sha"); p.add_argument("--requirements-blob-sha"); p.add_argument("--bundle-blob-sha")
    a=p.parse_args()
    try:
        d=load(Path(a.index))
        if a.self_test: self_test(d); print(f"PASS: {len(d['locked_items'])} unique IDs; duplicate rerun and replay-fingerprint guards passed"); return 0
        if a.problem_id: print(check(d,a.problem_id,a.action,a.new_source_location,a.execution_ref,a.code_blob_sha,a.requirements_blob_sha,a.bundle_blob_sha))
        else: print(f"PASS_PREFLIGHT: {len(d['locked_items'])} unique IDs; production_authorized=false")
        return 0
    except (ValueError,AssertionError) as e: print(str(e),file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())
