#!/usr/bin/env python3
"""Fail-closed preflight for the 539 unique acceptance index.

This gate prevents known accepted work from being scheduled for replay and
requires genuinely new source locations for unresolved source-recovery work.
It does not grant Production authorization.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PASS_STATES = {"PASS_CLOSED", "PASS_RETAINED_NO_RERUN"}
VALID_STATES = {
    "PASS_CLOSED",
    "PASS_RETAINED_NO_RERUN",
    "OPEN_SOURCE_NOT_RECOVERED",
    "NOT_ACCESSIBLE_IN_THIS_RUN",
    "NEW_EVIDENCE_REQUIRED",
    "REGRESSION_CONFIRMED",
}


def load_index(path: Path) -> dict:
    if not path.is_file():
        raise ValueError(f"FAIL_CLOSED: acceptance index not found: {path}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"FAIL_CLOSED: index is unreadable/invalid JSON: {exc}") from exc
    if data.get("index_id") != "539-UNIQUE-ACCEPTANCE-INDEX-V1":
        raise ValueError("FAIL_CLOSED: unexpected index_id")
    if data.get("production_authorized") is not False:
        raise ValueError("FAIL_CLOSED: index must explicitly keep production_authorized=false")
    if data.get("policy", {}).get("execution_preflight_required") is not True:
        raise ValueError("FAIL_CLOSED: preflight policy missing")
    items = data.get("locked_items")
    if not isinstance(items, list) or not items:
        raise ValueError("FAIL_CLOSED: locked_items missing or empty")
    seen = set()
    for item in items:
        pid = item.get("problem_id")
        status = item.get("status")
        if not pid or pid in seen:
            raise ValueError(f"FAIL_CLOSED: missing or duplicate problem_id: {pid!r}")
        seen.add(pid)
        if status not in VALID_STATES:
            raise ValueError(f"FAIL_CLOSED: invalid status for {pid}: {status!r}")
        if not item.get("scope") or not item.get("evidence_pointer"):
            raise ValueError(f"FAIL_CLOSED: scope/evidence_pointer missing for {pid}")
    return data


def check_task(data: dict, problem_id: str, action: str, new_source_location: str | None) -> str:
    matches = [x for x in data["locked_items"] if x["problem_id"] == problem_id]
    if len(matches) != 1:
        raise ValueError(f"FAIL_CLOSED: problem_id must match exactly one index entry: {problem_id}")
    item = matches[0]
    status = item["status"]
    if action == "rerun" and status in PASS_STATES:
        raise ValueError(f"BLOCKED_DUPLICATE_RERUN: {problem_id} is {status}")
    if action == "source-search":
        if status != "OPEN_SOURCE_NOT_RECOVERED":
            raise ValueError(f"BLOCKED_INVALID_SOURCE_SEARCH: {problem_id} is {status}")
        if not new_source_location or not new_source_location.strip():
            raise ValueError("FAIL_CLOSED: source-search requires --new-source-location")
        old_pointer = item.get("evidence_pointer", "")
        if new_source_location.strip() == old_pointer:
            raise ValueError("BLOCKED_DUPLICATE_SOURCE_SEARCH: location matches existing evidence pointer")
    if action == "incremental" and status in PASS_STATES:
        return f"ALLOW_INCREMENTAL_ONLY: {problem_id}; retain historical acceptance and append only new-period evidence"
    return f"ALLOW_{action.upper()}: {problem_id} [{status}]"


def self_test(data: dict) -> None:
    ids = [x["problem_id"] for x in data["locked_items"]]
    assert len(ids) == len(set(ids)), "duplicate IDs"
    assert data["production_authorized"] is False
    # The accepted replay and audit entries must remain locked against reruns.
    for pid in ("CI-CLEANROOM-REPLAY-20261126-RUN19", "R3-API-AUDIT-300-20261126-RUN3"):
        item = next(x for x in data["locked_items"] if x["problem_id"] == pid)
        assert item["status"] in PASS_STATES
        try:
            check_task(data, pid, "rerun", None)
        except ValueError as exc:
            assert "BLOCKED_DUPLICATE_RERUN" in str(exc)
        else:
            raise AssertionError(f"{pid} rerun was not blocked")
    # An unresolved source search must provide a genuinely new locator.
    open_item = next(x for x in data["locked_items"] if x["status"] == "OPEN_SOURCE_NOT_RECOVERED")
    try:
        check_task(data, open_item["problem_id"], "source-search", None)
    except ValueError as exc:
        assert "requires --new-source-location" in str(exc)
    else:
        raise AssertionError("source search without a new locator was not blocked")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--index", default="governance/539_unique_acceptance_index_v1.json")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--problem-id")
    parser.add_argument("--action", choices=("inspect", "rerun", "source-search", "incremental"), default="inspect")
    parser.add_argument("--new-source-location")
    args = parser.parse_args()

    try:
        data = load_index(Path(args.index))
        if args.self_test:
            self_test(data)
            print(f"PASS: index valid; {len(data['locked_items'])} unique problem IDs; duplicate rerun guards passed")
            return 0
        if args.problem_id:
            print(check_task(data, args.problem_id, args.action, args.new_source_location))
        else:
            print(f"PASS_PREFLIGHT: {len(data['locked_items'])} indexed problem IDs; production_authorized=false")
        return 0
    except (ValueError, AssertionError) as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
