# iris — IrisBooks CLI releases

This repository hosts the **official binary releases** of `iris`, the
command-line tool for [IrisBooks](https://irisbooks.jp) — local-first
bookkeeping for Japan, driven by your own AI assistant.

There is no source code here: `iris` ships as a signed, closed-source binary.
Releases are published to this repository; `https://irisbooks.jp/dl/…`
redirects here.

## Install

macOS / Linux:

```sh
curl -fsSL https://irisbooks.jp/install.sh | sh
```

Windows (PowerShell):

```powershell
irm https://irisbooks.jp/install.ps1 | iex
```

The install scripts detect your OS/architecture, download the matching asset
from the latest release, and verify the minisign signature over
`checksums.txt` when `minisign` is installed (falling back to a sha256 check
otherwise).

## Verify a download manually

Every release carries `checksums.txt` (SHA-256 over every asset) and
`checksums.txt.minisig`, signed with the IrisBooks release key
(key id `11D9CC26444B9F65`):

```sh
minisign -Vm checksums.txt -P RWRln0tEJszZEcTL7VcSL5XR+zcAA2FyqnfOAeLDnwaE7LAa7E3tJCCJ
grep " iris_darwin_arm64$" checksums.txt | shasum -a 256 -c -
```

## Release assets

| Asset | Platform |
|---|---|
| `iris_darwin_arm64` / `iris_darwin_amd64` | macOS (Apple Silicon / Intel) |
| `iris_linux_arm64` / `iris_linux_amd64` | Linux |
| `iris_windows_arm64.exe` / `iris_windows_amd64.exe` | Windows |
| `iris_<os>_<arch>.mcpb` | One-click MCP bundle (Claude Desktop) |
| `checksums.txt` / `checksums.txt.minisig` | Integrity manifest + signature |
| `version.txt` | Bare version string, for tooling |

## Links

- Product & documentation: <https://irisbooks.jp> · <https://irisbooks.jp/manual/>
- Getting started: <https://irisbooks.jp/start>
