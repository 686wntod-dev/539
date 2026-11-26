#!/usr/bin/env python3
"""Fail-closed preflight for the 539 unique acceptance index."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
PASS_STATES = {"PASS_CLOSED", "PASS_RETAINED_NO_RERUN"}
VALID_STATES = {"PASS_CLOSED","PASS_RETAINED_NO_RERUN","OPEN_SOURCE_NOT_RECOVERED","NOT_ACCESSIBLE_IN_THIS_RUN","NEW_EVIDENCE_REQUIRED","REGRESSION_CONFIRMED"}
def load_index(path: Path) -> dict:
    if not path.is_file(): raise ValueError(f"FAIL_CLOSED: acceptance index not found: {path}")
    try: data=json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc: raise ValueError(f"FAIL_CLOSED: index invalid JSON: {exc}") from exc
    if data.get("index_id") != "539-UNIQUE-ACCEPTANCE-INDEX-V1": raise ValueError("FAIL_CLOSED: unexpected index_id")
    if data.get("production_authorized") is not False: raise ValueError("FAIL_CLOSED: production_authorized must be false")
    if data.get("policy",{}).get("execution_preflight_required") is not True: raise ValueError("FAIL_CLOSED: preflight policy missing")
    items=data.get("locked_items")
    if not isinstance(items,list) or not items: raise ValueError("FAIL_CLOSED: locked_items missing")
    seen=set()
    for item in items:
        pid=item.get("problem_id")
        if not pid or pid in seen: raise ValueError(f"FAIL_CLOSED: missing/duplicate problem_id: {pid!r}")
        seen.add(pid)
        if item.get("status") not in VALID_STATES: raise ValueError(f"FAIL_CLOSED: invalid status for {pid}")
        if not item.get("scope") or not item.get("evidence_pointer"): raise ValueError(f"FAIL_CLOSED: scope/evidence_pointer missing for {pid}")
    return data
def check_task(data:dict, problem_id:str, action:str, new_source_location:str|None, execution_ref:str|None)->str:
    matches=[x for x in data["locked_items"] if x["problem_id"]==problem_id]
    if len(matches)!=1: raise ValueError(f"FAIL_CLOSED: problem_id must match exactly one entry: {problem_id}")
    item=matches[0]; status=item["status"]
    if action=="rerun" and status in PASS_STATES:
        raise ValueError(f"BLOCKED_DUPLICATE_RERUN: {problem_id} is {status}; retained evidence must be reused")
    if action=="replay-ci":
        if status not in PASS_STATES: raise ValueError(f"BLOCKED_INVALID_REPLAY_CI: {problem_id} is {status}")
        if not execution_ref: raise ValueError("FAIL_CLOSED: replay-ci requires --execution-ref")
        if execution_ref in item.get("accepted_execution_refs",[]):
            raise ValueError(f"BLOCKED_DUPLICATE_REPLAY: {problem_id} execution ref {execution_ref} already accepted")
        return f"ALLOW_NEW_REPLAY_CI: {problem_id}; new execution ref {execution_ref}"
    if action=="source-search":
        if status!="OPEN_SOURCE_NOT_RECOVERED": raise ValueError(f"BLOCKED_INVALID_SOURCE_SEARCH: {problem_id} is {status}")
        if not new_source_location or not new_source_location.strip(): raise ValueError("FAIL_CLOSED: source-search requires --new-source-location")
        if new_source_location.strip()==item.get("evidence_pointer",""): raise ValueError("BLOCKED_DUPLICATE_SOURCE_SEARCH: same evidence pointer")
    if action=="incremental" and status in PASS_STATES: return f"ALLOW_INCREMENTAL_ONLY: {problem_id}; append new-period evidence only"
    return f"ALLOW_{action.upper()}: {problem_id} [{status}]"
def self_test(data:dict)->None:
    ids=[x["problem_id"] for x in data["locked_items"]]
    assert len(ids)==len(set(ids)) and data["production_authorized"] is False
    cases=[("CI-CLEANROOM-REPLAY-20261126-RUN19","5cfd2ce9cb1867be55458aee32336bc0257ce26a"),("R3-API-AUDIT-300-20261126-RUN3","c15044cb175372fe01427cb5d2a5ef3e36c8a481")]
    for pid,ref in cases:
        try: check_task(data,pid,"rerun",None,None)
        except ValueError as e: assert "BLOCKED_DUPLICATE_RERUN" in str(e)
        else: raise AssertionError(f"{pid} duplicate rerun was not blocked")
        try: check_task(data,pid,"replay-ci",None,ref)
        except ValueError as e: assert "BLOCKED_DUPLICATE_REPLAY" in str(e)
        else: raise AssertionError(f"{pid} accepted execution ref was not blocked")
        assert "ALLOW_NEW_REPLAY_CI" in check_task(data,pid,"replay-ci",None,"new-commit-for-test")
    open_item=next(x for x in data["locked_items"] if x["status"]=="OPEN_SOURCE_NOT_RECOVERED")
    try: check_task(data,open_item["problem_id"],"source-search",None,None)
    except ValueError as e: assert "requires --new-source-location" in str(e)
    else: raise AssertionError("source search without locator was not blocked")
def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument("--index",default="governance/539_unique_acceptance_index_v1.json")
    p.add_argument("--self-test",action="store_true")
    p.add_argument("--problem-id")
    p.add_argument("--action",choices=("inspect","rerun","source-search","incremental","replay-ci"),default="inspect")
    p.add_argument("--new-source-location")
    p.add_argument("--execution-ref")
    a=p.parse_args()
    try:
        d=load_index(Path(a.index))
        if a.self_test: self_test(d); print(f"PASS: {len(d['locked_items'])} unique IDs; duplicate rerun/replay guards passed"); return 0
        if a.problem_id: print(check_task(d,a.problem_id,a.action,a.new_source_location,a.execution_ref))
        else: print(f"PASS_PREFLIGHT: {len(d['locked_items'])} indexed IDs; production_authorized=false")
        return 0
    except (ValueError,AssertionError) as e: print(str(e),file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())
