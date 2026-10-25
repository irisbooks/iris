"""Disposable-key trial of the signing path: one valid batch and every refusal.

    python3 -I .github/signing/trial.py

Runs the same candidate.py and sign.sh as the release-signing job, with a key
generated for this run only. Needs minisign on PATH. No secrets, no network.
"""
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("candidate", HERE / "candidate.py")
CANDIDATE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CANDIDATE)
WORKFLOW = "fluxlynx/irisbooks.io/.github/workflows/release-coordinator.yml@refs/heads/main"
RELEASE_ID = "2026-10-25.1"
PIN = "journal-balance@2026.10.1"
COMMIT = "a" * 40
PASSWORD = "disposable-trial-password"
failures = []


def check(name, condition, detail=""):
    print(("ok   " if condition else "FAIL ") + name + (f" — {detail}" if detail and not condition else ""))
    if not condition:
        failures.append(name)


def run(*command, env=None, stdin=None):
    return subprocess.run(command, capture_output=True, text=True, input=stdin, env=env, timeout=60)


def keypair(directory, password):
    directory.mkdir()
    subprocess.run(["minisign", "-G", "-f", "-p", str(directory / "pub"), "-s", str(directory / "key")],
                   input=f"{password}\n{password}\n", capture_output=True, text=True, check=True)
    return (directory / "key").read_text(), (directory / "pub").read_text().splitlines()[-1]


def fixture(root, **build):
    """A frozen candidate as the coordinator on main would produce it."""
    payload = root / "payload"
    engine, overlays = payload / "engine", payload / "overlays"
    engine.mkdir(parents=True)
    overlays.mkdir()
    for name in sorted(CANDIDATE.ENGINE_SIGNED - {"version.txt", "release.json"}):
        (engine / name).write_bytes(hashlib.sha256(name.encode()).digest())
    (engine / "version.txt").write_text("v0.2.19\n")
    (engine / "release.json").write_text(json.dumps({"environment": "dev", "source_commit": COMMIT, "version": "v0.2.19"}) + "\n")
    (engine / "checksums.txt").write_text("".join(
        f"{CANDIDATE.sha256(engine / name)}  {name}\n" for name in sorted(CANDIDATE.ENGINE_SIGNED)))
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
        text = b"id: journal-balance\nversion: 2026.10.1\nrequires_bindings: 5\n"
        info = tarfile.TarInfo("journal-balance/overlay.yaml")
        info.size = len(text)
        archive.addfile(info, io.BytesIO(text))
    (overlays / f"{PIN}.tar.gz").write_bytes(buffer.getvalue())
    identity = {"kind": "github", "repository": "fluxlynx/irisbooks.io", "workflow_ref": WORKFLOW,
                "ref": "refs/heads/main", "sha": COMMIT, "run_id": "1", "run_attempt": "1", **build}
    candidate = {
        "schema": 1, "release_id": RELEASE_ID, "request_sha256": "0" * 64,
        "application": {"repository": "fluxlynx/irisbooks.io", "commit": COMMIT},
        "engine": {"version": "v0.2.19", "source_commit": COMMIT, "environment": "dev", "bindings": 5,
                   "artifacts": {name: CANDIDATE.sha256(engine / name) for name in sorted(CANDIDATE.ENGINE_FILES)}},
        "compatible_engine": None,
        "overlays": [{"pin": PIN, "source_commit": "b" * 40, "tree_sha256": "c" * 64, "requires_bindings": 5,
                      "artifact_sha256": CANDIDATE.sha256(overlays / f"{PIN}.tar.gz")}],
        "toolchain": {"go": "1.26.9", "minisign": "0.12"}, "build": identity,
        "targets": ["dev", "prod-us"], "acceptance": list(CANDIDATE.GATES),
    }
    data = CANDIDATE.encode(candidate)
    (root / "candidate.json").write_bytes(data)
    return root / "candidate.json", payload, hashlib.sha256(data).hexdigest()


def validate(candidate, payload, digest, *extra):
    return run(sys.executable, "-I", str(HERE / "candidate.py"), "verify", str(candidate), str(payload / "engine"),
               str(payload / "overlays"), "--digest", digest, "--require-build", WORKFLOW, "--release-id", RELEASE_ID, *extra)


AWS_DOUBLE = r'''
import os, shutil, sys
from pathlib import Path
store, args = Path(os.environ["TRIAL_S3"]), sys.argv[1:]
def flag(name): return args[args.index(name) + 1]
if args[:2] == ["s3", "cp"]:
    source = store / args[-2].split("/", 3)[3]
    if not source.is_file(): sys.exit(1)
    shutil.copyfile(source, args[-1])
elif args[:2] == ["s3api", "put-object"]:
    assert flag("--if-none-match") == "*"
    target = store / flag("--key")
    if target.exists(): sys.exit(254)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(flag("--body"), target)
else: sys.exit(2)
'''


def staging_round_trip(temp, environ, pubkey):
    """fetch.sh → sign.sh → upload.sh against a private-staging double."""
    root = temp / "staging"
    root.mkdir()
    candidate, payload, digest = fixture(root)
    store, tools = root / "s3", root / "bin"
    tools.mkdir()
    (tools / "aws").write_text(f"#!{sys.executable}\n" + AWS_DOUBLE)
    (tools / "aws").chmod(0o755)
    prefix = store / "candidates" / RELEASE_ID / digest
    shutil.copytree(payload, prefix)
    shutil.copyfile(candidate, prefix / "candidate.json")
    (prefix / "engine/unlisted-extra").write_text("never fetched")
    env = {**environ, "PATH": f"{tools}{os.pathsep}{environ['PATH']}", "TRIAL_S3": str(store),
           "CANDIDATE_BUCKET": "trial-bucket", "TRUSTED_WORKFLOW": WORKFLOW, "GITHUB_RUN_ID": "7",
           "GITHUB_RUN_ATTEMPT": "1", "GITHUB_REPOSITORY": "irisbooks/iris", "GITHUB_SHA": "d" * 40}
    fetched = root / "fetched"
    result = run("bash", str(HERE / "fetch.sh"), RELEASE_ID, digest, str(fetched), env=env)
    check("fetch takes only the recorded payload", result.returncode == 0
          and not (fetched / "engine/unlisted-extra").exists(), result.stderr)
    check("fetch output hides the bucket", "trial-bucket" not in result.stdout + result.stderr)
    wrong = run("bash", str(HERE / "fetch.sh"), RELEASE_ID, "e" * 64, str(root / "wrong"), env=env)
    check("fetch refuses an unknown digest", wrong.returncode != 0 and "trial-bucket" not in wrong.stderr, wrong.stderr)
    signatures = root / "signatures"
    signed = run("bash", str(HERE / "sign.sh"), str(fetched / "candidate.json"), str(fetched), str(signatures), pubkey, env=env)
    check("fetched candidate signs", signed.returncode == 0, signed.stderr)
    stored = run("bash", str(HERE / "upload.sh"), RELEASE_ID, digest, str(signatures), env=env)
    set_dir = prefix / "signatures/7.1"
    manifest = json.loads((set_dir / "manifest.json").read_text()) if (set_dir / "manifest.json").exists() else {}
    check("signature set stored with manifest", stored.returncode == 0 and manifest.get("candidate_sha256") == digest
          and set(manifest.get("files", {})) == {"engine/checksums.txt.minisig", f"overlays/{PIN}.tar.gz.minisig"}, stored.stderr)
    again = run("bash", str(HERE / "upload.sh"), RELEASE_ID, digest, str(signatures), env=env)
    check("a stored signature set is never replaced", again.returncode != 0 and "trial-bucket" not in again.stderr, again.stderr)


def main():
    if not shutil.which("minisign"):
        sys.exit("trial: minisign is required")
    with tempfile.TemporaryDirectory() as directory:
        temp = Path(directory)
        secret, pubkey = keypair(temp / "release", PASSWORD)
        _, other_pubkey = keypair(temp / "other", PASSWORD)
        scratch = temp / "scratch"
        scratch.mkdir()
        environ = {**{k: v for k, v in os.environ.items() if not k.startswith("MINISIGN_")}, "TMPDIR": str(scratch),
                   "MINISIGN_SECRET_KEY": secret, "MINISIGN_KEY_PASSWORD": PASSWORD}

        def sign(root, candidate, payload, key=pubkey, env=None):
            result = run("bash", str(HERE / "sign.sh"), str(candidate), str(payload), str(root / "signatures"), key,
                         env=env or environ)
            leaked = PASSWORD in result.stdout + result.stderr or secret.splitlines()[-1] in result.stdout + result.stderr
            check(f"no key material in output ({root.name})", not leaked)
            check(f"temporary key removed ({root.name})", not any(scratch.iterdir()), str(list(scratch.iterdir())))
            return result

        # A valid batch signs and verifies with the client contract.
        root = temp / "valid"
        root.mkdir()
        candidate, payload, digest = fixture(root)
        check("valid request validates", validate(candidate, payload, digest).returncode == 0)
        result = sign(root, candidate, payload)
        check("valid batch signs", result.returncode == 0, result.stderr)
        signatures = root / "signatures"
        engine_check = run("minisign", "-Vm", str(payload / "engine/checksums.txt"), "-x",
                           str(signatures / "engine/checksums.txt.minisig"), "-P", pubkey)
        check("engine checksums verify", engine_check.returncode == 0, engine_check.stderr)
        comment = run("minisign", "-V", "-Q", "-m", str(payload / f"overlays/{PIN}.tar.gz"), "-x",
                      str(signatures / f"overlays/{PIN}.tar.gz.minisig"), "-P", pubkey)
        check("package carries its authenticated pin", comment.stdout.strip() == f"overlay:{PIN}", comment.stdout)
        for kind in ("engine", "overlays"):
            for path in (signatures / kind).iterdir():
                shutil.copyfile(path, payload / kind / path.name)
        check("signed payload still matches the candidate", validate(candidate, payload, digest, "--signed").returncode == 0)

        # Requests that must be refused before any key is used.
        untrusted = "trusted release workflow"
        refusals = {
            "changed digest": (lambda r: (*fixture(r)[:2], "f" * 64), "approved digest"),
            "untrusted workflow": (lambda r: fixture(r, workflow_ref=WORKFLOW.replace("release-coordinator", "check")), untrusted),
            "branch build": (lambda r: fixture(r, ref="refs/heads/topic",
                                               workflow_ref=WORKFLOW.replace("refs/heads/main", "refs/heads/topic")), untrusted),
            "pull request build": (lambda r: fixture(r, ref="refs/pull/1/merge"), untrusted),
            "forked repository": (lambda r: fixture(r, repository="someone/irisbooks.io"), untrusted),
        }
        for name, (make, expected) in refusals.items():
            root = temp / name.replace(" ", "-")
            root.mkdir()
            result = validate(*make(root))
            check(f"refuses {name}", result.returncode != 0 and expected in result.stderr, result.stderr)

        def tampered(name, expected, change):
            root = temp / name.replace(" ", "-")
            root.mkdir()
            candidate, payload, digest = fixture(root)
            change(candidate, payload)
            result = validate(candidate, payload, digest)
            check(f"refuses {name}", result.returncode != 0 and expected in result.stderr, result.stderr)
        tampered("non-canonical manifest", "not canonical",
                 lambda c, p: c.write_text(json.dumps(json.loads(c.read_text()), indent=1)))
        tampered("changed engine byte", "Engine file changed", lambda c, p: (p / "engine/iris_linux_amd64").write_bytes(b"x"))
        tampered("malformed package archive", "Overlay bundle changed",
                 lambda c, p: (p / f"overlays/{PIN}.tar.gz").write_bytes(b"not gzip"))
        tampered("unexpected file", "unexpected: run-me.sh", lambda c, p: (p / "engine/run-me.sh").write_text("echo"))
        def link(c, p):
            target = p / "engine/iris_linux_arm64"
            target.unlink()
            target.symlink_to(p / "engine/iris_linux_amd64")
        tampered("symlinked payload", "non-regular entry", link)

        # Signing failures stop the batch and still remove the key.
        def failing(name, expected, key=pubkey, env=None, shim=None):
            root = temp / name.replace(" ", "-")
            root.mkdir()
            candidate, payload, _ = fixture(root)
            run_env = dict(env or environ)
            if shim:
                shim_dir = root / "bin"
                shim_dir.mkdir()
                (shim_dir / "minisign").write_text(shim)
                (shim_dir / "minisign").chmod(0o755)
                run_env["PATH"] = f"{shim_dir}{os.pathsep}{run_env['PATH']}"
            result = sign(root, candidate, payload, key=key, env=run_env)
            check(f"refuses {name}", result.returncode != 0 and expected in result.stderr, result.stderr)
        failing("wrong password", "signing engine/checksums.txt failed", env={**environ, "MINISIGN_KEY_PASSWORD": "wrong"})
        failing("missing key", "not available", env={k: v for k, v in environ.items() if k != "MINISIGN_SECRET_KEY"})
        failing("mismatched public key", "does not verify", key=other_pubkey)
        real = shutil.which("minisign")
        failing("altered trusted comment", "carries trusted comment", shim=(
            "#!/bin/sh\n# Rewrites -t to prove the post-sign comment check.\n"
            "for a in \"$@\"; do shift; case \"$prev\" in -t) set -- \"$@\" overlay:other@2026.10.1 ;; *) set -- \"$@\" \"$a\" ;; esac; prev=\"$a\"; done\n"
            f"exec {real} \"$@\"\n"))

        staging_round_trip(temp, environ, pubkey)

    print(f"\n{len(failures)} failure(s)" if failures else "\nall signing trial checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
