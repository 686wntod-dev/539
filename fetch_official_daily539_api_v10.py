#!/usr/bin/env python3
"""539 official-site API evidence capture v10; append-only evidence package only.
The endpoint is a website-internal API, not a published/stable API contract.
No master dataset or Registry file is modified.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sys, time
from datetime import datetime, timezone
from pathlib import Path
import requests

API = "https://api.taiwanlottery.com/TLCAPIWeB/Lottery/Daily539Result"
PAGE_SIZE = 50
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; 539-period-evidence-audit/10.0)",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.taiwanlottery.com/",
}

def norm_nums(value):
    if isinstance(value, list):
        if len(value) != 5: return ""
        vals = value
    else:
        raw = str(value).strip()
        if not re.fullmatch(r"\d{1,2}(?:[ ,，、]+\d{1,2}){4}", raw): return ""
        vals = re.split(r"[ ,，、]+", raw)
    try:
        nums = sorted(int(v) for v in vals)
        if len(nums) != 5 or len(set(nums)) != 5 or any(n < 1 or n > 39 for n in nums): return ""
        return " ".join(f"{n:02d}" for n in nums)
    except Exception: return ""

def parse_api(data):
    if not isinstance(data, dict) or data.get("rtCode") != 0 or not isinstance(data.get("content"), dict):
        raise ValueError("INVALID_TOP_LEVEL_SCHEMA_OR_NONZERO_RTCODE")
    content=data["content"]
    arr=content.get("daily539Res")
    total=content.get("totalSize")
    if not isinstance(arr, list) or not isinstance(total, int) or total < 0:
        raise ValueError("MISSING_OR_INVALID_DAILY539_ARRAY_OR_TOTALSIZE")
    if total != len(arr):
        raise ValueError(f"PAGINATION_REQUIRED_OR_TRUNCATED_RESPONSE: totalSize={total}, rows={len(arr)}")
    out=[]
    for i, r in enumerate(arr):
        if not isinstance(r, dict): raise ValueError(f"ROW_{i}_NOT_OBJECT")
        raw_date=str(r.get("lotteryDate", ""))
        try: date=datetime.fromisoformat(raw_date.replace("Z", "+00:00")).date().isoformat()
        except Exception: raise ValueError(f"ROW_{i}_INVALID_DATE")
        period=str(r.get("period", ""))
        if not re.fullmatch(r"\d{9}", period): raise ValueError(f"ROW_{i}_INVALID_PERIOD")
        nums=norm_nums(r.get("drawNumberAppear", []))
        if not nums: raise ValueError(f"ROW_{i}_INVALID_FIVE_NUMBERS")
        out.append({"date":date,"period":period,"numbers":nums})
    if len({x["date"] for x in out}) != len(out): raise ValueError("DUPLICATE_DATE_WITHIN_MONTH")
    if len({x["period"] for x in out}) != len(out): raise ValueError("DUPLICATE_PERIOD_WITHIN_MONTH")
    return out

def months_between(start, end):
    y,m=map(int,start.split('-')); ey,em=map(int,end.split('-'))
    while (y,m)<=(ey,em):
        yield f"{y:04d}-{m:02d}"
        m+=1
        if m==13: y,m=y+1,1

def selftest():
    fixture={"rtCode":0,"content":{"totalSize":1,"daily539Res":[{"period":115000277,"lotteryDate":"2026-11-16T00:00:00","drawNumberAppear":[11,21,22,35,37]}]}}
    assert parse_api(fixture)==[{"date":"2026-11-16","period":"115000277","numbers":"11 21 22 35 37"}]
    assert norm_nums([1,2,3,4,5,6]) == ""
    assert norm_nums("1,2,3,4,5,999") == ""
    invalid=[
        {},
        {"rtCode":1,"content":{"totalSize":1,"daily539Res":[]}},
        {"rtCode":0,"content":{}},
        {"rtCode":0,"content":{"totalSize":2,"daily539Res":[fixture["content"]["daily539Res"][0]]}},
        {"rtCode":0,"content":{"totalSize":1,"daily539Res":[{"period":115000277,"lotteryDate":"not-a-date","drawNumberAppear":[1,2,3,4,5]}]}},
        {"rtCode":0,"content":{"totalSize":1,"daily539Res":[{"period":115000277,"lotteryDate":"2026-11-16","drawNumberAppear":[1,2,3,4,5,6]}]}},
    ]
    for bad in invalid:
        try: parse_api(bad)
        except ValueError: pass
        else: raise AssertionError("invalid schema accepted")
    return "PASS"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--mode',choices=['probe','full'],default='probe')
    ap.add_argument('--probe-month',default='2026-11')
    ap.add_argument('--input',default='candidates_906.csv')
    ap.add_argument('--out',default='539_v10_capture')
    ap.add_argument('--timeout',type=int,default=20)
    ap.add_argument('--retries',type=int,default=2)
    ap.add_argument('--sleep',type=float,default=0.8)
    args=ap.parse_args()
    input_path=Path(args.input)
    if not input_path.is_file():
        raise SystemExit(f'BLOCKED_INPUT_FILE_MISSING: {args.input}')
    out=Path(args.out); rawdir=out/'raw_api_responses'; metadir=out/'metadata'
    rawdir.mkdir(parents=True,exist_ok=True); metadir.mkdir(parents=True,exist_ok=True)
    months=list(months_between('2024-01','2026-11')) if args.mode=='full' else [args.probe_month]
    summary={"version":"v10","endpoint":API,"endpoint_classification":"website-internal API; not a published/stable API contract","selftest":selftest(),"mode":args.mode,"requested_months":months,"captured_months":0,"failed_months":[],"schema_failed_months":[],"parsed_rows":0,"candidate_rows":0,"exact_date_and_five_number_matches":0,"status":"RUNNING"}
    all_draws=[]; errors=[]; session=requests.Session(); session.headers.update(HEADERS)
    for ix,month in enumerate(months):
        params={"period":"","month":month,"pageNum":1,"pageSize":PAGE_SIZE}
        req=requests.Request('GET',API,params=params).prepare().url
        resp=None; err=None
        for attempt in range(args.retries+1):
            try:
                resp=session.get(API,params=params,timeout=args.timeout); resp.raise_for_status(); break
            except Exception as e:
                err=repr(e)
                if attempt<args.retries: time.sleep(1.5*(attempt+1))
        if resp is None:
            failure={"month":month,"requested_url":req,"error":err}
            errors.append(failure); (metadir/f'{month.replace("-","")}.failure.json').write_text(json.dumps(failure,ensure_ascii=False,indent=2),encoding='utf-8')
            summary['failed_months'].append(month); continue
        body=resp.content; stem=month.replace('-',''); bodyname=f'{stem}.response.bin'; (rawdir/bodyname).write_bytes(body)
        meta={"month":month,"url":resp.url,"captured_at_utc":datetime.now(timezone.utc).isoformat(),"http_status":resp.status_code,"headers":dict(resp.headers),"content_length":len(body),"sha256":hashlib.sha256(body).hexdigest(),"body_file":bodyname}
        try:
            parsed=parse_api(resp.json()); meta['schema_status']='VALID_DAILY539_SCHEMA'; meta['rows_parsed']=len(parsed)
            for row in parsed: row['source_month']=month
            all_draws.extend(parsed); summary['parsed_rows']+=len(parsed)
        except Exception as e:
            parsed=[]; meta['schema_status']='INVALID_OR_UNEXPECTED_SCHEMA'; meta['parse_error']=repr(e); summary['schema_failed_months'].append(month)
        (metadir/f'{stem}.metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
        summary['captured_months']+=1
        if ix<len(months)-1: time.sleep(args.sleep)
    # Deduplicate API rows by date+period+numbers; preserve collisions for review.
    bykey={}
    for d in all_draws: bykey.setdefault((d['date'],d['period'],d['numbers']),d)
    draws=sorted(bykey.values(),key=lambda x:(x['date'],x['period']))
    with (out/'official_api_draw_rows.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['date','period','numbers','source_month']); w.writeheader(); w.writerows(draws)
    summary['unique_api_rows']=len(draws)
    if Path(args.input).exists():
        with open(args.input,encoding='utf-8-sig',newline='') as f: candidates=list(csv.DictReader(f))
        if not candidates:
            raise SystemExit('BLOCKED_CANDIDATE_INPUT_EMPTY')
        required={'draw_date','expected_numbers','official_issue_id'}
        if not required.issubset(set(candidates[0])):
            raise SystemExit('BLOCKED_CANDIDATE_INPUT_SCHEMA_INVALID')
        candidate_dates=[]
        for row_no, row in enumerate(candidates, start=2):
            date=str(row.get('draw_date',''))[:10]
            try:
                if datetime.fromisoformat(date).date().isoformat()!=date: raise ValueError()
            except Exception:
                raise SystemExit(f'BLOCKED_CANDIDATE_INVALID_DATE_ROW_{row_no}')
            if not norm_nums(row.get('expected_numbers','')):
                raise SystemExit(f'BLOCKED_CANDIDATE_INVALID_NUMBERS_ROW_{row_no}')
            candidate_dates.append(date)
        if len(set(candidate_dates)) != len(candidate_dates):
            raise SystemExit('BLOCKED_CANDIDATE_DUPLICATE_DATE')
        summary['candidate_input_rows_validated']=len(candidates)
        idx={(d['date'],d['numbers']):d for d in draws}
        candidate_by_date={str(c.get('draw_date',''))[:10]:c for c in candidates}
        reconciled=[]
        for c in candidates:
            if c.get('official_issue_id'): continue
            date=str(c.get('draw_date',''))[:10]; nums=norm_nums(c.get('expected_numbers',''))
            hit=idx.get((date,nums)); row=dict(c)
            row.update({'api_period_candidate':hit['period'] if hit else '', 'api_evidence_status':'MATCHED_OFFICIAL_API_RAW_RESPONSE_CANDIDATE' if hit else 'NO_EXACT_MATCH_IN_CAPTURED_MONTHS'})
            reconciled.append(row)
        fields=list(dict.fromkeys(k for r in reconciled for k in r))
        with (out/'candidate_period_api_reconciliation.csv').open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(reconciled)
        api_only=[]
        for d in draws:
            same_date=candidate_by_date.get(d['date'])
            candidate_nums=norm_nums(same_date.get('expected_numbers','')) if same_date else ''
            if candidate_nums==d['numbers']: continue
            api_only.append({'date':d['date'],'api_period_candidate':d['period'],'api_numbers':d['numbers'],'candidate_numbers':candidate_nums,'classification':'SAME_DATE_NUMBER_CONFLICT' if same_date else 'API_DATE_NOT_IN_CANDIDATE_FILE','source_month':d['source_month']})
        with (out/'api_only_and_conflict_rows.csv').open('w',encoding='utf-8-sig',newline='') as f:
            w=csv.DictWriter(f,fieldnames=['date','api_period_candidate','api_numbers','candidate_numbers','classification','source_month']); w.writeheader(); w.writerows(api_only)
        summary['candidate_rows']=len(reconciled)
        summary['exact_date_and_five_number_matches']=sum(r['api_evidence_status'].startswith('MATCHED_') for r in reconciled)
        summary['candidate_rows_without_exact_api_match']=sum(r['api_evidence_status']=='NO_EXACT_MATCH_IN_CAPTURED_MONTHS' for r in reconciled)
        summary['api_only_or_conflicting_rows']=len(api_only)
        summary['api_only_new_dates']=sum(r['classification']=='API_DATE_NOT_IN_CANDIDATE_FILE' for r in api_only)
        summary['same_date_number_conflicts']=sum(r['classification']=='SAME_DATE_NUMBER_CONFLICT' for r in api_only)
        summary['candidate_reconciliation_status']='REVIEW_REQUIRED_DIFFERENCES' if api_only or summary['candidate_rows_without_exact_api_match'] else 'EXACT_MATCH_COMPLETE'
        summary['warning']='API period values are website-internal response candidates only. Do not automatically promote period IDs to official master data; independently verify and use append-only evidence overlay.'
    if summary['captured_months'] != len(months):
        summary['status']='PARTIAL_CAPTURE' if summary['captured_months'] else 'BLOCKED_NETWORK_OR_DNS'
    elif summary['schema_failed_months']:
        summary['status']='CAPTURE_WITH_SCHEMA_ERRORS'
    else:
        summary['status']='CAPTURE_COMPLETE'
    summary['network_failures']=errors
    summary['reconciliation_status']=summary.get('candidate_reconciliation_status','NOT_RUN')
    (out/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return 0 if summary['status']=='CAPTURE_COMPLETE' and summary.get('candidate_reconciliation_status') in ('EXACT_MATCH_COMPLETE','REVIEW_REQUIRED_DIFFERENCES') else 2
if __name__=='__main__': sys.exit(main())
