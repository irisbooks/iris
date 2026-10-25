#!/usr/bin/env bash
# fetch.sh <release-id> <digest> <dest> — download one frozen candidate from
# private staging by its recorded identity and verify it before use.
#
# Reads only candidates/<release-id>/<digest>/candidate.json and the payload
# paths that manifest names; never lists or syncs a prefix. The repository is
# public, so AWS output is suppressed: logs must not reveal the bucket.
set -euo pipefail
[ "$#" -eq 3 ] || { echo "usage: $0 <release-id> <digest> <dest>" >&2; exit 2; }
release_id="$1" digest="$2" dest="$3"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
die() { echo "fetch: $*" >&2; exit 1; }
[[ "$release_id" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}\.[1-9][0-9]{0,2}$ ]] || die "invalid release id"
[[ "$digest" =~ ^[0-9a-f]{64}$ ]] || die "invalid digest"
: "${CANDIDATE_BUCKET:?}" "${TRUSTED_WORKFLOW:?}"
prefix="s3://$CANDIDATE_BUCKET/candidates/$release_id/$digest"
get() { aws s3 cp --only-show-errors "$prefix/$1" "$dest/$1" >/dev/null 2>&1 || die "could not fetch $1"; }

mkdir -p "$dest/engine" "$dest/overlays"
get candidate.json
echo "$digest  $dest/candidate.json" | sha256sum -c --status - || die "candidate.json does not match the requested digest"
paths="$(python3 -I "$here/candidate.py" files "$dest/candidate.json")" || die "candidate.json is invalid"
while IFS= read -r path; do
  case "$path" in engine/*|overlays/*) ;; *) die "unexpected payload path" ;; esac
  get "$path"
done <<<"$paths"
python3 -I "$here/candidate.py" verify "$dest/candidate.json" "$dest/engine" "$dest/overlays" \
  --digest "$digest" --release-id "$release_id" --require-build "$TRUSTED_WORKFLOW" >/dev/null
