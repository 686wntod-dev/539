#!/usr/bin/env python3
"""Compare the retained 300-draw R3 evaluation window with Taiwan Lottery's public Daily539Result API.
Read-only: never edits the source master or infers official periods.
"""
import csv, hashlib, json, os, sys, urllib.parse, urllib.request, zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "replay_bundle.zip"
OUT = ROOT / "official_source_audit"
OUT.mkdir(parents=True, exist_ok=True)
EXPECTED_BUNDLE_SHA = "02fd9ff8b17f2eaa57d1b29dcec45a09f789d810b8a6aba7bf068666ebc7d17a"
START_DATE, END_DATE = "2025-12-04", "2026-11-14"
API = "https://api.taiwanlottery.com/TLCAPIWeB/Lottery/Daily539Result"

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024), b""): h.update(b)
    return h.hexdigest()

def norm_nums(vals):
    return tuple(sorted(int(x) for x in vals[:5]))

if not BUNDLE.exists():
    raise SystemExit(f"FAIL_CLOSED: missing {BUNDLE}")
bundle_sha=sha256(BUNDLE)
if bundle_sha != EXPECTED_BUNDLE_SHA:
    raise SystemExit(f"FAIL_CLOSED: bundle SHA mismatch {bundle_sha}")

with zipfile.ZipFile(BUNDLE) as z:
    candidates=[n for n in z.namelist() if n.endswith("data/shadow_master_4036.csv")]
    if len(candidates)!=1: raise SystemExit(f"FAIL_CLOSED: expected one shadow master, found {candidates}")
    raw=z.read(candidates[0]).decode("utf-8-sig").splitlines()
    rows=list(csv.DictReader(raw))

targets=[]
for r in rows:
    d=(r.get("開獎日期") or "").strip()[:10]
    if START_DATE <= d <= END_DATE:
        nums=tuple(sorted(int(r[f"號碼{i}"]) for i in range(1,6)))
        targets.append({"date":d,"inferred_period":str(r.get("period_inferred") or r.get("期別_補齊推定") or "").replace(".0",""),"nums":nums,"source":r.get("資料來源",""),"original_period":str(r.get("期別") or "").replace(".0",""),"period_is_official_original":str(r.get("period_is_official_original","")).lower()=="true"})
targets.sort(key=lambda x:x["date"])
if len(targets)!=300: raise SystemExit(f"FAIL_CLOSED: expected 300 target rows, got {len(targets)}")

months=sorted({x["date"][:7] for x in targets})
official={}
request_log=[]
for month in months:
    params=urllib.parse.urlencode({"month":month,"pageNum":1,"pageSize":50})
    url=f"{API}?period&{params}"
    req=urllib.request.Request(url,headers={"User-Agent":"539-R3-Official-Source-Audit/1.0","Accept":"application/json"})
    with urllib.request.urlopen(req,timeout=30) as resp:
        payload=json.loads(resp.read().decode("utf-8"))
        status=resp.status
    content=payload.get("content") or {}
    draws=content.get("daily539Res") or []
    request_log.append({"month":month,"url":url,"http_status":status,"returned":len(draws),"totalSize":content.get("totalSize")})
    for x in draws:
        date=(x.get("lotteryDate") or "")[:10]
        period=str(x.get("period") or "")
        nums=norm_nums(x.get("drawNumberSize") or x.get("drawNumberAppear") or [])
        if date and len(nums)==5:
            official[date]={"period":period,"nums":nums}

results=[]
for x in targets:
    o=official.get(x["date"])
    if o is None:
        status="NOT_RETURNED_BY_OFFICIAL_API"
        api_period=""; nums_match=False; period_match=False
    else:
        api_period=o["period"]
        nums_match=(o["nums"]==x["nums"])
        period_match=(api_period==x["inferred_period"])
        status="PASS_EXACT_DATE_PERIOD_NUMBERS" if nums_match and period_match else ("FAIL_NUMBERS_MISMATCH" if not nums_match else "PERIOD_MISMATCH")
    results.append({
      "date":x["date"],"candidate_inferred_period":x["inferred_period"],"official_api_period":api_period,
      "candidate_numbers":"-".join(f"{n:02d}" for n in x["nums"]),
      "official_api_numbers":"-".join(f"{n:02d}" for n in official[x["date"]]["nums"]) if x["date"] in official else "",
      "numbers_match":nums_match,"period_match":period_match,
      "original_period_field_present":bool(x["original_period"]),
      "period_is_official_original_in_master":x["period_is_official_original"],
      "master_source_label":x["source"],"status":status
    })

counts=defaultdict(int)
for r in results: counts[r["status"]]+=1
summary={
 "audit":"R3_300_DRAW_OFFICIAL_API_RECONCILIATION",
 "source":"Taiwan Lottery Daily539Result API",
 "api_endpoint":API,
 "window":{"start":START_DATE,"end":END_DATE,"rows":len(targets)},
 "bundle_sha256":bundle_sha,
 "target_master_member":candidates[0],
 "official_api_month_requests":request_log,
 "counts":dict(counts),
 "all_300_exact":len(results)==300 and all(r["status"]=="PASS_EXACT_DATE_PERIOD_NUMBERS" for r in results),
 "fail_closed_note":"No period or number is filled from third-party sources; unavailable API rows remain unresolved.",
}
with (OUT/"r3_300_official_api_reconciliation.csv").open("w",newline="",encoding="utf-8-sig") as f:
    w=csv.DictWriter(f,fieldnames=list(results[0].keys())); w.writeheader(); w.writerows(results)
with (OUT/"r3_300_official_api_reconciliation.json").open("w",encoding="utf-8") as f: json.dump({"summary":summary,"rows":results},f,ensure_ascii=False,indent=2)
print(json.dumps(summary,ensure_ascii=False,indent=2))
if not summary["all_300_exact"]:
    sys.exit(2)
