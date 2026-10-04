# CLI command reference

Every `iris` command, grouped by purpose. The CLI has two surfaces:

- **File-mode commands** operate on a local book folder. With no path
  argument they walk up from the current directory to find the book, so you
  can run them from anywhere inside the book tree.
- **Cloud commands** (`iris api …`) talk to the IrisBooks server and operate
  on a **book ID**, not a path. They need you to be signed in
  (`iris api login`) or to set `IRIS_API_TOKEN`.

Run `iris <command> -h` for the authoritative, up-to-date flags of any
command. `iris -h` lists everything; `iris api -h` lists the cloud
subcommands.

Commands that emit JSON share one convention: **amounts are integers in the
book currency's minor units** (¥1,200 is `1200` at scale 0; $12.00 is `1200` at
scale 2), dates are `YYYY-MM-DD` strings, and the document is pretty-printed
with a two-space indent. The output shapes below are written as key skeletons —
`?` marks a key that is omitted when empty.

## Setup

### iris update

```bash
iris update --check [--json]   # read-only check against the latest stable release
iris update [--json]           # install after signature, checksum and version checks
```

Updates the executable currently running (resolving symlinks), so MCP
registrations keep pointing at the same path. JSON includes `currentVersion`,
`latestVersion`, `status`, `updateAvailable`, `executablePath`, `pathExecutable`,
`pathMismatch`, `installKind`, `downloadURL`, `updateCommand` (an argument
array), `instructions`, `updated`, `restartRequired`, and optional `error`.
`updateAvailable` is null for a failed check or development/prerelease build.
Status is `update_available`, `up_to_date`, `newer_than_latest`, `development`,
`check_failed`, or `updated`. Exit 0 means a successful check/update (including
no update needed); exit 1 means failure; exit 2 means invalid arguments.

No implicit network checks occur during book operations. `IRIS_DL_BASE`
selects the download base (default `https://irisbooks.jp/dl`); the release
signature is always checked against the built-in key, without requiring
`minisign` to be installed. A failed verification preserves the old executable.
No downgrade or development-build replacement is automatic.

For `.mcpb` installations the check provides a matching bundle URL; installation
is done through the client's extension settings. After a CLI update, rerun
`iris onboard` in your book and restart MCP; call `check_update` to confirm the
agent's running version. On Windows, stop MCP servers and retry if locked.
Older binaries without this command use the installer to upgrade first.

### iris init

Create a new book. Bare `iris init` runs a guided wizard in the current directory.
With flags, supply a destination path (`.` for the current directory) to skip the
prompts.

```bash
iris init [flags] <path>
```

| Flag | Meaning |
| --- | --- |
| `--name` | Book display name |
| `--region` | Region code (JP, US; default JP) |
| `--language` | Language (ISO 639-1) |
| `--entity-kind` | individual / company / partnership / trust |
| `--chart` | Starter-chart variant, where the region offers several — JP: general / it / food (default general). A region without a chart of its own gets a neutral starter chart |
| `--currency` | Currency (ISO 4217; default per region) |
| `--fiscal-start-month` | Fiscal-year start month 1–12 |
| `--fiscal-year` | The fiscal year the book covers (YYYY; default: the one holding today) — e.g. last year's, when you're catching up on its filing |
| `--sample` | Seed ~40 demo journals to explore |
| `--posting` | Posting policy written into LLM-GUIDE.md: `approve` (default — you review and post) / `auto` (your assistant posts everything that validates) |
| `--book-id` | Pre-link to an existing server book (advanced) |

### iris onboard

Wire this machine's AI assistant to the book: register `iris mcp serve` with
MCP clients and write the Claude Code skill. Claude Code's project config
(`.mcp.json`) is always written; Claude Desktop, the Codex CLI, Cursor,
Gemini CLI, and VS Code are registered when detected on the machine, or
forced with their flag.

```bash
iris onboard [--book PATH] [--claude-desktop] [--codex] [--cursor] [--gemini] [--vscode] [--install-path] [--no-skill] [--dry-run]
iris onboard --status [--json]    # read-only report: what is registered where
```

`--status` reports each client's registration state (including whether the
registered binary still exists — the stale state re-running `iris onboard`
fixes). `--json` makes the report machine-readable. Re-running `iris onboard`
is always safe: registrations are updated in place, never duplicated.

### iris offboard

The inverse of `iris onboard`: remove the `irisbooks` MCP registration from
every client config (including leftovers from clients no longer installed)
and the Claude Code skill. Does not touch the book's data or your sign-in.
Idempotent — safe to run before a clean reinstall.

```bash
iris offboard [--book PATH] [--keep-skill] [--remove-path] [--dry-run]
```

| Flag | Meaning |
| ---- | ------- |
| `--keep-skill` | Keep the Claude Code skill (when other books still use it) |
| `--remove-path` | Also remove the binary installed by `onboard --install-path` and revert its PATH entry |
| `--dry-run` | Print what would be removed without removing anything |

### iris uninstall

Remove iris itself from this machine: the iris binaries, your sign-in and
local config (`~/.config/irisbooks` — the CLI session is revoked server-side
first), the Claude Code skill, machine-level MCP registrations (Claude
Desktop, Codex CLI), and the PATH entry from `iris onboard --install-path`.
It always prints the exact list of what it found on this machine and asks
for confirmation before deleting anything.

Your books are never touched — they are plain files you own. Per-book agent
wiring (`.mcp.json` inside a book) is also left in place; run
`iris offboard --book PATH` first if you want that removed too.

```bash
iris uninstall [--yes] [--dry-run]
```

| Flag | Meaning |
| ---- | ------- |
| `--yes` | Skip the confirmation prompt |
| `--dry-run` | Print the deletion plan without removing anything |

### iris clone

Fetch a server book to disk (the lifecycle peer of `init`). Requires
sign-in. Works immediately on a brand-new book created in the web app or
with `iris api books new` outside a book folder — those are born with
`config/book.yaml` and a starter chart of accounts. (A cloud book created
from inside a local book starts empty and receives that folder's files on its
first `iris sync`.) It also writes the local
guides for your AI assistant (`LLM-GUIDE.md`, `CLAUDE.md`, `README.md`) when
the book has none — they never sync, so a book created in the web app arrives
without them.

```bash
iris clone [--force] <book-id> [dest]
```

## Inspect & validate

### iris status

Print a book's identity, fiscal-year start, archive flags, and how many
`draft` drafts exist (drafts are excluded from reports).

```bash
iris status [--json] [path]
```

**Output shape** (`--json`):

```text
{ name, bookId, region, language, currency, fiscalStartMonth,
  archived, archive?{ sourceBookId, fiscalYear },
  draftCount?, remoteDeleted? }
```

`archive` appears only inside an archive folder, `draftCount` only when the
drafts could be counted, and `remoteDeleted` only when the server reports the
book gone.

### iris validate

Validate a book's structure and entries: YAML, double-entry balance, account
existence, date consistency, status values, and (JP taxable books) tax
classification.

```bash
iris validate [--v] [--json] [--fix] [path]
```

`--fix` records the values the region overlay derives for you — reported as
hints, such as the consumption tax inside a line on a 税抜経理 book — into the
files, then validates again.

`--v` prints every file scanned; `--json` emits issues + counts and exits 1
on errors.

**Output shape** (`--json`):

```text
{ book, bookOk, chartOk, journals, assets, notes,
  errors, warnings, hints, ok,
  issues[{ severity, file, code?, message }] }
```

`code` is a stable catalogue key — `journal.date-required`,
`chart.alias-shadow-path`, `asset.ikkatsu-cost-range`, and so on. Branch on it
rather than on `message`, which is translated. `ok` is `errors == 0`; warnings
and hints affect neither `ok` nor the exit code.

### iris hash

Print the canonical content hash of a single file (useful when comparing
local bytes against what the server accepted).

```bash
iris hash [--raw] <file>
```

### iris organize

Bring a book's layout into canonical shape. Dry-run by default.

```bash
iris organize [--apply] [--fix month-folders,extensions,empty-raw,config-typos] [--json] [path]
```

`month-folders` moves a journal filed under a `journals/YYYY-MM/` folder that
isn't its date's month into the right one, and updates the parse caches'
`target:` links in `notes/raw/` to the new paths. Subfolders below the month
(such as `auto/`) are kept; journals outside month folders are left alone.

**Output shape** (`--json`) — the plan, which is exactly what `--apply` executes:

```text
[ { family, code, path, new_path?, delete?, reason } ]
```

`family` is one of the `--fix` categories. A move carries `new_path`; a removal
carries `delete: true`.

## Reports & search

### iris balance

Trial balance as of a date (posted entries only).

```bash
iris balance [--as-of YYYY-MM-DD] [path]
```

Output is the same trial-balance document as `iris report tb` (see below).

### iris report

Financial statements. Subcommands:

```bash
iris report tb [--as-of YYYY-MM-DD] [path]               # trial balance
iris report pl [--from D] [--to D] [path]                # profit & loss
iris report bs [--as-of YYYY-MM-DD] [path]               # balance sheet
iris report ledger --account PATH [--as-of D] [path]     # general ledger for one account
iris report sum --by KEY[,KEY...] [--from D] [--to D] [--year YYYY] [path]
                                                         # group-by sums over journal lines
```

Report output is **JSON** (amounts in minor units). Cloud responses may
include additional revision or freshness metadata. There is no text-table mode:
terminal column alignment is
unreliable for Japanese account names, your AI consumes JSON anyway, and the
web app is the formatted view for humans. A `--json` flag is still accepted
as a no-op for compatibility.

`report sum` groups posted journal lines by the keys you choose — `account`,
`unit`, `payee`, `month`, or a dotted field like `tax.category` — and returns
debit/credit/net totals plus a line count per group (e.g.
`--by tax.category,tax.rate --year 2026` for consumption-tax figures). Lines
missing a key form an explicit empty-keys group, so unclassified lines are
visible rather than dropped. `--year` uses the fiscal year (begins-in
convention); `--from/--to` take arbitrary inclusive dates.

**Default dates.** A date you leave out comes from the book's fiscal year
(`fiscal_year` — a book is one year). Balances (`balance`, `tb`, `bs`,
`ledger`) are as of today, where today is the date where the book is kept
(Japan time for a JP book), or as of the year's last day once that year is
over; `pl` and `sum` run from the year's first day to the same date. So last
year's book, opened in February to file its return, shows last year in full.
Give only `--to` and the range starts on
the first day of that date's fiscal year; give only `--from` and it runs
through today. An entry dated after today stays out until its date arrives.
The JSON always states the dates it used, and the web app, the MCP tools and
the remote connector use the same defaults. For filing figures, name the
period (`--year`, or `--from`/`--to`).

**Output shapes.** All five build on one row type:

```text
Balance = { account, debits, credits, type?, net? }

tb      { asOf?, rows[Balance], totalDebit, totalCredit, balanced }
pl      { from?, to?, income[Balance], expenses[Balance],
          totalIncome, totalExpense, net }
bs      { asOf?, assets[Balance], liabilities[Balance], equity[Balance],
          totalAssets, totalLiabilities, totalEquity,
          currentEarnings, balanced }
ledger  { account, asOf?,
          entries[{ date, file, payee, debit, credit, balance }],
          totalDebits, totalCredits, balance }
sum     { groupBy[], from?, to?,
          rows[{ keys[], debit, credit, net, lines }],
          totalDebit, totalCredit, totalNet, totalLines }
```

`type` and `net` on a `Balance` populate once the account is classified against
the chart. `ledger.entries[].balance` is the running balance *after* that entry,
and `file` is the journal it came from — that is the 帳簿間の相互関連性 trail.
`sum.rows[].keys` is positional: one entry per `--by` key, in the order you gave
them.

### iris search

Find journals by any combination of filters (combined with AND). Deterministic
and offline.

```bash
iris search [--from D] [--to D] [--min N] [--max N] [--payee S] \
  [--status draft,posted,closed] [--account S] [--tag S] [--json] [path]
```

The status column shows the **effective** status: a journal dated inside a
sealed fiscal year displays as `closed` regardless of what its file says, and
`--status closed` filters on exactly those.

**Output shape** (`--json`):

```text
[ { path, date, payee, status, amount, lines } ]
```

`amount` is the entry's debit total in minor units; `lines` is its line count.

### iris show

Cross-references for a path: for a document, the journals that cite it; for a
journal, the documents it cites plus siblings.

```bash
iris show [--json] <path> [path]
```

**Output shape** (`--json`):

```text
{ ref, mode,
  citedBy[{ path, date, payee, status }],
  cites[{ path, type?, locator?, alsoCitedBy[] }] }
```

`mode` says whether `ref` was read as a document or as a journal. `type` is the
attachment's provenance (`receipt`, `invoice`, `bank_statement`) and is absent
on supporting material. `alsoCitedBy` lists the *other* journals citing the same
document — how you spot a receipt booked twice.

### iris export

Export journals, trial balance, ledgers, or assets as CSV (UTF-8 with BOM).

```bash
iris export [--out DIR] [--year YYYY] [--as-of YYYY-MM-DD] [path]
iris export assets [--year YYYY] [--out FILE] [path]
```

## Fixed assets

### iris asset

Fixed-asset depreciation and reporting.

```bash
iris asset schedule [--year YYYY] [path]    # print each asset's depreciation schedule
iris asset depreciate --month YYYY-MM [path]  # generate that month's entries (status: draft)
iris asset depreciate --year YYYY [path]      # one FY-total entry per asset, dated the FY's last day
```

Pick one cadence per fiscal year: `depreciate` refuses to write annual entries
into a year that already has monthly ones, and vice versa (mixing them would
double-count).

## Region overlay

### iris overlay

The region overlay is the versioned set of country-specific rules, recipes and
derivations the book validates and computes with — pinned by `overlay:` in
`config/book.yaml`, extended by the book's own `config/overlays/` when present.

```bash
iris overlay list [--json] [path]                                   # the overlay in effect: pin, layers, rules, recipes, derivations
iris overlay recipe <id> --set name=value ... [--write <path>] [path]  # run a recipe; --write records it with provenance
iris overlay test [--json] [path]                                   # run the golden tests of every layer in effect
iris overlay test --dir <overlay-dir> [--json]                      # run one published overlay's golden tests, outside any book
iris overlay fetch [path]                                           # download + verify the version the book pins, if this iris lacks it
iris overlay upgrade [--to <id>@<version>] [path]                   # move the pin to the newest published version (or --to)
iris overlay trust [path]                                           # trust this book's config/overlays/ on this machine
```

`recipe` prints the proposal; with `--write` a schedule recipe rewrites the
asset file (`schedule:` + `schedule_source:`) and a figures recipe writes a
filing under `filings/`. Map-valued params are passed as `--set name='{"1": 90}'`.

`upgrade` and `fetch` download from the releases of the public
[`irisbooks/overlays`](https://github.com/irisbooks/overlays) repository and
check the signature before a version is used. Versions released before your
`iris` was built are included in it and never downloaded. Downloaded versions are kept in
`~/.config/irisbooks/overlays/` (never in the book) and checked again every
time they load. `upgrade` changes nothing unless the new version passes its own
tests and the book's `config/overlays/` still loads on it. `iris validate`
never downloads anything.

## Editing & promoting

### iris post

Promote journals from `draft` to `posted`, then sync (if linked). If the
book owner turned on **posting approval** (web app → Settings), posting is
web-only: `iris post` refuses locally and the server rejects any pushed
status flip with `APPROVAL_REQUIRED`.
Validates each file is non-empty and balanced first. A journal dated inside a
sealed fiscal year is refused (*"FY \<n\> is sealed (closed period) — run
`iris reopen <n>` to amend it, then re-seal"*).

```bash
iris post [--dry-run] <file>...
iris post [--dry-run] --all
```

`--all` posts every `draft` draft in the book instead of naming files —
including drafts you didn't author (phone/connector drafts, email-ingested
entries, generated depreciation). Drafts that fail validation are reported
and left as drafts. This is the ritual for books with the `auto` posting
policy.

### iris diff

Show what would be pushed — local changes versus the last-synced snapshot.

```bash
iris diff                # list all pending changes
iris diff <relpath>      # line-level diff for one file
iris diff --paths        # names + kind only
```

## Sync & conflicts (cloud)

### iris sync

One explicit pass: push local changes, pull remote changes, report per-file
accept/reject. Needs the book linked to the cloud and you signed in.

```bash
iris sync [--quiet] [--json] [--allow-bulk-delete] [path]
```

Exit codes: `0` clean · `1` rejections/conflicts/IO · `2` usage/setup · `3`
terminal disconnect (book deleted, access revoked, session expired).

If a sync would delete most of the book's cloud files at once, the server
refuses those deletions (`BULK_DELETE_REFUSED`) as a safety net. When the mass
deletion is really what you want, re-run with `--allow-bulk-delete`.

**Output shape** (`--json`) — one document that replaces all of the above, and
the one your AI reads after every edit:

```text
{ status, counts{ pushed, pulled, deleted, conflicts }, queueLeft,
  disconnected, disconnectReason?,
  newRejections[], allRejections[], applyErrors[], blockedByConflicts[],
  error? }
```

- `status` — `ok` | `rejected` | `conflicts` | `disconnected` | `error`
- `disconnectReason` — `deleted` | `forbidden` | `auth_expired`
- `newRejections` / `allRejections` — attention records, the same shape
  `iris attention list --json` returns
- `blockedByConflicts` — canonical paths with an unresolved `.conflicted`
  sidecar. **Non-empty means the whole pass was a no-op**: nothing was pushed
  or pulled, so merge or resolve first.
- `applyErrors` — remote changes that failed to land locally. The working tree
  may be incomplete; re-run rather than trusting the files as they stand.

This is why an edit → sync → read loop needs no second call: the per-file accept
*and* reject are both in this one response.

### iris conflicts

When a push conflicts (409), the server version takes the canonical path and
your version becomes a `.conflicted` sidecar.

```bash
iris conflicts list [path]
iris conflicts resolve <path> --keep mine|cloud [path]
```

The usual resolution is to merge by hand (edit the canonical file, delete the
sidecar, `iris sync`). See
[Troubleshooting](troubleshooting.md#sync-conflicts).

### iris attention

Manage the local queue of server-side rejections.

```bash
iris attention list [path]              # show path + code + issues
iris attention retry [path]             # drop suppression; the next `iris sync` re-pushes
iris attention retry --path <relpath> [path]   # just one file
```

**Output shape** (`list --json`):

```text
{ records[ { path, local_fs, local_sha, code?,
             issues[{ field, message, rule? }], detected_at, reason? } ] }
```

`code` is the server invariant that refused the file — `UNBALANCED_JOURNAL`,
`UNKNOWN_ACCOUNT`, `PERIOD_SEALED`, `BULK_DELETE_REFUSED`, and so on.
`OVERLAY_RULE` means a region-overlay rule refused it (the published overlay's
or your book's own in `config/overlays/`); each issue's `rule` names the rule,
which `iris overlay list` shows.

### iris yearend

End a fiscal year by starting the next year's book — the accounting half of
a year-end close (the compliance half, locking the year, is `iris api seal`).
A book covers one fiscal year, so `iris yearend` creates the next one as a
standalone copy, in a new folder beside this one (`acme-2025` →
`acme-2026`; `--to` picks the folder). The new book gets:

- `config/` — `book.yaml` with `fiscal_year` advanced and its own book ID,
  the chart of accounts, `rules.yaml` and `config/overlays/`;
- the guides (`README.md`, `LLM-GUIDE.md`, `CLAUDE.md`) and the policy notes
  (`decisions.md`, `workflow.md`, `todos.md`, `open-questions.md`);
- the fixed assets still held when the new year starts;
- an opening-balances journal (期首残高) at
  `journals/<YYYY-MM>/0000-opening-balances.md`, dated the new year's first
  day and tagged `opening-balance`. Balance-sheet accounts carry forward at
  their closing balance (with quantities for currency, crypto and other
  unit-tracked holdings); income and expense reset to zero; net income folds
  into the equity account named by `opening_balance_equity_account` in
  `config/book.yaml` (or the book's sole equity account).

Entries already dated in the new year **move** to the new book, with the raw
files they cite. Earlier journals, `compiled/`, `filings/`, parse caches and
disposed assets stay here. `--carry notes,raw` copies all of `notes/` or
`raw/` as well.

If this book is linked to the cloud, the same run creates the new book's
cloud copy — everyone with access to this book gets the same access, and
this book's inbound email address moves to the new one — then syncs both
books. It asks first; `--yes` skips the question (needed when no terminal is
attached), and `--local` makes only the local book.

Nothing links the two books afterwards. To carry a late correction to the
old year, fix it in the old book and run `iris yearend` again with the same
`--to`: the new book's opening entry is refreshed (identical results are a
no-op), and entries dated in the new year that appeared in the old book since
are moved. The new book's config and notes are left as they are. Once the new
year is sealed, its opening entry is frozen — a mismatch is reported with
remedies, never silently rewritten. Unposted drafts dated in the closed year
are warned about (they don't carry).

`<fiscal-year>` is optional — it defaults to the book's `fiscal_year`, and
naming any other year is refused.

```bash
iris yearend [<fiscal-year>] [--to PATH] [--carry notes,raw] [--yes | --local] [path]
```

### iris reopen

Unlock a sealed fiscal year for amendment. The seal is unlocked on the server
(the year’s journals and `config/`, `assets/`, `filings/`, `compiled/` are
locked until this runs; edits to that scope after reopening are permanently
flagged as post-seal edits). `raw/` and `notes/` remain writable throughout.
The year's files never
left the working tree — sealing locks the year, it does not remove files —
so there is nothing to restore: edit them directly, run `iris sync` to push
your edits, and `iris api seal` to close the year again.

```bash
iris reopen <fiscal-year> [path]
```

## Prices (Net Worth)

### iris price

Record/list unit prices offline, and sync them to the server. User-scoped (not
stored in the book).

```bash
iris price add --unit BTC --price 9850000 [--currency JPY] [--date YYYY-MM-DD] [--source S]
iris price list [--unit BTC] [--json]
iris price sync
```

**Output shapes.** `list --json`:

```text
[ { unit, currency, date, valueMicro, source?, origin, recordedAt } ]
```

`valueMicro` is the value of **one whole unit** × 1,000,000, so a ¥9,850,000
bitcoin is `9850000000000`. `origin` is `local` (captured on this machine) or
`server`. `sync --json` returns `{ pushed, pulled }`.

## MCP server

### iris mcp

Run a Model Context Protocol server that exposes the `iris` verbs to a BYO
agent, pinned to one book.

```bash
iris mcp serve [--book PATH] [--http 127.0.0.1:PORT]
```

Local tools: `validate`, `diff`, `balance`, `report`, `status`, `check_update`. Asset tools:
`asset_schedule` (the engine's per-asset figures) plus three depreciation
calculators — `declining_table`, `flat_table`, `straight_line_table` — your AI
composes into a recorded `schedule:` for methods no recipe covers. Recipe
tools: one per recipe of the book's overlay (`jp_teiritsu`,
`jp_shouhizei-general`, `jp_shouhizei-simplified`), each recording its result
with provenance when given a `write` path. Cloud tools (when authenticated):
`sync`, `seal`, `export_from_cloud`.

With `--http`, the server listens on a localhost address instead of stdio and
accepts only requests carrying the header `Authorization: Bearer <token>`. The
token is created the first time you start it, in
`~/.config/irisbooks/mcp-http.token` (readable only by you), and stays the same
after restarts, so set it once as a header in your MCP client. Delete the file
to get a new token on the next start, then update the header in your MCP client
to match.

### iris version

```bash
iris version
```

---

# Cloud commands (`iris api …`)

These operate on a **book ID** and require authentication.

## Account-scoped

### iris api login

Browser-assisted sign-in. This device gets its own CLI session:
signing out of the web app does not affect it, it expires only after
90 days unused (each use renews it), and you can revoke it in the web
app under your Settings (avatar menu) → API tokens.

```bash
iris api login
iris api whoami     # validate the cached token
iris api logout     # revoke this device's session and remove the token
```

For a cloud agent or a browser that blocks localhost callbacks, use file delivery
(the browser's download folder must be accessible to the CLI):

```bash
iris api login --handoff-file
# Open the printed URL, sign in, and allow access. The browser downloads iris-login.json.
iris api login --complete /path/to/downloads/iris-login.json
iris api whoami
```

Pass only the downloaded file's path; the CLI reads it and stores the session
credential internally. The file contains a single-use authorization code, not
a session token. It is bound to the private PKCE verifier retained by the CLI
and expires 5 minutes after approval. The pending login expires 10 minutes
after starting; starting again replaces it, so use the new URL and download.
Completion uses the environment selected when login started. Cancel on the
consent page downloads a cancellation result; completing that file clears the
pending login without saving a credential. After completion, remove the
downloaded file. Normal `iris api books …` and `iris sync` then work unchanged.

### iris api books

List or create cloud books, or link a local book to one.

```bash
iris api books list [--json]
iris api books new [flags]
iris api books link [--force] <book-id> [path]
```

Run `new` from inside a local book that has no cloud id yet and the new book
is linked to that folder automatically — the same effect as `books link`, so
the next `iris sync` just works. The cloud book is created from that folder's
`config/book.yaml` (name, fiscal year, region, currency, individual or company,
fiscal-year start), so no flags are needed; a flag that contradicts the file is
refused. It starts empty, and that first sync pushes the folder's own files.
`--no-link` skips all of this. Run `new` from inside a
book that is *already* linked and it refuses: a second cloud book there would
sit empty while `iris sync` keeps pushing to the first.

Outside a book folder, provide at least `--name` and `--fy`:

```bash
iris api books new --name "Acme Design" --fy 2026 --region JP
```

Other flags are `--currency`, `--book-type PERSONAL|BUSINESS`, `--scale`,
`--no-link`, and `--idempotency-key`. Creation prints a retry key; retain it
and reuse `--idempotency-key <key>` if the result is uncertain, to avoid a
duplicate book. Inside a local book, the default key is derived from its
stable local ID, so retrying the same creation uses the same key.

### iris api token

List or revoke your Personal Access Tokens. Minting a new PAT is
web-only (your Settings → API tokens); revocation is available here too so an
automated run can revoke the PAT it used when it finishes. Requires a
signed-in session or a Full-access PAT.

```bash
iris api token list [--json]
iris api token revoke <token-id>
```

### iris api config

Show or set per-user preferences (reporting currency, default unit scales).
Merged into new books at `iris init`.

```bash
iris api config
iris api config set --base-currency USD
iris api config set --set-unit BTC:8,XAU:4
iris api config set --remove-unit XAG
```

## Per-book

### iris api grants

Manage book access (owner-only).

```bash
iris api grants list [--json] <book-id>
iris api grants invite --email EMAIL <book-id>
iris api grants role --user USER_ID --to OWNER|BOOKKEEPER|REVIEWER <book-id>
iris api grants revoke --user USER_ID <book-id>
```

### iris api inbox

Inbound email for a book: show the receiving address, manage the sender
allowlist, and review quarantined mail. See "Receipts by email".

```bash
iris api inbox show [--json] <book-id>
iris api inbox allow <pattern> <book-id>       # user@host or *@host
iris api inbox disallow <pattern> <book-id>
iris api inbox quarantine [--json] <book-id>
```

### iris api seal

Close a fiscal year (period seal). The server locks journals dated in the year
and `config/`, `assets/`, `filings/`, `compiled/`. `raw/` and `notes/` remain
writable. Local files can still be edited, but locked changes cannot sync;
the year's files stay in your working tree. To amend a sealed year, run
`iris reopen <fy>` — changes to the locked scope while reopened are flagged
in the audit trail
(`iris api history`) — then re-run this command to close the year again (the
new seal supersedes the old one). `--preview` lists the files the seal
would lock, without sealing. Sealing is **refused** while the year
still contains `draft` drafts — a sealed year must be fully resolved. Post
each draft if it belongs in the year, delete it if abandoned, or change its
date into an open year; `--preview` lists the blockers.

Before previewing or closing, recorded filings must replay successfully against
the cloud's current posted journals and recipe sources. A stale filing after a
correction, or an unavailable recipe source, can block even the preview before
it lists drafts. Re-run the filing recipe with the intended inputs, run
`iris validate`, sync the filing and its inputs, and preview again. If the
cloud still reports an unavailable replay projection after a successful sync,
seek support from the [Discord community](https://discord.gg/wZDsv9gyb9); repeated close attempts will not repair it.

```bash
iris api seal --period YYYY [--type yearly] [--preview] <book-id>
```

### iris api balance / holdings / history

```bash
iris api balance [--as-of YYYY-MM-DD] <book-id>              # server-side trial balance (JSON output)
iris api holdings [--as-of YYYY-MM-DD] [--json] <book-id>    # per-unit net positions
iris api history [--path PATH] [--from D] [--to D] [--all] [--limit N] [--json] <book-id> # durable correction/deletion record
```

**Output shapes:**

```text
balance   [ { account, debits, credits, type?, net? } ]
holdings  [ { account, unit, quantity } ]
history   [ { id, path, op, sha?, version_id?, size_bytes,
              actor, actor_display?, source?, reason?,
              post_seal_period?, moved_from_path?, ts } ]
```

`holdings` counts only unit-tagged lines, and positions that net to zero are
omitted server-side.

In `history` — the durable correction/deletion record — `actor` is the stable
account identifier (the audit identity) and `actor_display` is the server's
read-time resolution of it to a name or email, for human readers.
`post_seal_period` is set when the change landed *after* that fiscal year was
sealed; that is the flag an auditor looks for. `moved_from_path` records a
rename rather than a delete plus a create.

`history` returns the newest 100 events unless you narrow it:

- `--path` — one file's timeline.
- `--all` — every event. A book is one fiscal year, so this is the year's
  whole record, corrections made after it was closed included.
- `--from` / `--to` — changes made between two dates, in the book's time
  zone (Japan time for a JP book).

With `--from`, `--to` or `--all` it returns every matching event;
`--limit` still caps it when you give one. To hand the record over as a file,
for example when a tax office asks for it, write it out as JSON:

```bash
iris api history --all --json <book-id> > history-2025.json
```

`books list --json` emits a stable list with `bookId`, `fiscalYear`, `role`,
`name`, `region`, and `currency`. The other cloud commands' `--json`
(`grants list`, `token list`, `inbox show`, `inbox quarantine`) passes the
server's response through unchanged.

### iris api export

```bash
iris api export [--out DIR] [--year YYYY] [--as-of YYYY-MM-DD] <book-id>  # CSVs
```

With `--year`, the export is restricted to journals dated in that fiscal
year. Sealed years stay in the live tree, so they export like any other
year.

### iris api price / networth

```bash
iris api price add --unit BTC --price 9850000 [--date YYYY-MM-DD] [--source S]
iris api price list [--unit BTC] [--json]

iris api networth [--as-of YYYY-MM-DD] [--json]              # cross-book total
iris api networth --book <book-id> [--as-of YYYY-MM-DD] [--json]
iris api networth settings [--include|--exclude|--reset <id>]
iris api networth history [--months N] [--refresh] [--json]
iris api networth movers [--as-of D] [--compare D] [--json]
```

`networth` values each book's balance sheet — assets minus liabilities,
leaving out `owner: true` accounts — with unit holdings at your recorded prices
(`basis: price`) and everything else, or a unit with no price, at book value
(`basis: book`). A book counts only inside its own fiscal year; the cross-book
total lists the books it leaves out under `excluded`, with the reason
(`year_ended` or `year_not_started`). Movers compare by account and unit across
books, so moving to next year's book isn't shown as a sale.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `IRIS_API_TOKEN` | Personal Access Token; takes precedence over the cached login token |
| `IRIS_BOOK` | Default book ID for cloud commands (a positional arg still wins) |
| `IRIS_API_ENDPOINT` | API endpoint override; takes precedence over everything below |
| `IRISBOOKS_APP_BASE` | App base URL (default `https://irisbooks.jp`) |
| `IRISBOOKS_API_BASE` | API base URL (default `<app-base>/api`) |

When none of the endpoint variables are set, commands use the endpoint
saved by your last `iris api login` — so a session signed in to one
environment keeps talking to that same environment.

## Common exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success |
| `1` | Validation errors, rejections, or I/O failure |
| `2` | Usage or setup error (not in a book, bad flags) |
| `3` | Terminal disconnect — sync commands only (book deleted, access revoked, session expired) |
