"""Frozen release candidates: request validation, manifest freeze and payload checks.

    candidate.py request <request.json>                       validate; print the normalized request
    candidate.py freeze  <request.json> <engine-dir> <overlay-dir> <out> [--tool name=version ...]
    candidate.py digest  <candidate.json>                     validate; print the approval digest
    candidate.py verify  <candidate.json> <engine-dir> <overlay-dir> [--signed] [--digest <sha256>]
                         [--require-build <workflow-ref>] [--release-id <id>]
    candidate.py files   <candidate.json>      payload paths (engine/…, overlays/…) to fetch by identity
    candidate.py sign-list <candidate.json>    "<path>\t<trusted comment>" for each file to sign

A release request (`release/request.json`, merged through a PR) names what to
ship. `freeze` binds it to exact source commits and unsigned payload bytes. The
candidate file is canonical JSON, so the SHA-256 of its bytes is the approval
subject: the signer, acceptance and promotion all refer to that digest.
Signatures, test results, waivers and approvals are receipts kept beside the
candidate, never inside it; a changed source, payload or scope is a new
candidate. `verify --signed` checks that the signature files are present and
the payload bytes are unchanged — signature validity is checked by
release-artifacts.py (engine) and overlaybundle verify (packages), the same
code installers and clients use.

This file is stdlib-only and reads nothing beside itself: the signing
workflow in the public distribution repo runs a reviewed copy of it
(make signing.sync), never code from a downloaded candidate.
"""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tarfile

ROOT = Path(__file__).resolve().parents[1]
# The 16-file engine distribution of release-artifacts.py, unchanged; the
# unsigned candidate is everything except the signature over checksums.txt.
_PLATFORMS = [(system, arch) for system in ("darwin", "linux", "windows") for arch in ("amd64", "arm64")]
ENGINE_SIGNED = frozenset({f"iris_{system}_{arch}{'.exe' if system == 'windows' else ''}" for system, arch in _PLATFORMS}
                          | {f"iris_{system}_{arch}.mcpb" for system, arch in _PLATFORMS} | {"version.txt", "release.json"})
ENGINE_FILES = ENGINE_SIGNED | {"checksums.txt"}
ENGINE_SIGNATURES = frozenset({"checksums.txt.minisig"})

SCHEMA = 1
VERSION = re.compile(r"v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
PIN = re.compile(r"[a-z][a-z0-9]*(-[a-z0-9]+)*@[0-9]{4}\.[0-9]{2}\.[0-9]+")
RELEASE_ID = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\.[1-9][0-9]{0,2}")
COMMIT = re.compile(r"[0-9a-f]{40}")
SHA256 = re.compile(r"[0-9a-f]{64}")
REPOSITORY = re.compile(r"[A-Za-z0-9-]+/[A-Za-z0-9._-]+")
TOOL = re.compile(r"([a-z][a-z0-9-]*)=([0-9A-Za-z.+-]{1,32})")
# Acceptance gates of the release integration test, in report order.
GATES = ("pr-checks", "candidate-integrity", "local", "native", "deployed", "manual", "public")
TARGETS = ("dev", "beta", "prod-us")
REQUEST_KEYS = {"schema", "release_id", "engine", "compatible_engine", "overlays", "targets", "acceptance"}
CANDIDATE_KEYS = {"schema", "release_id", "request_sha256", "application", "engine", "compatible_engine",
                  "overlays", "toolchain", "build", "targets", "acceptance"}
GITHUB_BUILD = ("repository", "workflow_ref", "ref", "sha", "run_id", "run_attempt")


def fail(message):
    raise ValueError(message)


def strict_json(data):
    def pairs(items):
        keys = [key for key, _ in items]
        if len(keys) != len(set(keys)):
            fail("Duplicate JSON key.")
        return dict(items)
    try:
        return json.loads(data, object_pairs_hook=pairs,
                          parse_constant=lambda name: fail(f"Unsupported JSON constant {name}."))
    except json.JSONDecodeError as error:
        fail(f"Malformed JSON: {error.msg}.")


def encode(document):
    """Canonical bytes: the candidate digest must not depend on the writer."""
    return (json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode()


def matches(pattern, value):
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def exact_keys(document, keys, what):
    if not isinstance(document, dict) or set(document) != set(keys):
        fail(f"{what} must have exactly the keys {', '.join(sorted(keys))}.")


def ordered_subset(values, universe, what):
    if not isinstance(values, list) or not values or any(value not in universe for value in values):
        fail(f"{what} must be a non-empty list drawn from {', '.join(universe)}.")
    if len(set(values)) != len(values):
        fail(f"{what} has duplicates.")
    return [value for value in universe if value in values]


def check_scope(engine, compatible, overlays, targets, acceptance):
    """Rules shared by requests and frozen candidates."""
    if engine is None and not overlays:
        fail("A release needs an engine version, Overlay pins or both.")
    if engine is None and overlays:
        if not matches(VERSION, compatible):
            fail("Overlay-only releases must name the published compatible_engine they are qualified against.")
    elif compatible is not None:
        fail("compatible_engine is only for Overlay-only releases; packages are qualified against the released engine.")
    ids = [pin.split("@")[0] for pin in overlays]
    if len(set(ids)) != len(ids):
        fail("Release one version per Overlay id.")
    if "dev" not in targets:
        fail("Every candidate is staged and accepted in dev first.")
    if "candidate-integrity" not in acceptance:
        fail("The candidate-integrity gate cannot be omitted.")
    if ("public" in acceptance) != ("prod-us" in targets):
        fail("The public gate is required for, and only for, a prod-us target.")


def load_request(raw):
    request = strict_json(raw)
    if not isinstance(request, dict) or not set(request) <= REQUEST_KEYS or not {"schema", "release_id", "engine", "targets"} <= set(request):
        fail("Request needs schema, release_id, engine and targets; optional compatible_engine, overlays and acceptance.")
    if type(request["schema"]) is not int or request["schema"] != SCHEMA:
        fail(f"Unsupported request schema; expected {SCHEMA}.")
    if not matches(RELEASE_ID, request["release_id"]):
        fail("release_id must be YYYY-MM-DD.N.")
    engine = request["engine"]
    if engine != "none" and not matches(VERSION, engine):
        fail('engine must be a stable vX.Y.Z or "none".')
    overlays = request.get("overlays", [])
    if not isinstance(overlays, list) or any(not matches(PIN, pin) for pin in overlays):
        fail("overlays must list <id>@<version> pins.")
    if len(set(overlays)) != len(overlays):
        fail("overlays has duplicates.")
    targets = ordered_subset(request["targets"], TARGETS, "targets")
    default = [gate for gate in GATES if gate != "public" or "prod-us" in targets]
    # An omitted gate is an owner decision recorded in the merged request.
    acceptance = ordered_subset(request.get("acceptance", default), GATES, "acceptance")
    normalized = {
        "schema": SCHEMA, "release_id": request["release_id"], "engine": None if engine == "none" else engine,
        "compatible_engine": request.get("compatible_engine"), "overlays": sorted(overlays),
        "targets": targets, "acceptance": acceptance,
    }
    check_scope(normalized["engine"], normalized["compatible_engine"], normalized["overlays"], targets, acceptance)
    return normalized


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, text=True, stderr=subprocess.DEVNULL).strip()


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def listing(directory, expected, what):
    """Exact regular files only: no symlinks, subdirectories or extras."""
    directory = Path(directory)
    if directory.is_symlink() or not directory.is_dir():
        fail(f"{what} directory is missing.")
    found = {}
    for path in directory.iterdir():
        if path.is_symlink() or not path.is_file():
            fail(f"{what} contains a non-regular entry: {path.name}.")
        found[path.name] = path
    if set(found) != set(expected):
        missing, extra = sorted(set(expected) - set(found)), sorted(set(found) - set(expected))
        fail(f"{what} file set differs (missing: {', '.join(missing) or '-'}; unexpected: {', '.join(extra) or '-'}).")
    return found


def overlay_files(pins, signed):
    names = {pin + ".tar.gz" for pin in pins}
    return names | {name + ".minisig" for name in names} if signed else names


def bundle_manifest(path, pin):
    """Read <id>/overlay.yaml from an unsigned bundle without extracting it."""
    identifier, version = pin.split("@")
    try:
        with tarfile.open(path, "r:gz") as archive:
            member = archive.getmember(f"{identifier}/overlay.yaml")
            if not member.isreg() or member.size > 64 << 10:
                fail(f"{pin}: overlay.yaml must be a small regular file.")
            text = archive.extractfile(member).read().decode()
            for entry in archive.getmembers():
                name = entry.name
                if (not (entry.isreg() or entry.isdir()) or name.startswith("/") or "\\" in name
                        or ".." in name.split("/") or name.split("/")[0] != identifier):
                    fail(f"{pin}: bundle entry {name!r} is outside {identifier}/ or not a plain file.")
    except (tarfile.TarError, KeyError, OSError, EOFError, UnicodeDecodeError):
        fail(f"{pin}: unreadable bundle.")
    fields = dict(re.findall(r"^(id|version|requires_bindings):[ \t]*(\S+)[ \t]*$", text, re.M))
    if fields.get("id") != identifier or fields.get("version") != version:
        fail(f"{pin}: bundle carries {fields.get('id')}@{fields.get('version')}.")
    if not re.fullmatch(r"[1-9][0-9]{0,2}", fields.get("requires_bindings", "")):
        fail(f"{pin}: bundle lacks requires_bindings.")
    return int(fields["requires_bindings"])


def overlay_lock(root):
    lock = {}
    for line in (Path(root) / "iris/overlays/overlays.lock").read_text().splitlines():
        if line and not line.startswith("#"):
            pin, commit, tree = line.split()
            lock[pin] = (commit, tree)
    return lock


def build_identity(commit, environ):
    if environ.get("GITHUB_ACTIONS") != "true":
        return {"kind": "local"}
    values = {key: environ.get("GITHUB_" + key.upper(), "") for key in GITHUB_BUILD}
    if not all(values.values()):
        fail("GitHub build identity is incomplete.")
    if values["sha"] != commit:
        fail("The workflow commit does not match the frozen application commit.")
    return {"kind": "github", **values}


def freeze(raw_request, engine_dir, overlay_dir, tools=(), root=ROOT, environ=os.environ):
    request = load_request(raw_request)
    if git(root, "status", "--porcelain", "--untracked-files=no"):
        fail("Commit or stash tracked changes first; a candidate freezes one clean commit.")
    commit = git(root, "rev-parse", "--verify", "HEAD")
    repository = environ.get("GITHUB_REPOSITORY") or "fluxlynx/irisbooks.io"
    toolchain = {"go": re.search(r"^go ([0-9.]+)$", (Path(root) / "iris/go.mod").read_text(), re.M)[1]}
    for tool in tools:
        match = TOOL.fullmatch(tool)
        if not match or match[1] in toolchain:
            fail(f"Invalid or duplicate --tool {tool!r}.")
        toolchain[match[1]] = match[2]

    engine, bindings = None, None
    if request["engine"]:
        version = request["engine"]
        try:
            tagged = git(root, "rev-parse", "--verify", f"refs/tags/{version}^{{commit}}")
        except subprocess.CalledProcessError:
            fail(f"Source tag {version} is missing; tag the final merged commit first.")
        if tagged != commit:
            fail(f"Source tag {version} does not point at the frozen commit.")
        files = listing(engine_dir, ENGINE_FILES, "Engine candidate")
        if files["version.txt"].read_text() != version + "\n":
            fail("version.txt does not match the requested engine.")
        metadata = strict_json(files["release.json"].read_text())
        if not isinstance(metadata, dict) or metadata.get("version") != version or metadata.get("source_commit") != commit \
                or metadata.get("environment") not in ("dev", "beta") or set(metadata) != {"version", "source_commit", "environment"}:
            fail("release.json does not describe this version, commit and staging environment.")
        sums = "".join(f"{sha256(files[name])}  {name}\n" for name in sorted(ENGINE_SIGNED))
        if files["checksums.txt"].read_text() != sums:
            fail("checksums.txt does not match the candidate files.")
        bindings = int(re.search(r"^const BindingsVersion = ([0-9]+)$",
                                 (Path(root) / "iris/overlay/overlay.go").read_text(), re.M)[1])
        engine = {"version": version, "source_commit": commit, "environment": metadata["environment"],
                  "bindings": bindings, "artifacts": {name: sha256(path) for name, path in sorted(files.items())}}

    lock = overlay_lock(root)
    bundles = listing(overlay_dir, overlay_files(request["overlays"], False), "Overlay candidate") if request["overlays"] else {}
    overlays = []
    for pin in request["overlays"]:
        source_commit, tree = lock.get(pin, ("", ""))
        if not matches(COMMIT, source_commit):
            fail(f"{pin} is not vendored from a released tag in overlays.lock.")
        required = bundle_manifest(bundles[pin + ".tar.gz"], pin)
        if bindings is not None and required > bindings:
            fail(f"{pin} requires bindings {required}; engine {engine['version']} provides {bindings}.")
        overlays.append({"pin": pin, "source_commit": source_commit, "tree_sha256": tree,
                         "requires_bindings": required, "artifact_sha256": sha256(bundles[pin + ".tar.gz"])})

    candidate = {
        "schema": SCHEMA, "release_id": request["release_id"],
        "request_sha256": hashlib.sha256(raw_request).hexdigest(),
        "application": {"repository": repository, "commit": commit}, "engine": engine,
        "compatible_engine": request["compatible_engine"], "overlays": overlays, "toolchain": toolchain,
        "build": build_identity(commit, environ), "targets": request["targets"], "acceptance": request["acceptance"],
    }
    if git(root, "rev-parse", "--verify", "HEAD") != commit or git(root, "status", "--porcelain", "--untracked-files=no"):
        fail("The checkout changed while freezing.")
    validate(candidate)
    return encode(candidate)


def validate(candidate):
    """Strict schema: anything unexpected refuses rather than being ignored."""
    exact_keys(candidate, CANDIDATE_KEYS, "Candidate")
    if type(candidate["schema"]) is not int or candidate["schema"] != SCHEMA:
        fail(f"Unsupported candidate schema; expected {SCHEMA}.")
    if not matches(RELEASE_ID, candidate["release_id"]) or not matches(SHA256, candidate["request_sha256"]):
        fail("Invalid release_id or request digest.")
    application = candidate["application"]
    exact_keys(application, {"repository", "commit"}, "application")
    if not matches(REPOSITORY, application["repository"]) or not matches(COMMIT, application["commit"]):
        fail("Invalid application identity.")
    engine = candidate["engine"]
    if engine is not None:
        exact_keys(engine, {"version", "source_commit", "environment", "bindings", "artifacts"}, "engine")
        artifacts = engine["artifacts"]
        if (not matches(VERSION, engine["version"]) or engine["source_commit"] != application["commit"]
                or engine["environment"] not in ("dev", "beta") or type(engine["bindings"]) is not int or engine["bindings"] < 1
                or not isinstance(artifacts, dict) or set(artifacts) != ENGINE_FILES
                or not all(matches(SHA256, value) for value in artifacts.values())):
            fail("Invalid engine entry.")
    overlays = candidate["overlays"]
    if not isinstance(overlays, list):
        fail("overlays must be a list.")
    for overlay in overlays:
        exact_keys(overlay, {"pin", "source_commit", "tree_sha256", "requires_bindings", "artifact_sha256"}, "Overlay entry")
        if (not matches(PIN, overlay["pin"]) or not matches(COMMIT, overlay["source_commit"])
                or not matches(SHA256, overlay["tree_sha256"]) or not matches(SHA256, overlay["artifact_sha256"])
                or type(overlay["requires_bindings"]) is not int or overlay["requires_bindings"] < 1):
            fail("Invalid Overlay entry.")
        if engine is not None and overlay["requires_bindings"] > engine["bindings"]:
            fail(f"{overlay['pin']} requires newer bindings than the candidate engine.")
    pins = [overlay["pin"] for overlay in overlays]
    if pins != sorted(set(pins)):
        fail("Overlay entries must be unique and sorted by pin.")
    toolchain = candidate["toolchain"]
    if not isinstance(toolchain, dict) or "go" not in toolchain or not all(
            isinstance(value, str) and TOOL.fullmatch(f"{name}={value}") for name, value in toolchain.items()):
        fail("Invalid toolchain.")
    build = candidate["build"]
    if build != {"kind": "local"}:
        exact_keys(build, {"kind", *GITHUB_BUILD}, "build")
        if build["kind"] != "github" or not all(isinstance(build[key], str) and build[key] for key in GITHUB_BUILD) \
                or build["sha"] != application["commit"] or not matches(REPOSITORY, build["repository"]) \
                or not build["run_id"].isdigit() or not build["run_attempt"].isdigit():
            fail("Invalid build identity.")
    targets, acceptance = candidate["targets"], candidate["acceptance"]
    if ordered_subset(targets, TARGETS, "targets") != targets or ordered_subset(acceptance, GATES, "acceptance") != acceptance:
        fail("targets and acceptance must be in canonical order.")
    check_scope(engine and engine["version"], candidate["compatible_engine"], pins, targets, acceptance)


def load_candidate(raw, digest=None):
    """Return (candidate, digest); refuse non-canonical bytes or another digest."""
    candidate = strict_json(raw)
    validate(candidate)
    if encode(candidate) != raw:
        fail("Candidate bytes are not canonical; it was edited after freezing.")
    actual = hashlib.sha256(raw).hexdigest()
    if digest is not None and digest != actual:
        fail("Candidate digest does not match the approved digest.")
    return candidate, actual


def require_build(candidate, workflow_ref):
    """Only candidates frozen by the named workflow on the default branch are signable."""
    build = candidate["build"]
    repository = workflow_ref.split("/.github/", 1)[0]
    if build.get("kind") != "github" or build["workflow_ref"] != workflow_ref or build["ref"] != "refs/heads/main" \
            or build["repository"] != repository or candidate["application"]["repository"] != repository:
        fail("Candidate was not frozen by the trusted release workflow on main.")


def verify(raw, engine_dir, overlay_dir, signed=False, digest=None, workflow_ref=None, release_id=None):
    candidate, actual = load_candidate(raw, digest)
    if release_id is not None and candidate["release_id"] != release_id:
        fail("Candidate belongs to another release.")
    if workflow_ref is not None:
        require_build(candidate, workflow_ref)
    engine = candidate["engine"]
    if engine is not None:
        expected = set(engine["artifacts"]) | (ENGINE_SIGNATURES if signed else set())
        files = listing(engine_dir, expected, "Engine candidate")
        for name, value in engine["artifacts"].items():
            if sha256(files[name]) != value:
                fail(f"Engine file changed after freezing: {name}.")
    pins = [overlay["pin"] for overlay in candidate["overlays"]]
    if pins:
        files = listing(overlay_dir, overlay_files(pins, signed), "Overlay candidate")
        for overlay in candidate["overlays"]:
            if sha256(files[overlay["pin"] + ".tar.gz"]) != overlay["artifact_sha256"]:
                fail(f"Overlay bundle changed after freezing: {overlay['pin']}.")
    return actual


def payload_paths(candidate):
    engine = candidate["engine"]
    return ([f"engine/{name}" for name in sorted(engine["artifacts"])] if engine else []) \
        + [f"overlays/{overlay['pin']}.tar.gz" for overlay in candidate["overlays"]]


def sign_list(candidate):
    """One approved batch: the engine checksums and every package bundle."""
    return (["engine/checksums.txt\t"] if candidate["engine"] else []) \
        + [f"overlays/{overlay['pin']}.tar.gz\toverlay:{overlay['pin']}" for overlay in candidate["overlays"]]


def main(argv):
    try:
        action, *args = argv
        if action == "request" and len(args) == 1:
            sys.stdout.buffer.write(encode(load_request(Path(args[0]).read_bytes())))
        elif action == "freeze" and len(args) >= 4:
            request, engine_dir, overlay_dir, out, *rest = args
            if len(rest) % 2 or any(flag != "--tool" for flag in rest[::2]):
                fail("freeze accepts only --tool name=version options.")
            data = freeze(Path(request).read_bytes(), engine_dir, overlay_dir, rest[1::2])
            Path(out).write_bytes(data)
            print(hashlib.sha256(data).hexdigest())
        elif action == "digest" and len(args) == 1:
            print(load_candidate(Path(args[0]).read_bytes())[1])
        elif action == "verify" and len(args) >= 3:
            path, engine_dir, overlay_dir, *rest = args
            signed, digest, workflow_ref, release_id = False, None, None, None
            while rest:
                if rest[0] == "--signed":
                    signed, rest = True, rest[1:]
                elif rest[0] == "--digest" and len(rest) > 1 and matches(SHA256, rest[1]):
                    digest, rest = rest[1], rest[2:]
                elif rest[0] == "--require-build" and len(rest) > 1:
                    workflow_ref, rest = rest[1], rest[2:]
                elif rest[0] == "--release-id" and len(rest) > 1:
                    release_id, rest = rest[1], rest[2:]
                else:
                    fail(f"Unknown verify option {rest[0]!r}.")
            print(verify(Path(path).read_bytes(), engine_dir, overlay_dir, signed, digest, workflow_ref, release_id))
        elif action in ("files", "sign-list") and len(args) == 1:
            candidate, _ = load_candidate(Path(args[0]).read_bytes())
            print("".join(f"{line}\n" for line in (payload_paths if action == "files" else sign_list)(candidate)), end="")
        else:
            fail("usage: candidate.py request|freeze|digest|verify … (see the module docstring)")
    except (ValueError, OSError, subprocess.CalledProcessError) as error:
        print("candidate: " + str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
