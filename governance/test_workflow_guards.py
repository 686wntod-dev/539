from pathlib import Path

capture = Path(".github/workflows/539-official-capture.yml").read_text(encoding="utf-8")
assert "options:\n          - probe" in capture
assert "full" not in capture
assert '--mode "probe"' in capture
assert "--problem-id RUN10-906-8-DIFFERENCES" in capture
assert "--action incremental" in capture
assert capture.index("Governance preflight") < capture.index("Install dependency") < capture.index("Capture bounded official-site API evidence")
push_block = capture.split("on:", 1)[1].split("workflow_dispatch:", 1)[0]
assert ".github/workflows/539-official-capture.yml" not in push_block

replay = Path(".github/workflows/539-cleanroom-replay.yml").read_text(encoding="utf-8")
replay_job = replay.split("  cleanroom-replay:", 1)[1].split("  append-replay-ledger:", 1)[0]
append_job = replay.split("  append-replay-ledger:", 1)[1]
assert "permissions:\n      contents: read" in replay_job
assert "permissions:\n      contents: write" in append_job
assert "contents: write" not in replay_job
assert "github.event_name == 'workflow_dispatch' && github.ref != 'refs/heads/replay-ci-v1'" in replay
assert "needs.cleanroom-replay.result == 'success' && github.event_name != 'pull_request'" in append_job
assert replay.index("Execute all 12 historical lock replays") < replay.index("Append successful replay fingerprint")
assert 'git push origin "HEAD:$REF_NAME"' in append_job
assert "ref: " + chr(36) + "{{ github.sha }}" in append_job
push_paths = replay.split("push:", 1)[1].split("pull_request:", 1)[0]
pr_paths = replay.split("pull_request:", 1)[1].split("workflow_dispatch:", 1)[0]
for paths in (push_paths, pr_paths):
    assert "governance/" not in paths
    assert "replay_fingerprint_ledger.jsonl" not in paths
    assert ".github/workflows/" not in paths
    assert "gpt_rebuild/replay/**" in paths
    assert "gpt_rebuild/replay_bundle.zip" in paths
    assert "gpt_rebuild/requirements-replay.txt" in paths
print("PASS: least-privilege replay, write-isolated append job, canonical manual ref, bounded capture, and no ledger self-trigger")
