"""Prove a candidate was frozen by a real release-coordinator run, via GitHub.

    python3 -I .github/signing/verify-build.py <candidate.json>      (GH_TOKEN: Actions read)

Private staging accepts writes from more than the coordinator (the dev
account's deploy role is effectively admin there), so a candidate.json in
staging is not proof of its origin. GitHub is: the claimed run must be
release-coordinator.yml on main of the application repo, at the recorded
attempt, completed successfully, and own an artifact named
approval-<candidate digest> — which only code inside that run can create.
"""
import hashlib
import json
import os
from pathlib import Path
import sys
import urllib.request

WORKFLOW_PATH = ".github/workflows/release-coordinator.yml"
REPOSITORY = "fluxlynx/irisbooks.io"


def fail(message):
    raise ValueError(message)


def github(token):
    def fetch(path):
        request = urllib.request.Request(f"https://api.github.com/{path}", headers={
            "Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"})
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.load(response)
    return fetch


def verify(raw, fetch):
    candidate = json.loads(raw)
    build, digest = candidate["build"], hashlib.sha256(raw).hexdigest()
    if build.get("kind") != "github" or build.get("repository") != REPOSITORY:
        fail("candidate does not name a build in the application repository")
    run_id, attempt = build["run_id"], build["run_attempt"]
    if not (run_id.isdigit() and attempt.isdigit()):
        fail("candidate run identity is malformed")
    run = fetch(f"repos/{REPOSITORY}/actions/runs/{run_id}/attempts/{attempt}")
    if (run.get("path") != WORKFLOW_PATH or run.get("head_branch") != "main"
            or run.get("repository", {}).get("full_name") != REPOSITORY
            or str(run.get("id")) != run_id or str(run.get("run_attempt")) != attempt):
        fail("the claimed run is not release-coordinator.yml on main at that attempt")
    if run.get("status") != "completed" or run.get("conclusion") != "success":
        fail("the claimed coordinator run has not completed successfully")
    name = f"approval-{digest}"
    artifacts = fetch(f"repos/{REPOSITORY}/actions/runs/{run_id}/artifacts?name={name}").get("artifacts", [])
    if not any(a.get("name") == name and str(a.get("workflow_run", {}).get("id")) == run_id for a in artifacts):
        fail("the claimed coordinator run did not freeze this candidate digest")
    return run_id, attempt, digest


def main(argv):
    try:
        if len(argv) != 1:
            fail("usage: verify-build.py <candidate.json>")
        run_id, attempt, digest = verify(Path(argv[0]).read_bytes(), github(os.environ["GH_TOKEN"]))
    except Exception as error:
        # Sanitized: never echo API responses or the token.
        message = str(error) if isinstance(error, ValueError) else f"{type(error).__name__} while asking GitHub"
        print(f"verify-build: {message}", file=sys.stderr)
        return 1
    print(f"✓ candidate {digest[:12]}… was frozen by coordinator run {run_id} attempt {attempt}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
