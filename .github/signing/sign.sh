#!/usr/bin/env bash
# sign.sh <candidate.json> <payload-dir> <signature-dir> <public-key>
#
# Sign one approved batch — the engine checksums and every package bundle the
# candidate names — then verify each signature and trusted comment with the
# public key. The key arrives in MINISIGN_SECRET_KEY (+ MINISIGN_KEY_PASSWORD)
# and exists on disk only inside a 0700 temporary directory that is removed on
# success and failure. Never builds, restores caches or executes payloads; the
# only code run is this reviewed checkout and the pinned minisign.
set -euo pipefail
set +x
[ "$#" -eq 4 ] || { echo "usage: $0 <candidate.json> <payload-dir> <signature-dir> <public-key>" >&2; exit 2; }
candidate="$1" payload="$2" out="$3" pubkey="$4"
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
die() { echo "sign: $*" >&2; exit 1; }

list="$(python3 -I "$here/candidate.py" sign-list "$candidate")" || die "candidate is not signable"
[ -n "$list" ] || die "nothing to sign"
[ -n "${MINISIGN_SECRET_KEY:-}" ] || die "MINISIGN_SECRET_KEY is not available to this step"

umask 077
key_dir="$(mktemp -d)"
cleanup() {
  if [ -f "$key_dir/key" ]; then
    # Best effort before unlinking; the runner is discarded after the job.
    dd if=/dev/zero of="$key_dir/key" bs=1 count="$(wc -c <"$key_dir/key")" conv=notrunc 2>/dev/null || true
  fi
  rm -rf "$key_dir"
}
trap cleanup EXIT
printf '%s\n' "$MINISIGN_SECRET_KEY" >"$key_dir/key"
password="${MINISIGN_KEY_PASSWORD:-}"
unset MINISIGN_SECRET_KEY MINISIGN_KEY_PASSWORD

mkdir -p "$out"
while IFS=$'\t' read -r path comment; do
  file="$payload/$path"
  [ -f "$file" ] && [ ! -L "$file" ] || die "missing payload $path"
  mkdir -p "$out/$(dirname "$path")"
  args=(-S -s "$key_dir/key" -m "$file" -x "$out/$path.minisig")
  [ -z "$comment" ] || args+=(-t "$comment")
  printf '%s\n' "$password" | minisign "${args[@]}" >/dev/null || die "signing $path failed"
done <<<"$list"
cleanup
trap - EXIT
password=""

while IFS=$'\t' read -r path comment; do
  trusted="$(minisign -V -Q -m "$payload/$path" -x "$out/$path.minisig" -P "$pubkey")" \
    || die "$path does not verify with the release public key"
  if [ -n "$comment" ]; then
    [ "$trusted" = "$comment" ] || die "$path carries trusted comment '$trusted', expected '$comment'"
  fi
  echo "✓ signed $path"
done <<<"$list"
