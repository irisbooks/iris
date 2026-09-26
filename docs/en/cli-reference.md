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

### iris init

Create a new book. Bare `iris init` runs a guided wizard; flags skip the
prompts.

```bash
iris init [flags] [path]
```

| Flag | Meaning |
| --- | --- |
| `--name` | Book display name |
| `--region` | Region code (JP, US; default JP) |
| `--language` | Language (ISO 639-1) |
| `--entity-kind` | individual / company / partnership / trust |
| `--chart` | Chart variant: general / it / food (default general) |
| `--currency` | Currency (ISO 4217; default per region) |
| `--fiscal-start-month` | Fiscal-year start month 1–12 |
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
with `iris api books new` — server-created books are born with
`config/book.yaml` and a starter chart of accounts.

```bash
iris clone <book-id> [dest] [--force]
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
iris organize [--apply] [--fix fy-folders,extensions,empty-raw,config-typos] [--json] [path]
```

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

Report output is **JSON** (amounts in minor units — the same shape the web
API serves). There is no text-table mode: terminal column alignment is
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

**Default dates.** A date you leave out comes from the book's **working
fiscal year**: the fiscal year of your latest journal dated on or before
today, where today is the date where the book is kept (Japan time for a JP
book). Balances (`balance`, `tb`, `bs`, `ledger`) are as of today, or as of
the year's last day once that year is over; `pl` and `sum` run from the
year's first day to the same date. So while you are still entering last
year after it ended, reports show last year in full, and your first entry of
the new year moves them forward. Give only `--to` and the range starts on
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
iris export assets [--out DIR] [path]
```

## Fixed assets

### iris asset

Fixed-asset depreciation and reporting.

```bash
iris asset schedule [path]                  # print each asset's depreciation schedule
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
iris overlay trust [path]                                           # trust this book's config/overlays/ on this machine
```

`recipe` prints the proposal; with `--write` a schedule recipe rewrites the
asset file (`schedule:` + `schedule_source:`) and a figures recipe writes a
filing under `filings/`. Map-valued params are passed as `--set name='{"1": 90}'`.

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
iris attention retry [path]             # drop suppression and ask the engine to re-push
iris attention retry [path] --path <relpath>   # just one file
```

**Output shape** (`list --json`):

```text
{ records[ { path, local_fs, local_sha, code?,
             issues[{ field, message }], detected_at, reason? } ] }
```

`code` is the server invariant that refused the file — `UNBALANCED_JOURNAL`,
`UNKNOWN_ACCOUNT`, `PERIOD_SEALED`, `BULK_DELETE_REFUSED`, and so on.

### iris yearend

Write the next fiscal year's opening-balances journal (期首残高) from a
year's closing balances — the accounting half of a year-end close (the
compliance half, locking and archiving, is `iris api seal`). Balance-sheet
accounts carry forward at their closing balance; income and expense reset to
zero; net income folds into the equity account named by
`opening_balance_equity_account` in `config/book.yaml` (or the book's sole
equity account). The entry lands at
`journals/<fy+1>/<MM>/0000-opening-balances.md`, tagged `opening-balance` —
reports treat the latest such entry as the starting point for balances, which
is what makes each fiscal year self-contained.

Safe to re-run while the next year is still open: late corrections to the
closed year flow into the entry (identical results are a no-op). Once the
next year is sealed, the entry is frozen — a mismatch is reported with
remedies, never silently rewritten. Unposted drafts dated in the year are
warned about (they don't carry). Works offline; run `iris sync` afterwards
to push.

```bash
iris yearend <fiscal-year> [path]
```

### iris reopen

Unlock a sealed fiscal year for amendment. The seal is unlocked on the server
(a sealed period refuses all writes until this runs; edits made while
reopened are permanently flagged as post-seal edits). The year's files never
left the working tree — sealing locks and archives, it does not remove files
— so there is nothing to restore: edit them directly, run `iris sync` to push
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

Local tools: `validate`, `diff`, `balance`, `report`, `status`. Asset tools:
`asset_schedule` (the engine's per-asset figures) plus three depreciation
calculators — `declining_table`, `flat_table`, `straight_line_table` — your AI
composes into a recorded `schedule:` for methods no recipe covers. Recipe
tools: one per recipe of the book's overlay (`jp_teiritsu`,
`jp_shouhizei-general`, `jp_shouhizei-simplified`), each recording its result
with provenance when given a `write` path. Cloud tools (when authenticated):
`sync`, `seal`, `export_from_cloud`.

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

### iris api books

List or create cloud books, or link a local book to one.

```bash
iris api books list [--json]
iris api books new [flags] [--json]
iris api books link <book-id> [path]
```

Run `new` from inside a local book that has no cloud id yet and the new book
is linked to that folder automatically — the same effect as `books link`, so
the next `iris sync` just works. `--no-link` skips it. Run `new` from inside a
book that is *already* linked and it refuses: a second cloud book there would
sit empty while `iris sync` keeps pushing to the first.

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

Close a fiscal year (period seal) and build its archive snapshot. A sealed
period is **locked**: every write into it is refused, on every surface — but
the year's files stay in your working tree. To amend a sealed year, run
`iris reopen <fy>` — edits made while reopened are flagged in the audit trail
(`iris api history`) — then re-run this command to close the year again (the
new seal supersedes the old one). `--preview` lists the files the seal's
archive would capture, without sealing. Sealing is **refused** while the year
still contains `draft` drafts — a sealed year must be fully resolved. Post
each draft if it belongs in the year, delete it if abandoned, or change its
date into an open year; `--preview` lists the blockers.

```bash
iris api seal --period YYYY [--type yearly] [--preview] <book-id>
```

### iris api archive

Download a sealed fiscal-year archive (triggers the build and waits).

```bash
iris api archive download --year YYYY [--out DIR] [--timeout 5m] [--interval 5s] <book-id>
```

### iris api balance / holdings / history

```bash
iris api balance [--as-of YYYY-MM-DD] <book-id>              # server-side trial balance (JSON output)
iris api holdings [--as-of YYYY-MM-DD] [--json] <book-id>    # per-unit net positions
iris api history [--path PATH] [--limit N] [--json] <book-id> # durable correction/deletion record
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

The other cloud commands' `--json` (`books list`, `grants list`, `token list`,
`inbox show`, `inbox quarantine`) passes the server's response through
unchanged.

### iris api export

```bash
iris api export [--out DIR] [--year YYYY] [--as-of YYYY-MM-DD] <book-id>  # CSVs
iris api export audit <book-id>                                          # auditor bundle
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
