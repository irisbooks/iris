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

# Key material reaches only the one step that runs sign.sh, after approval.
# Other secrets are staging identifiers kept secret so logs mask them.
steps = re.split(r"\n      - ", signing)
holders = [step for step in steps if "secrets.MINISIGN_" in step]
require(len(holders) == 1 and "sign.sh" in holders[0], "signing.yml: key secrets may reach only the sign.sh step")
validate_job, sign_job = signing.split("\n  sign:\n", 1)
require("secrets.MINISIGN_" in sign_job and "secrets.MINISIGN_" not in validate_job,
        "signing.yml: key secrets belong to the approved sign job")
require("secrets.CANDIDATE_SIGNER_ROLE_ARN" not in validate_job, "signing.yml: the signer role belongs to the approved sign job")
names = set(re.findall(r"secrets\.([A-Z0-9_]+)", signing))
require(names <= {"MINISIGN_SECRET_KEY", "MINISIGN_KEY_PASSWORD", "CANDIDATE_BUCKET", "CANDIDATE_VALIDATOR_ROLE_ARN",
                  "CANDIDATE_SIGNER_ROLE_ARN", "RELEASE_DISPATCH_APP_KEY"}, f"signing.yml: unexpected secrets {sorted(names)}")

# The dispatch App key mints one token, after signatures are stored, that can
# only dispatch workflows in the application repo.
app_steps = [i for i, step in enumerate(steps) if "secrets.RELEASE_DISPATCH_APP_KEY" in step]
store = [i for i, step in enumerate(steps) if "upload.sh" in step]
require(len(app_steps) == 1 and bool(store) and app_steps[0] > store[-1],
        "signing.yml: the dispatch App key is used once, after the signatures are stored")
if len(app_steps) == 1:
    app_step = steps[app_steps[0]]
    require("uses: actions/create-github-app-token@" in app_step, "signing.yml: the App key only feeds create-github-app-token")
    require(re.findall(r"permission-[a-z-]+: \w+", app_step) == ["permission-actions: write"],
            "signing.yml: the dispatch token is limited to actions: write")
    require("repositories: irisbooks.io\n" in app_step and "owner: fluxlynx\n" in app_step,
            "signing.yml: the dispatch token is limited to fluxlynx/irisbooks.io")
    require("secrets.RELEASE_DISPATCH_APP_KEY" not in validate_job, "signing.yml: the dispatch key belongs to the approved sign job")
# Public logs: staging identifiers must come from secrets (masked), never vars.
require(re.search(r"vars\.CANDIDATE_(BUCKET|\w*ROLE_ARN)", signing) is None,
        "signing.yml: bucket and role ARNs must be secrets so public logs mask them")

# Expressions go through env:, never straight into a shell script.
for block in re.findall(r"run: \|\n((?:          .*\n|\n)+)|run: (.*)", signing):
    body = "".join(block)
    require("${{" not in body, "signing.yml: interpolate inputs through env:, not inside run:")

if failures:
    print("\n".join("✗ " + failure for failure in failures))
    sys.exit(1)
print("✓ signing workflow guards hold")
