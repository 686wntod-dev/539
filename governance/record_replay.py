#!/usr/bin/env python3
from __future__ import annotations
import argparse
from datetime import datetime,timezone
from replay_ledger import append_record
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--ledger",default="governance/replay_fingerprint_ledger.jsonl")
    p.add_argument("--run-id",type=int,required=True); p.add_argument("--run-attempt",type=int,required=True)
    p.add_argument("--execution-ref",required=True); p.add_argument("--validator-blob-sha",required=True)
    p.add_argument("--requirements-blob-sha",required=True); p.add_argument("--bundle-blob-sha",required=True)
    a=p.parse_args()
    r={"schema_version":"1","run_id":a.run_id,"run_attempt":a.run_attempt,"execution_ref":a.execution_ref,
       "validator_blob_sha":a.validator_blob_sha,"requirements_blob_sha":a.requirements_blob_sha,
       "bundle_blob_sha":a.bundle_blob_sha,"result":"SUCCESS","recorded_at_utc":datetime.now(timezone.utc).isoformat()}
    n=append_record(a.ledger,r); print(f"PASS_APPEND_ONLY: run={a.run_id} attempt={a.run_attempt} ledger_entries={n}")
if __name__=="__main__": main()
