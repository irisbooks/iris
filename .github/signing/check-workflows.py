"""Static guards for the release-signing workflow (no YAML parser needed).

    python3 -I .github/signing/check-workflows.py

Refuses changes that would let untrusted code or events reach the key:
other triggers, unpinned actions, caches, artifact uploads, inline
expression interpolation in shell, or secrets outside the signing step.
"""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
failures = []


def require(condition, message):
    if not condition:
        failures.append(message)


for workflow in sorted((ROOT / ".github/workflows").glob("*.yml")):
    text = workflow.read_text()
    for uses in re.findall(r"^\s*-?\s*uses:\s*(\S+)", text, re.M):
        require(re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", uses) is not None, f"{workflow.name}: unpinned action {uses}")
    require("actions/cache" not in text and "cache:" not in text, f"{workflow.name}: caches are not allowed")
    require("upload-artifact" not in text, f"{workflow.name}: public repo — never upload Actions artifacts")
    require("pull_request_target" not in text and "workflow_run" not in text, f"{workflow.name}: privileged trigger")

signing = (ROOT / ".github/workflows/signing.yml").read_text()
triggers = signing.split("\non:", 1)[1].split("\npermissions:", 1)[0]
require(re.findall(r"^  (\w+):", triggers, re.M) == ["workflow_dispatch"], "signing.yml: workflow_dispatch is the only trigger")
require("\npermissions: {}\n" in signing, "signing.yml: top-level permissions must be empty")
require(signing.count("environment: release-signing") == 1, "signing.yml: exactly one job uses the release-signing environment")
require(signing.count("if: github.ref == 'refs/heads/main'") == 2, "signing.yml: both jobs must refuse non-main refs")
require("contents: write" not in signing and "id-token: write" in signing, "signing.yml: no write tokens beyond OIDC")

# Secrets appear only in the one step that runs sign.sh, after approval.
steps = re.split(r"\n      - ", signing)
holders = [step for step in steps if "secrets." in step]
require(len(holders) == 1 and "sign.sh" in holders[0], "signing.yml: secrets may reach only the sign.sh step")
sign_job = signing.split("\n  sign:\n", 1)[1]
require("secrets." in sign_job and "secrets." not in signing.split("\n  sign:\n", 1)[0],
        "signing.yml: secrets belong to the approved sign job")

# Expressions go through env:, never straight into a shell script.
for block in re.findall(r"run: \|\n((?:          .*\n|\n)+)|run: (.*)", signing):
    body = "".join(block)
    require("${{" not in body, "signing.yml: interpolate inputs through env:, not inside run:")

if failures:
    print("\n".join("✗ " + failure for failure in failures))
    sys.exit(1)
print("✓ signing workflow guards hold")
