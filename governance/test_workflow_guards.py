from pathlib import Path

capture = Path(".github/workflows/539-official-capture.yml").read_text(encoding="utf-8")
assert "options:\n          - probe" in capture
assert "full" not in capture
assert "--mode \"probe\"" in capture
assert "--problem-id RUN10-906-8-DIFFERENCES" in capture
assert "--action incremental" in capture
assert capture.index("Governance preflight") < capture.index("Install dependency") < capture.index("Capture bounded official-site API evidence")
push_block = capture.split("on:", 1)[1].split("workflow_dispatch:", 1)[0]
assert ".github/workflows/539-official-capture.yml" not in push_block

replay = Path(".github/workflows/539-cleanroom-replay.yml").read_text(encoding="utf-8")
assert "contents: write" in replay
assert "github.event_name != 'pull_request'" in replay
assert replay.index("Execute all 12 historical lock replays") < replay.index("Append successful replay fingerprint")
assert 'git push origin "HEAD:$REF_NAME"' in replay
assert "if: success() && github.event_name != 'pull_request'" in replay
# A ledger-only commit must not retrigger the expensive replay workflow.
push_paths = replay.split("push:", 1)[1].split("pull_request:", 1)[0]
pr_paths = replay.split("pull_request:", 1)[1].split("workflow_dispatch:", 1)[0]
for paths in (push_paths, pr_paths):
    assert "governance/" not in paths
    assert "replay_fingerprint_ledger.jsonl" not in paths
    assert ".github/workflows/" not in paths
    assert "gpt_rebuild/replay/**" in paths
    assert "gpt_rebuild/replay_bundle.zip" in paths
    assert "gpt_rebuild/requirements-replay.txt" in paths
print("PASS: bounded capture, append-only ledger, PR write exclusion, and no ledger self-trigger guards")
