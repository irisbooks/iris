#!/usr/bin/env bash
# upload.sh <release-id> <digest> <signature-dir> — store one run's signature
# set beside the candidate, create-only, with its manifest written last.
#
#   candidates/<id>/<digest>/signatures/<run>.<attempt>/{engine,overlays}/…minisig
#   candidates/<id>/<digest>/signatures/<run>.<attempt>/manifest.json
#
# A rerun writes a new set; the coordinator verifies whichever complete set it
# uses. AWS output is suppressed so public logs never reveal the bucket.
set -euo pipefail
[ "$#" -eq 3 ] || { echo "usage: $0 <release-id> <digest> <signature-dir>" >&2; exit 2; }
release_id="$1" digest="$2" signatures="$3"
die() { echo "upload: $*" >&2; exit 1; }
: "${CANDIDATE_BUCKET:?}" "${GITHUB_RUN_ID:?}" "${GITHUB_RUN_ATTEMPT:?}" "${GITHUB_REPOSITORY:?}" "${GITHUB_SHA:?}"
set_key="candidates/$release_id/$digest/signatures/$GITHUB_RUN_ID.$GITHUB_RUN_ATTEMPT"
put() {
  aws s3api put-object --bucket "$CANDIDATE_BUCKET" --key "$set_key/$1" --body "$2" --if-none-match '*' \
    >/dev/null 2>&1 || die "could not store $1 (already present or access denied)"
}
files=()
while IFS= read -r path; do files+=("${path#"$signatures"/}"); done < <(find "$signatures" -type f -name '*.minisig' | LC_ALL=C sort)
[ "${#files[@]}" -gt 0 ] || die "no signatures to store"
for name in "${files[@]}"; do put "$name" "$signatures/$name"; done
python3 -I - "$signatures" "$digest" "${files[@]}" >"$signatures/manifest.json" <<'PY'
import hashlib, json, os, sys
root, digest, *names = sys.argv[1:]
print(json.dumps({
    "candidate_sha256": digest,
    "signer": {"repository": os.environ["GITHUB_REPOSITORY"], "commit": os.environ["GITHUB_SHA"],
               "run_id": os.environ["GITHUB_RUN_ID"], "run_attempt": os.environ["GITHUB_RUN_ATTEMPT"]},
    "files": {name: hashlib.sha256(open(os.path.join(root, name), "rb").read()).hexdigest() for name in names},
}, sort_keys=True, separators=(",", ":")))
PY
put manifest.json "$signatures/manifest.json"
echo "stored ${#files[@]} signature(s) as set $GITHUB_RUN_ID.$GITHUB_RUN_ATTEMPT"
