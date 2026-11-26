from pathlib import Path

capture = Path(".github/workflows/539-official-capture.yml").read_text(encoding="utf-8")
assert "options:\n          - probe" in capture, "capture must expose only probe mode"
assert "full" not in capture, "unbounded full capture option must not exist"
assert "--mode \"probe\"" in capture, "capture command must hard-pin probe mode"
assert "--problem-id RUN10-906-8-DIFFERENCES" in capture
assert "--action incremental" in capture
assert capture.index("Governance preflight") < capture.index("Install dependency") < capture.index("Capture bounded official-site API evidence"), "preflight must run before network dependency install and capture"
push_block = capture.split("on:", 1)[1].split("workflow_dispatch:", 1)[0]
assert ".github/workflows/539-official-capture.yml" not in push_block, "editing the workflow must not trigger an automatic capture"
print("PASS: official capture is probe-only, preflight-gated, and cannot self-trigger on workflow edits")
