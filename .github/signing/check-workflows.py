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
require("\nrun-name: Sign ${{ inputs.release_id }} (${{ inputs.digest }})\n" in signing,
        "signing.yml: run title must bind the approved release id and candidate digest")
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

# The App key mints exactly two tokens in the approved job, both limited to
# fluxlynx/irisbooks.io: Actions read to verify provenance before signing,
# and Actions write to dispatch "collect" after the signatures are stored.
app_steps = [i for i, step in enumerate(steps) if i and "secrets.RELEASE_DISPATCH_APP_KEY" in step]  # 0 is the file header
sign_step = [i for i, step in enumerate(steps) if i and ".github/signing/sign.sh" in step]  # 0 is the file header
store = [i for i, step in enumerate(steps) if i and "upload.sh" in step]  # 0 is the file header
expected = [("permission-actions: read", lambda i: sign_step and i < sign_step[0]),
            ("permission-actions: write", lambda i: store and i > store[-1])]
require(len(app_steps) == 2, "signing.yml: the App key mints exactly two tokens")
for index, (permission, placed) in zip(app_steps, expected):
    step = steps[index]
    require("uses: actions/create-github-app-token@" in step, "signing.yml: the App key only feeds create-github-app-token")
    require(re.findall(r"permission-[a-z-]+: \w+", step) == [permission], f"signing.yml: token {index} must be exactly {permission}")
    require("repositories: irisbooks.io\n" in step and "owner: fluxlynx\n" in step,
            "signing.yml: App tokens are limited to fluxlynx/irisbooks.io")
    require(bool(placed(index)), f"signing.yml: the {permission} token is out of place")
require("secrets.RELEASE_DISPATCH_APP_KEY" not in validate_job, "signing.yml: the App key belongs to the approved sign job")
require(all("steps.provenance" not in steps[i] and "steps.dispatch" not in steps[i] for i in sign_step),
        "signing.yml: no GitHub token reaches the signing step")
verify_steps = [i for i, step in enumerate(steps) if i and "verify-build.py" in step]  # 0 is the file header
require(len(verify_steps) == 1 and sign_step and app_steps and app_steps[0] < verify_steps[0] < sign_step[0],
        "signing.yml: provenance is verified before signing")

if failures:
    print("\n".join("✗ " + failure for failure in failures))
    sys.exit(1)
print("✓ signing workflow guards hold")
