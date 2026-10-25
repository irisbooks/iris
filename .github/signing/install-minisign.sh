#!/usr/bin/env bash
# Install the pinned minisign release (linux x86_64) onto the job's PATH.
# The tarball hash is the trust anchor: it was checked against the upstream
# signature (key RWQf6LRCGA9i53mlYecO4IzT51TGPpvWucNSCh1CBM0QTaLn73Y7GFO3)
# when pinned. Re-pin both together when upgrading.
set -euo pipefail
VERSION=0.12
SHA256=9a599b48ba6eb7b1e80f12f36b94ceca7c00b7a5173c95c3efc88d9822957e73
dir="${RUNNER_TEMP:?}/minisign"
mkdir -p "$dir/bin"
cd "$dir"
curl -fsSL --retry 3 -o minisign.tar.gz "https://github.com/jedisct1/minisign/releases/download/$VERSION/minisign-$VERSION-linux.tar.gz"
echo "$SHA256  minisign.tar.gz" | sha256sum -c -
tar xzf minisign.tar.gz minisign-linux/x86_64/minisign
install -m 0755 minisign-linux/x86_64/minisign bin/minisign
echo "$dir/bin" >>"$GITHUB_PATH"
