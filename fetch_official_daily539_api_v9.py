#!/usr/bin/env python3
"""Taiwan Lottery Daily539 API evidence fetcher v9.

Uses the observed query contract from independent public crawler source:
  ?period=&month=YYYY-MM&pageNum=1&pageSize=50
The endpoint is a website-internal API, not a published/stable API contract.
Raw bytes and metadata are preserved. Nothing writes to or edits the master dataset.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sys, time
from datetime import datetime
from pathlib import Path
import requests

API = "https://api.taiwanlottery.com/TLCAPIWeB/Lottery/Daily539Result"
PAGE_SIZE = 50
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; 539-period-evidence-audit/9.0)",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.taiwanlottery.com/",
}

def norm_nums(value):
    vals = value[:5] if isinstance(value, list) else re.findall(r"\d+", str(value))[:5]
    try:
        nums = sorted(int(v) for v in vals)
        if len(nums) != 5 or len(set(nums)) != 5 or any(n < 1 or n > 39 for n in nums):
            return ""
        return " ".join(f"{n:02d}" for n in nums)
    except Exception:
        return ""

def parse_api(data):
    if not isinstance(data, dict) or not isinstance(data.get("content"), dict):
        raise ValueError("INVALID_TOP_LEVEL_SCHEMA")
    if "daily539Res" not in data["content"] or not isinstance(data["content"]["daily539Res"], list):
        raise ValueError("MISSING_OR_INVALID_content.daily539Res")
    rows=[]
    for i, r in enumerate(data["content"]["daily539Res"]):
        if not isinstance(r, dict):
            raise ValueError(f"ROW_{i}_NOT_OBJECT")
        date_raw = str(r.get("lotteryDate", ""))
        try: date = datetime.fromisoformat(date_raw.replace("Z", "+00:00")).date().isoformat()
        except Exception: date = date_raw[:10]
        period = str(r.get("period", ""))
        numbers = norm_nums(r.get("drawNumberAppear", []))
        if not date or not period or not numbers:
            raise ValueError(f"ROW_{i}_MISSING_DATE_PERIOD_OR_VALID_FIVE_NUMBERS")
        rows.append({"date":date,"period":period,"numbers":numbers,"raw":r})
    return rows

def request_month(session, month, timeout, retries, rawdir):
    params = {"period":"", "month":month, "pageNum":1, "pageSize":PAGE_SIZE}
    last_error=None; resp=None
    for attempt in range(retries + 1):
        try:
            resp=session.get(API, params=params, timeout=timeout)
            resp.raise_for_status()
            break
        except Exception as e:
            last_error=repr(e)
            if attempt < retries: time.sleep(1.0 * (attempt + 1))
    if resp is None:
        return None, {"month":month,"requested_url":requests.Request("GET",API,params=params).prepare().url,"error":last_error}
    body=resp.content
    stem=month.replace("-", "")
    body_file=rawdir/f"{stem}.response.bin"
    body_file.write_bytes(body)
    meta={"month":month,"url":resp.url,"captured_at_utc":datetime.utcnow().isoformat()+"Z","http_status":resp.status_code,"headers":dict(resp.headers),"content_length":len(body),"sha256":hashlib.sha256(body).hexdigest(),"body_file":str(body_file.name)}
    try:
        parsed=parse_api(resp.json())
        meta["schema_status"]="VALID_DAILY539_SCHEMA"
        meta["rows_parsed"]=len(parsed)
    except Exception as e:
        parsed=[]; meta["schema_status"]="INVALID_OR_UNEXPECTED_SCHEMA"; meta["parse_error"]=repr(e)
    (rawdir/f"{stem}.metadata.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
    return (meta, parsed), None

def selftest():
    fixture={"content":{"daily539Res":[{"period":"115000277","lotteryDate":"2026-11-16T00:00:00","drawNumberAppear":[11,21,22,35,37]}]}}
    rows=parse_api(fixture)
    assert rows[0]["date"]=="2026-11-16"
    assert rows[0]["period"]=="115000277"
    assert rows[0]["numbers"]=="11 21 22 35 37"
    for bad in ({}, {"content":{}}, {"content":{"daily539Res":None}}):
        try: parse_api(bad)
        except ValueError: pass
        else: raise AssertionError("invalid schema accepted")
    return {"parser_fixture":"PASS","invalid_schema_guards":"PASS","page_size":PAGE_SIZE,"query_parameters":["period","month","pageNum","pageSize"]}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--probe-month",default="2026-11")
    ap.add_argument("--probe-only",action="store_true")
    ap.add_argument("--input")
    ap.add_argument("--out",default="539_official_api_capture_v9")
    ap.add_argument("--timeout",type=int,default=15)
    ap.add_argument("--retries",type=int,default=0)
    ap.add_argument("--sleep",type=float,default=0.5)
    args=ap.parse_args()
    out=Path(args.out); rawdir=out/"raw_api_responses"; rawdir.mkdir(parents=True,exist_ok=True)
    summary={"version":"v9","endpoint":API,"endpoint_classification":"website-internal API; not a published stable API specification","selftest":selftest(),"probe_month":args.probe_month,"page_size":PAGE_SIZE,"captured_months":0,"parsed_rows":0,"api_matches":0,"status":"NOT_RUN"}
    session=requests.Session(); session.headers.update(HEADERS)
    result, failure=request_month(session,args.probe_month,args.timeout,args.retries,rawdir)
    if failure:
        summary.update({"status":"BLOCKED_NETWORK_OR_DNS","probe_failure":failure})
        (out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
        print(json.dumps(summary,ensure_ascii=False,indent=2)); return 2
    meta, rows=result
    summary.update({"status":"PROBE_CAPTURED" if meta["schema_status"]=="VALID_DAILY539_SCHEMA" else "CAPTURED_SCHEMA_UNVERIFIED","captured_months":1,"parsed_rows":len(rows),"capture_metadata":meta})
    if not args.probe_only:
        if not args.input: ap.error("--input is required unless --probe-only is set")
        with open(args.input,encoding="utf-8-sig",newline="") as f: candidates=list(csv.DictReader(f))
        target={}
        for r in candidates:
            if not r.get("official_issue_id") and r.get("period_canonical_not_official"):
                target[(r["draw_date"][:10],norm_nums(r.get("expected_numbers", "")))]=r
        index={(r["date"],r["numbers"]):r for r in rows}
        outrows=[]
        for (date,nums),candidate in sorted(target.items()):
            m=index.get((date,nums)); row=dict(candidate)
            row.update({"api_period_candidate":m["period"] if m else "","api_evidence_status":"MATCHED_OFFICIAL_API_RAW_RESPONSE" if m else "NO_EXACT_MATCH_IN_PROBE_MONTH"})
            outrows.append(row)
        fields=list(dict.fromkeys(k for r in outrows for k in r))
        with open(out/"candidate_period_api_reconciliation.csv","w",encoding="utf-8-sig",newline="") as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(outrows)
        summary.update({"input_rows":len(candidates),"candidate_rows_without_official_id":len(target),"api_matches":sum(r["api_evidence_status"]=="MATCHED_OFFICIAL_API_RAW_RESPONSE" for r in outrows),"warning":"Only probe_month was fetched. Do not infer coverage for other months or promote period IDs automatically."})
    (out/"summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return 0
if __name__=="__main__": sys.exit(main())
