import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
registry = json.loads((ROOT / "registry.json").read_text(encoding="utf-8"))
summary = json.loads((ROOT / "validation_summary.json").read_text(encoding="utf-8"))
retrain = json.loads((ROOT / "retrain_comparison.json").read_text(encoding="utf-8"))

assert registry["registry_id"] == "GPT_REBUILT_REGISTRY_V1"
assert registry["production_authorized"] is False
assert len(registry["models"]) == 12
assert summary["validation"] == "PASS_12_OF_12_LOCK_REPLAYS"
assert summary["total_models_replayed"] == 12
assert summary["formal7"]["replayed"] == 7
assert summary["full4034_shadow"]["replayed"] == 4
assert summary["r3_hgb_shadow"]["replayed"] == 1
assert summary["r3_hgb_shadow"]["max_abs_score_difference"] == 0
assert retrain["status"] == "NOT_REPRODUCED_BYTE_FOR_BYTE_IN_CURRENT_ENVIRONMENT"
assert retrain["decision"].startswith("Do not replace/promote")
ids = [m["model_id"] for m in registry["models"]]
assert len(set(ids)) == 12
ai1 = [m for m in registry["models"] if m["model_id"].startswith("AI-1-")]
assert len(ai1) == 2
assert any("one family vote" in rule for rule in registry["family_rules"])
assert any("Historical original Production lineage" in gate for gate in registry["open_gates"])
print("GPT rebuild governance guard: PASS")
