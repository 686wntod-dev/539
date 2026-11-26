#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, sys, importlib.util, os
import numpy as np
import pandas as pd
import joblib

ROOT = Path(os.environ.get("539_REPLAY_BUNDLE_ROOT", Path(__file__).resolve().parent)).resolve()

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

def check_master(path, expected_sha, expected_rows, cutoff):
    assert sha(path) == expected_sha, (path, sha(path), expected_sha)
    df = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
    assert len(df) == expected_rows, (len(df), expected_rows)
    assert "開獎日期" in df.columns and all(f"號碼{i}" in df.columns for i in range(1, 6))
    dates = pd.to_datetime(df["開獎日期"], errors="raise")
    assert dates.is_monotonic_increasing and dates.is_unique
    assert str(dates.iloc[-1].date()) == cutoff
    nums = df[[f"號碼{i}" for i in range(1, 6)]].apply(pd.to_numeric, errors="raise").to_numpy(dtype=int)
    assert np.all((nums >= 1) & (nums <= 39)) and all(len(set(row)) == 5 for row in nums)
    return df, nums

def formal7():
    lock = json.loads((ROOT / "formal7/lock_2026-11-17.json").read_text(encoding="utf-8"))
    master = ROOT / "data/formal7_master_4037.csv"
    artifacts = ROOT / "formal7/artifacts"
    df, nums = check_master(master, lock["master_sha256"], 4037, "2026-11-16")
    assert lock["master_rows"] == 4037 and lock["data_cutoff"] == "2026-11-16"
    assert sha(ROOT / "formal7/runtime.py") == "c6d01f06a4cc51b207a9ad3bc374c79c506f0df09a64a36443976504b1bf9b67"
    assert sha(ROOT / "formal7/schema.json") == lock["feature_schemas_sha256"]
    for rel, expected in lock["artifacts_sha256"].items():
        assert sha(artifacts / rel) == expected, (rel, sha(artifacts / rel), expected)
    rt = load_module(ROOT / "formal7/runtime.py", "formal7_runtime")
    out = ROOT / "validation_output/formal7"
    out.mkdir(parents=True, exist_ok=True)
    result = rt.run(master, artifacts, out)
    assert len(result["models"]) == 7
    idmap = {"AI-3-Full4036-CR1": "AI-3-Full4037-CR1"}
    rows = []
    for model_id, expected in lock["models"].items():
        got = result["models"][idmap.get(model_id, model_id)]
        for field in ["A", "B", "pool", "ranked_numbers"]:
            assert got[field] == expected[field], (model_id, field, got[field], expected[field])
        assert len(got["pool"]) == 10 and len(set(got["pool"])) == 10
        assert len(got["ranked_numbers"]) == 39 and len(set(got["ranked_numbers"])) == 39
        rows.append({"model_id": model_id, "A_B_pool_rank": "PASS", "replay_exact": True})
    nums0 = rt.make_y(nums)
    dates = pd.to_datetime(df["開獎日期"])
    for t in [200, 1000, 2000, len(nums) - 1]:
        altered = nums0.copy()
        altered[t:] = np.roll(altered[t:], 7, axis=1)
        assert np.array_equal(rt.features18(nums0, t), rt.features18(altered, t))
        assert np.array_equal(rt.features19(nums0, t), rt.features19(altered, t))
        assert np.array_equal(rt.ai3_scores(nums0[:t], dates.iloc[:t]), rt.ai3_scores(altered[:t], dates.iloc[:t]))
    assert abs(result["models"]["AI-2-19F-CR1"]["probability_sum"] - 5.0) < 1e-9
    return {
        "models": rows, "count": 7, "master_sha256": sha(master),
        "runtime_sha256": sha(ROOT / "formal7/runtime.py"),
        "artifact_hashes": "PASS_8_OF_8", "schema_hash": "PASS",
        "prefix_invariance": "PASS_4_CUTOFFS", "probability_sum": "PASS",
        "status": "PASS_CLEANROOM_REPLAY_NOT_PRODUCTION"
    }

def shadow4():
    master = ROOT / "data/shadow_master_4036.csv"
    df, nums = check_master(master, "c857fe7ea8995bb28f9d5d168da513792cb21a3334d18753e96dd5482c1f6a06", 4036, "2026-11-14")
    src = ROOT / "shadow4/source/reproduce_shadow_v1.py"
    assert sha(src) == "28bb5907e0c96ac90d8230d59dc6e6d67110d6fbf7737f4c4e3664182f4f2cb8"
    module = load_module(src, "shadow_engine")
    Y = np.zeros((len(nums), 39), dtype=np.uint8)
    for i, row in enumerate(nums):
        Y[i, row - 1] = 1
    mapping = {
        "V1_Full4034_Shadow_v1": "V1", "V2_Full4034_Shadow_v1": "V2",
        "R3_Full4034_Shadow_v1": "R3", "MIX_Full4034_Shadow_v1": "MIX"
    }
    rows = []
    for model_id, version in mapping.items():
        lock = json.loads((ROOT / f"shadow4/locks/{model_id}_2026-11-16_prediction.json").read_text(encoding="utf-8"))
        scores = module.score_at(Y, len(Y), version)
        rank = (np.argsort(-scores, kind="stable") + 1).tolist()
        assert rank == [int(x) for x in lock["ranked"]]
        assert rank[:5] == [int(x) for x in lock["A"]]
        assert rank[5:10] == [int(x) for x in lock["B"]]
        assert rank[:10] == [int(x) for x in lock["pool"]]
        rows.append({"model_id": model_id, "rank_A_B_pool": "PASS", "status": "SHADOW_ONLY"})
    return {"models": rows, "count": 4, "master_sha256": sha(master), "source_sha256": sha(src), "status": "PASS_SHADOW_LOCK_REPLAY"}

def r3_hgb():
    master = ROOT / "data/shadow_master_4036.csv"
    df, nums = check_master(master, "c857fe7ea8995bb28f9d5d168da513792cb21a3334d18753e96dd5482c1f6a06", 4036, "2026-11-14")
    base = ROOT / "r3_hgb"
    lock = json.loads((base / "R3_HGB_NoPP_2026-11-16_prediction_lock.json").read_text(encoding="utf-8"))
    assert lock["master_sha256"] == sha(master)
    assert sha(base / "R3_HGB_NoPP_2026-11-16_model.joblib") == "80ea63669eabe924708b16467bd6faff466b6ba6c360e283c4e25f5ddc0b92b7"
    schema = json.loads((base / "R3_HGB_NoPP_2026-11-16_feature_schema.json").read_text(encoding="utf-8"))
    assert schema["sha256"] == lock["feature_schema_sha256"] and len(schema["features"]) == 32
    N = len(df)
    D = np.zeros((N, 39), dtype=np.int8)
    for j in range(1, 6):
        D[np.arange(N), nums[:, j - 1] - 1] = 1
    cum = np.vstack([np.zeros((1, 39), dtype=np.int32), np.cumsum(D, axis=0)])
    pc = np.zeros((N + 1, 39, 39), dtype=np.int32)
    for i in range(N):
        pc[i + 1] = pc[i] + np.outer(D[i], D[i])
    last = np.full(39, -1000, dtype=np.int32)
    for t in range(200, N + 1):
        if t > 0:
            last[np.where(D[t - 1] == 1)[0]] = t - 1
    features = [np.arange(1, 40, dtype=np.float32)]
    for w in [5, 10, 20, 50, 100, 200]:
        features.append((cum[N] - cum[max(0, N - w)]).astype(np.float32))
    features.append(np.minimum(N - last, 500).astype(np.float32))
    for w in [1, 2, 3, 5]:
        features.append((cum[N] - cum[max(0, N - w)]).astype(np.float32))
    for delta in [-2, -1, 1, 2]:
        src = np.arange(39) + delta
        ok = (src >= 0) & (src < 39)
        for w in [20, 50]:
            z = np.zeros(39, dtype=np.float32)
            z[ok] = (cum[N] - cum[max(0, N - w)])[src[ok]]
            features.append(z)
    f10 = (cum[N] - cum[N - 10]).astype(np.float32)
    f50 = (cum[N] - cum[N - 50]).astype(np.float32)
    f20 = (cum[N] - cum[N - 20]).astype(np.float32)
    f100 = (cum[N] - cum[N - 100]).astype(np.float32)
    features.extend([f10 - f50 / 5, f20 - f100 / 5, D[N - 1].astype(np.float32)])
    for k in [1, 2, 3]:
        recent = D[N - k:N].max(axis=0).astype(np.int32)
        for w in [20, 50, 100]:
            features.append(((pc[N] - pc[N - w]) @ recent).astype(np.float32))
    X = np.column_stack(features)
    assert X.shape == (39, 32)
    model = joblib.load(base / "R3_HGB_NoPP_2026-11-16_model.joblib")
    probabilities = model.predict_proba(X)[:, 1]
    order = np.argsort(probabilities, kind="mergesort")
    excluded = (order[:10] + 1).tolist()
    assert excluded == lock["excluded_10"], (excluded, lock["excluded_10"])
    lock_scores = np.array([lock["scores"][f"{i + 1:02d}"] for i in range(39)])
    assert float(np.max(np.abs(probabilities - lock_scores))) == 0.0
    return {
        "model_id": "R3-HGB-NoPP-Shadow-v1",
        "excluded_10": [f"{x:02d}" for x in excluded],
        "score_max_abs_diff": 0.0, "feature_count": 32,
        "status": "PASS_SHADOW_LOCK_REPLAY"
    }

def main():
    manifest = json.loads((ROOT / "bundle_manifest.json").read_text(encoding="utf-8"))
    for item in manifest["files"]:
        path = ROOT / item["path"]
        assert path.is_file() and path.stat().st_size == item["bytes"] and sha(path) == item["sha256"], item["path"]
    registry = json.loads((ROOT / "registry/gpt_rebuilt_registry_v1.json").read_text(encoding="utf-8"))
    assert registry["registry_id"] == "GPT_REBUILT_REGISTRY_V1" and registry["production_authorized"] is False
    formal = formal7()
    shadow = shadow4()
    reverse = r3_hgb()
    output = {
        "registry_id": registry["registry_id"],
        "validation": "PASS_12_OF_12_LOCK_REPLAYS",
        "formal7": formal, "shadow4": shadow, "r3_hgb": reverse,
        "total_models_replayed": formal["count"] + shadow["count"] + 1,
        "production_authorized": False,
        "not_claimed": [
            "historical Production source recovery", "Canonical Registry v3 recovery",
            "external deployment", "R3 90% fixed-10 exclusion target",
            "predictive superiority over random baseline"
        ]
    }
    path = ROOT / "validation_output/validation_result.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
