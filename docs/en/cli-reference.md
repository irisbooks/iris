# CLI command reference

Every `iris` command, grouped by purpose. `iris --help` separates books,
bookkeeping, reports, sync, portfolio, AI integration, cloud administration and
installation. Command placement does not imply that it is offline.

- Local book commands accept `--book-path PATH` or their documented positional
  book path. With neither, they find the nearest book above the current folder.
  Portfolio commands accept `--books-dir PATH` or an explicit list of folders.
- Per-book cloud commands (`iris api …`) accept `--book-id ID`, their positional
  cloud ID, or `IRIS_BOOK`. Account commands need no book selector. Cloud access
  requires `iris api login` or `IRIS_API_TOKEN`.
- `clone`, `sync`, and `reopen` use the network. `post` syncs the whole linked
  book after posting; `--local` skips that sync. Linked `yearend` creates/syncs
  the next cloud book unless `--local` is chosen. `price sync`, package downloads
  and `update` also use the network.

Run `iris <command> --help` or `iris help <command>` for current invocation
details. Help works offline without a book or login, writes to stdout and exits
0. Flags may precede or follow arguments; `--` makes the remaining arguments
literal. Boolean values use `--flag=true` or `--flag=false`.

Calculations and repairs (`journal complete`, `organize`, `financial prepare`,
`overlay recipe`, and derived values in `validate`) write only with `--apply`.
Recipes also need `--out PATH`; retained financial calculations need the reviewed
`--revision`. Action commands such as `post`, `yearend`, `overlay select`,
`overlay upgrade`, and `api seal` perform their named action; `--dry-run` previews
it. `yearend` carries balances into the next book; `api seal` separately locks
the current year, and `reopen` unlocks it for amendments.

`report`, `balance`, `reconcile`, `allocation`, `context`, `financial`,
`journal complete`, `networth` and `analytics export` always emit JSON. Other
inspection commands document their optional `--json`; `sync issues list`,
`conflicts list` and `api config show` support it. Successful data goes to stdout;
errors go to stderr. Exit 0 means success, 1 an operation/check failure, 2 invalid
arguments/setup, and 3 a terminal sync disconnect.

The command names are `journal complete`, `references`, and `sync issues`.
The former `autocomplete`, `show`, and `attention` names are removed. Folder
selectors use `--book-path`; the former ambiguous `--book` flag is removed.
Closing previews use `api seal --dry-run`; calculation writes use `validate
--apply`, `financial prepare --apply`, and `overlay recipe --out PATH --apply`.

Commands that emit JSON share one convention: **amounts are integers in the
book currency's minor units** (¥1,200 is `1200` at scale 0; $12.00 is `1200` at
scale 2), dates are `YYYY-MM-DD` strings, and the document is pretty-printed
with a two-space indent. The output shapes below are written as key skeletons —
`?` marks a key that is omitted when empty.

## Setup

### iris docs

Read the English LLM reference bundled with the running executable. No book,
login, network or downloaded cache is required. Chapters match that binary's
release; Japanese human-facing docs remain online.

```bash
iris docs                                      # list topics
iris docs cli-reference                         # list section IDs and word counts
iris docs cli-reference --full                  # explicitly read the whole chapter
iris docs cli-reference --section iris-sync     # one section + its subsections
iris docs --json cli-reference --section iris-sync
```

Flags may precede or follow the topic. A topic returns its section outline by
default; `--list` explicitly requests the same outline. `--section` reads one
section and its children; `--full` explicitly reads the chapter. These modes
cannot be combined. Topic/section lists include word counts. JSON includes
`version`, `source: "bundled"`, `language: "en"`, `words`, and `topics`,
`sections` or `markdown` according to the request. Unknown selectors
exit 2 with discovery guidance; they never fall back to the full manual.
Use `iris <command> --help` for invocation details and current online docs for
changing cloud access/authorization. Docs are reference, not permission to act.
Local MCP exposes the same lookup as `read_docs(topic?, section?, outline?, full?)`,
without a book selector. A topic defaults to its outline; `full=true` opts into
the complete chapter. Offline cross-references show `iris docs` commands; use
the same topic and section with MCP.

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
selects the download base (default `https://irisbooks.io/dl`); the release
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
| `--preset` | Setup intent: `personal` (household chart) or `business` (default). Legal entity and tax status remain independent |
| `--language` | Language (ISO 639-1) |
| `--chart` | Starter-chart variant, where the region offers several — JP: general / it / food (default general). A region without a chart of its own gets a neutral starter chart |
| `--currency` | Currency (ISO 4217; default per region) |
| `--fiscal-start-month` | Fiscal-year start month 1–12 (default 1, January — pass `4` for a year that starts in April) |
| `--fiscal-year` | The fiscal year the book covers (YYYY; default: the one holding today) — e.g. last year's, when you're catching up on its filing |
| `--sample` | Seed ~40 demo journals for the business chart; unavailable with personal setup |
| `--posting` | Posting policy written into AGENTS.md: `approve` (default — you review and post) / `auto` (your assistant posts everything that validates) |
| `--book-id` | Pre-link to an existing server book (advanced) |

The interactive wizard, parent-MCP `create_book` and explicit Web/API creation
use the same static planner. Personal setup selects the common package and
household accounts; business setup selects the common and available regional
packages. Exact copies are stored before the selecting config. The config's
`creation` marker records the initial preset/version; edits, clone and year-end
use the actual Book files without reapplying it. Setup guidance leaves tax
applicability, evidence and account mappings for explicit decisions.
Init also prints the selected/resolved package sources and up to three task
links from the shared context resolver. Older sources without task metadata
show that discovery limit; the output never invents a task from a newer release.

For a fresh cloud book, `iris api books new --preset personal --name "Household"
--fy 2026` uses the same choice. `--chart general|it|food` and `--language en|ja`
are available for fresh creation. When connecting an existing local book, its
actual config/chart/policy are retained and preset overrides are refused.
Cloud retries retain their original server-owned seed bytes and hashes;
starter attachment checks those files and their history before replacing the
core config/chart/policy.

### iris onboard

Wire this machine's AI assistant to the book: register `iris mcp serve` with
MCP clients and write the Claude Code skill. Claude Code's project config
(`.mcp.json`) is always written; Claude Desktop, the Codex CLI, Cursor,
Gemini CLI, and VS Code are registered when detected on the machine, or
forced with their flag.

```bash
iris onboard [--book-path PATH] [--claude-desktop] [--codex] [--cursor] [--gemini] [--vscode] [--install-path] [--no-skill] [--dry-run]
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
iris offboard [--book-path PATH] [--keep-skill] [--remove-path] [--dry-run]
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
`iris offboard --book-path PATH` first if you want that removed too.

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
`config/book.yaml`, a starter chart of accounts and `AGENTS.md`. (A cloud book created
from inside a local book starts empty and receives that folder's files on its
first `iris sync`.) Cloning preserves the synced `AGENTS.md`, including its
posting policy. Missing contracts in older books are filled before the clone
is published; local `CLAUDE.md` and `README.md` entry files are added when absent.
Existing custom files are preserved.

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
  draftCount?, remoteDeleted?, packageContext?,
  sealStatus{ fiscalYear, state, source, checkedAt?, sealId?, sealedAt?, supersedesSealId? } }
```

`archive` appears only inside an archive folder, `draftCount` only when the
drafts could be counted, and `remoteDeleted` only when the server reports the
book gone.

`sealStatus` is offline, last-known data for this fiscal year. `closed` or
`reopened` includes the active seal ID, original close time and superseded ID when
known. `checkedAt` is the successful server read or close/reopen observation time;
a failed refresh keeps the previous data and time. `unsealed` means the last
complete read found no seal. Missing, corrupt, unbound or foreign-endpoint state
is `unknown`; an old closed flag can lack references/time. `local-only` has no
cloud seal. `archive` describes the local archive marker, without claiming the
live cloud is still closed. This command does not connect or log in. Run
`iris sync` to refresh; local unsynced files may differ from the sealed sources.

Live status includes selected/resolved package sources, up to three actual
task links and context diagnostic counts. `packageContext` carries that compact
summary in JSON. It is an offline read using the same resolver as `iris context`,
not validation or an eligibility verdict. A missing copy is diagnosed without
installation; archived status skips the live lookup. Use `iris context` for the
full task index, source/view errors and metadata limits.

### iris validate

Validate a book's structure and entries: YAML, double-entry balance, account
existence, date consistency, status values, and (JP taxable books) tax
classification.

```bash
iris validate [--v] [--json] [--apply] [path]
```

`--apply` records the values the region overlay derives for you — reported as
hints, such as the consumption tax inside a line on a 税抜経理 book — into the
files, then validates again.

Overlay checks share input, execution and output limits across the entire Book.
If a limit is reached, `overlay.checks-incomplete` is an error and `--apply`
writes no proposals, including hints collected earlier. Core accounting checks
continue. Validation checks the recorded candidate; it does not run a preparation
chain to repair it. See the book-format reference for the resource limits.

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

### iris journal complete

Preview completion of an existing draft journal, using explicitly selected
Overlay definitions and native arithmetic. Money-only journals can leave one balancing amount as `null`.
The inventory overlay fills disposal cost and proposes a gain/loss line from
recorded quantities, settlement amounts and earlier posted acquisitions.

```bash
iris journal complete [--book-path PATH] [--view NAME] [--apply] [--revision HASH] <journal>
iris journal complete journals/2026-10/2026-10-21-sale.md
iris journal complete --apply --revision <preview-revision> journals/2026-10/2026-10-21-sale.md
```

The path is relative to the book. Omitted `--book-path` finds the current book;
omitted `--view` uses its default view. A selected view receives its own lines,
leaving shared lines and other views intact.

Output is always JSON: `proposal` contains the complete Markdown, `allocations`
lists quantities, costs, lots and effective methods, and `revision` identifies
the inputs and proposal. Preview writes nothing. `--apply` recalculates before
writing and refuses a stale revision; it keeps the journal a draft. It does
not post or sync. Archived books and known sealed years refuse apply.

Packages with bindings v5 preparation points can first fill missing scalar
concern fields through fixed classification/calculation stages. JSON includes
`preparation_plan` and `preparation_trace` with exact providers, consumed inputs
and proposed values. Apply saves per-field provenance in `preparation_source`;
ordinary `iris validate` can replay it from retained Book definitions. Preparation
preserves authored values and requires balanced source postings. The same preview
and revision guard are available through local MCP `complete_journal`.

**FIFO is implicit.** Configure `inventory.params.gain_account` once in
`config/book.yaml`; no journal-level method or automatic lot labels are needed.
Matching `inventory.params.method` overrides the opening method, then FIFO
applies. `accounts.exact` and `commodity` optionally narrow the scope. See
[defaults and inferred values](book-format-reference.md#defaults-and-inferred-values)
for a minimal sale example. Completion leaves recorded amounts intact and
rejects conflicts, missing settlement/fee amounts, insufficient holdings and
unknown opening acquisition basis. Use `null` on an amount you want calculated.
Fees stay explicit; short positions and zero-cost disposals are unsupported.

The public [overlays repository](https://github.com/irisbooks/overlays) supplies
`journal-balance` and `inventory-disposal` as independent completion functions.
Each requires an exact selection and Book copy under `config/overlay-packages/`.
New Books copy/select both explicitly. Removing inventory disposal keeps monetary
balancing available; removing balancing does not disable disposal calculations.
Omitted or empty selections enable neither. Embedded releases and caches never
supply runtime fallback. Specialist or trusted Book-local completions can
replace matching common completion IDs. The catalog contains only the independent function packages.

`iris overlay list --json` and local MCP `describe_overlay` list completions.
Trusted book-local or selected published `completions/*.yaml` definitions can
choose native `balance` or `inventory` primitives. A matching ID replaces the
common definition; conflicting active proposals fail. Unavailable or untrusted
selected policy must be repaired before completing a journal.

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

### iris reconcile

Check the observations in `config/balance-assertions.yaml` against a fixed local
root ledger and evidence hashes, without packages, login or network.

```bash
iris reconcile [--json] [path]
```

Output is always JSON. Results include account/date/FY, measure/unit/scale,
posted or explicit posted-and-drafts scope, normal direction, exact decimal and
integer strings for actual/expected/difference, and evidence status. Exit 1 means
a mismatch, missing/changed evidence or invalid input. An empty observations list
checks no balances. Nothing is rewritten or posted; `iris validate` also reports
failures. Local MCP `reconcile` uses the same checker in single-book and parent
mode. Cloud close previews run the same native check against the accepted cloud
snapshot and refuse unresolved observations. Sync local changes before comparing;
this does not certify Overlay policy or the authenticity of source evidence.
See [the format and complete example](book-format-reference.md#balance-assertions).

### iris allocation

Calculate a dated gross expense's business/private split without a Book, login,
evidence reads or writes. `--schema` gives the exact input contract. Amounts are
strings, scale and rounding are explicit, and the whole charge period must fit
one documented basis period. Results retain version/input identity and label
evidence unchecked. Review sources and both Books' counterpart entries separately.

```bash
iris allocation --schema
iris allocation --input raw/allocation-jan.json
iris allocation --input -     # read one bounded JSON object from stdin
```

The input is at most 8192 bytes. Invalid or ambiguous input exits 1; usage errors
exit 2. This calculator does not allocate acquisition cost or post journals.
See [the complete allocation example](book-format-reference.md#businessprivate-expense-allocation).

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
Balance = { account, debits, credits, type?, net }

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

`net` is always a number, including `0` for a cleared account. When `type`
is present it uses the account's native direction; an unclassified row uses
`debits - credits`. Current CLI clients fill an omitted legacy net before
re-emitting JSON. Existing filters can still omit an entire zero row. `ledger.entries[].balance` is the running balance *after* that entry,
and `file` is the journal it came from, so every ledger row traces back to its
journal.
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

### iris references

Cross-references for a path: for a document, the journals that cite it; for a
journal, the documents it cites plus siblings.

```bash
iris references [--json] <path> [path]
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
double-count). The writer holds the working-tree lock and refuses a known sealed
FY or a requested year outside a year-specific Book. The seal mirror is offline;
missing information does not establish that the cloud period is open.
For an explicit mixed-use manual pattern, keep gross depreciation once and
record a separate private-use reclassification; see
[the complete example](book-format-reference.md#mixed-use-equipment-with-a-full-acquisition-basis).

Native work is bounded; an invalid or excessive asset schedule is an error.
See [schedule limits](book-format-reference.md#schedule-recording-the-table-instead-of-computing-it).

## Region overlay

### iris context

Accounting packages provide the fields, checks, calculations and guidance used
by your Book. Read a compact task index, then request only the relevant task:

```bash
iris context [path]
iris context --task jp-small-asset-deduction.equipment --record assets/2026/laptop.md [path]
iris context --task jp-tax-classification.classify --record journals/2026-10/purchase.md [path]
```

The task must exist in the exact selected Book package. Older releases report
limited discovery instead of receiving metadata from a newer release. The
response separates package sources, inputs, diagnostics, supported operations
and remaining judgment. It is reference data, not permission to change or post.
Local MCP `get_book_context(task?, record?, view?)` returns the same context;
parent mode also requires `book`. `--view` selects the existing accounting view
and may be repeated for explicit composition. Context inspects asset and journal
records, or Book settings when no record is needed. It never downloads, installs, edits or posts.

Remote MCP `get_book_context(book_id, package?, task?, field?, guide?, example?)`
reads a bounded reference subset from synced Book copies. It returns stored
selection/settings, declared field/task metadata, accepted hashes and the checked
Book revision/time. An exact package source is required for a guide; an example
also requires its declaring task. Package and `book:<hash>` sources are read
without compiling their expressions. Compatibility, applicability, requiredness
conditions, view resolution, execution plans, validation and replay remain
unevaluated. Missing tax settings stay missing. Unsynced local changes are excluded;
references do not authorize actions. Current grant/token checks apply to each read.

### iris overlay

Accounting rule packages (overlays) provide versioned common and regional
rules, calculations and derived values — pinned by `overlay:` or `overlays:` in
`config/book.yaml`, extended by the book's own `config/overlays/` when present.

```bash
iris overlay install [--pin id@version ...] [path]                  # copy exact definitions into the Book; selection unchanged
iris overlay select --pin id@version [--pin ...] [--dry-run] [--json] [--revision HASH] [path]  # complete enabled set; --off disables optional packages
iris overlay example <task> <file#case> [path]                      # read a task's actual executable example
iris overlay list [--json] [path]                                   # the overlay in effect: pin, layers, rules, recipes, derivations
iris overlay guide <id[#section]> [path]                                     # read a pinned package workflow guide
iris overlay recipe <id> --set name=value ... [--out <path> --apply] [path]  # run a recipe; --apply records it with provenance
iris overlay test [--json] [path]                                   # run the golden tests of every layer in effect
iris overlay test --dir <overlay-dir> [--json]                      # run one published overlay's golden tests, outside any book
iris overlay fetch [path]                                           # download + verify the version the book pins, if this iris lacks it
iris overlay upgrade [--to <id>@<version>] [--dry-run] [--json] [--revision HASH] [path]                   # move the pin to the newest published version (or --to)
iris overlay trust [--source book:HASH] [path]                       # trust the current layer or one exact retained local source on this machine
```

`list --json` includes `pins`, `fields` with allowed values, rule conditions
and assertions, parameter schemas, and guide IDs. Local MCP exposes this
through `describe_overlay` and `read_overlay_guide`. With plural pins, `fetch`
verifies every member and upgrade checks the complete candidate set. `--dry-run`
may populate the verified cache but leaves book files unchanged. See
[book configuration examples](book-format-reference.md#configure-shared-rules-and-recipes-for-your-book)
for stored defaults and account selectors.

`recipe` prints the proposal; with `--apply --out PATH` a schedule recipe rewrites the
asset file (`schedule:` + `schedule_source:`) and a figures recipe writes a
filing under `filings/`. Map-valued params are passed as `--set name='{"1": 90}'`.

`fetch` fills the verified distribution cache only. `install` copies exact
embedded or signed release bytes into `config/overlay-packages/`; it does not
change selection. `select` checks the complete exact set, settings, dependencies
and local-layer compatibility. Omitted/empty selection and `select --off` enable
no optional packages. Core structural/accounting checks remain active.

#### Change the enabled selection

Use `iris context` / local MCP `get_book_context` to distinguish available Book
copies, enabled pins and task applicability. Installing a copy or reading a
guide does not enable its policy. Selection validates and applies in one call:

```bash
iris overlay select --off ./books/example
```

From inside the Book, `iris diff config/book.yaml` shows pending selection edits
against the last successful sync. Before the first sync, files appear as added.
After syncing, use file history to inspect earlier changes. To inspect the
definition and provenance impact before applying, preview is optional:

```bash
iris overlay select --off --dry-run --json ./books/example
iris overlay select --off --revision REVISION_FROM_PREVIEW ./books/example
```

For another selection, repeat `--pin` for **every** desired exact version,
including dependencies. Both preview and apply report before/after pins, required versions,
changed rules, recipes, derivations, completions, fields and preparation points.
A missing provider, incompatible version or cycle blocks apply; choose a complete
compatible set explicitly. No dependency is downloaded or enabled automatically.

`affected_results` inventories recorded asset schedules, filing sources and
prepared journal fields whose recorded providers would become inactive. Each
entry identifies its path, zero-based journal line (`-1` for whole records),
field and any raw `source_view` declaration. This is a provenance inventory,
not a resolved accounting view or a calculation. `retained` means verified
source bytes are present; `will-retain` means apply will preserve the current
local definition with its original parent pins. Availability, machine trust and
successful replay are separate. Missing historical sources produce a warning;
selection does not repair them. The preview neither checks the ledger nor
replays historical recipes, and does not rewrite recorded amounts or fields.

#### Apply through local MCP

Local MCP `select_overlays` validates and applies a complete `pins` array (`[]`
for off) in one call and returns the change details. Parent-folder mode also
requires `book`. The selection replaces the whole enabled set; include every
existing pin you want to keep. No preview or revision is required.

For an optional prior review, call `preview_overlay_selection`, then pass the
same pins and returned `revision` to `select_overlays`. CLI `--revision` provides
the same stale-input refusal. Apply uses the sync lock and
rechecks configuration, definitions, trust, record membership and provenance.
Archives and known sealed settings refuse changes. Seal observations are cached;
an available local write is not proof of current cloud permission or seal state.
Preview creates no runtime/cache files and never connects to a service.

The current writer refuses unresolved configuration views and YAML aliases or
merges that would alter other settings. Preview also refuses incomplete input:
at most 16 selected packages, 1,024 dependency files/64 MiB, 10,000 captured
files/128 MiB, 2,048 recorded provenance entries, 64 affected provider identities
and 2 MiB of preview JSON. Upgrade uses the same bounded source/impact review.
An empty selection is never upgraded by region.

#### Upgrade selected versions

```bash
iris overlay upgrade --to id@version --dry-run --json ./books/example
iris overlay upgrade --to id@version --revision REVISION_FROM_PREVIEW ./books/example
```

`--to` replaces one already selected package. Omitting it checks the newest
published versions of selected packages. Dependencies must remain explicitly
selected and compatible; upgrade never adds them. An exact target already
verified inside the Book works offline. Otherwise preview may download verified
release bytes into the distribution cache, while leaving all Book files unchanged.

The preview includes planned `copies`, package `golden_tests`, dependency and
retained-result impact, and `local_source` / `local_source_after` identities and
trust. Fixture test success does not validate the owner's ledger or replay its
recorded results. Scalar/plural selection formats and unrelated settings are
preserved; local parent updates retain the original local content and parents.
An active trusted layer keeps trust only for the reviewed parent change;
untrusted layers stay inactive.

Local MCP uses `preview_overlay_upgrade(to?)`, then `upgrade_overlays` with the
same `to` and required `revision`; parent mode adds `book`. CLI `--revision`
provides the same stale-review refusal. If a write fails, rollback restores only
unchanged proposal-owned bytes and preserves intervening owner edits. Verified
source copies may already have been retained. An interrupted trusted parent/pin
mismatch blocks execution instead of substituting published policy; inspect it
and make a fresh explicit review before continuing.

Runtime resolution and historical replay use only Book-contained definitions.
A missing, changed, incompatible or competing copy produces a diagnostic and
never executes a regional, embedded or cached substitute. `upgrade` checks
candidate goldens/settings, copies new definitions before selecting them and
retains old versions and local-layer content with its original parent pins.
Disabling does not remove stored fields or recorded results. Clone/sync carry
the Book copies; ordinary reads never install them. Cloud stores definitions
and results as data, runs host integrity/security guards, and does not compile
Overlay expressions or replay Overlay recipes at close.

#### Trust retained historical definitions

Cloning does not transfer another machine's local-layer trust. To replay a
recorded `book:HASH` after its active layer has changed, inspect that exact
retained definition under `config/overlay-packages/local/HASH/` and its original
parents, then explicitly trust it on this machine:

```bash
iris overlay trust --source book:HASH ./books/example
```

Use the actual identity from recorded provenance; `HASH` is a placeholder.
The command verifies the retained content and original Book-contained parents,
then records trust for that identity only. It does not select packages or change
Book sources. Missing, changed or linked sources refuse; no current definition
or distribution cache substitutes for missing history. Rollover carries retained
copies without replacing the successor's selection and checks the combined
snapshot-store limits before copying.

## Editing & promoting

### iris post

Promote journals from `draft` to `posted`, then sync the entire linked book,
including other pending changes. Use `--local` to post without syncing. If the
book owner turned on **posting approval** (web app → Settings), posting is
web-only: `iris post` refuses locally and the server rejects any pushed
status flip with `APPROVAL_REQUIRED`.
Web approval displays the stored source and submits only `status: posted` with
that reviewed file's hash. Bulk approval first displays up to 32 selected
sources and uses those same hashes. A changed file requires a fresh review;
approval never fetches and posts an unseen replacement. Ordinary browser record
creation, editing, deletion and recovery are unavailable. Make corrections in a
local client under the owner's posting policy.
Validates each file is non-empty and balanced first. A journal dated inside a
sealed fiscal year is refused (*"FY \<n\> is sealed (closed period) — run
`iris reopen <n>` to amend it, then re-seal"*).

```bash
iris post [--dry-run] [--local] <file>...
iris post [--dry-run] [--local] --all
```

`--all` posts every `draft` draft in the book instead of naming files —
including drafts you didn't author (phone/connector drafts, email-ingested
entries, generated depreciation). Drafts that fail validation are reported
and left as drafts. This is the ritual for books with the `auto` posting
policy.

Posting edits `status` in the source document, retaining other fields,
attachments, quantities, annotations and Markdown. YAML indentation may change;
scripts must parse YAML rather than match its formatting. The obsolete journal
fields `source` and `source.ref` are rejected before writing. Use an attachment
with `path: raw/bank/x.csv`, `type: bank_statement` and `locator: L2` instead
for the first data record after a one-line header. CSV `L` locators identify
physical lines, including headers and quoted record line breaks. Unknown units are
rejected without changing the journal; declare them in `config/book.yaml`.

### iris diff

Show what would be pushed — local changes versus the last-synced snapshot.
Works offline for local-only Books too: before the first sync, files appear
as added. Once changes are synced, use file history to inspect earlier versions.

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

Sync includes `AGENTS.md`, the canonical config files (`book.yaml`, `chart-of-accounts.yaml`,
`rules.yaml`, `balance-assertions.yaml`), YAML under `config/overlays/`, retained
files under `config/overlay-packages/`, Markdown under `journals/`,
`assets/`, `notes/` and `filings/`, and source bytes under `raw/`. It excludes
`.iris/`, conflict sidecars, editor/OS residue, generated `compiled/` output,
exports, and local entry files such as `README.md` and `CLAUDE.md`.
`AGENTS.md` holds shared book policy; only an Owner may change it in the cloud.

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
  `iris sync issues list --json` returns
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
iris conflicts list [--json] [path]
iris conflicts resolve <path> --keep mine|cloud [path]
```

The usual resolution is to merge by hand (edit the canonical file, delete the
sidecar, `iris sync`). See
[Troubleshooting](troubleshooting.md#sync-conflicts).

### iris sync issues

Manage the local queue of server-side rejections.

```bash
iris sync issues list [--json] [path]              # show path + code + issues
iris sync issues retry [path]             # drop suppression; the next `iris sync` re-pushes
iris sync issues retry --path <relpath> [path]   # just one file
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

Create the next year's book and carry forward opening balances. This leaves
the current year open; close it separately with `iris api seal` when ready.
A book covers one fiscal year, so `iris yearend` creates the next one as a
standalone copy, in a new folder beside this one (`acme-2025` →
`acme-2026`; `--to` picks the folder). The new book gets:

- `config/` — `book.yaml` with `fiscal_year` advanced and its own book ID,
  the chart of accounts, `rules.yaml` and `config/overlays/`;
- the guides (`README.md`, `AGENTS.md`, `CLAUDE.md`) and the policy notes
  (`decisions.md`, `workflow.md`, `todos.md`, `open-questions.md`);
- the fixed assets still held when the new year starts;
- an opening-balances journal (期首残高) at
  `journals/<YYYY-MM>/0000-opening-balances.md`, dated the new year's first
  day and tagged `opening-balance`. Balance-sheet accounts carry forward at
  their closing balance (with quantities for currency, crypto and other
  unit-tracked holdings); income and expense reset to zero; net income folds
  into the equity account marked `retained_earnings: true` in
  `config/chart-of-accounts.yaml`, or the chart's only equity account when
  none is marked. With several equity accounts and none marked, the run stops
  and asks you to mark one.

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
iris yearend [<fiscal-year>] [--to PATH] [--carry notes,raw] [--yes] [--local | --link-existing BOOK_ID] [--dry-run] [path]
```

`--link-existing BOOK_ID` reuses an untouched next-year cloud starter you own.
It checks the target before local moves and attaches config/chart/AGENTS.md before moving
entries. The existing target keeps its grants and inbound address; the preview
sets `copy_grants` and `transfer_inbox` to false. It creates no cloud book and
cannot be combined with `--local`. Re-running against the same linked successor
verifies its cloud settings and seals, then refreshes it. The successor syncs
successfully before the old linked book syncs its removals.

`--dry-run` returns a JSON preview of opening balances, moves and cloud
actions, plus the count of unposted drafts excluded. It writes nothing.

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

### iris networth

```bash
iris networth --books-dir ~/IrisBooks --as-of 2026-10-06
iris networth --currency JPY ~/IrisBooks/business-2026 ~/IrisBooks/personal-2026
iris networth history --books-dir ~/IrisBooks --months 12
iris networth movers --books-dir ~/IrisBooks --compare 2026-09-30
```

Values posted local journals and the local price log without network access.
Select immediate child books of a parent folder or supply explicit book folders.
Mixed currencies require `--currency`. Explicitly linked annual books form one
continuous position history; successor openings must reconcile and replace prior
checkpoints. Without a successor the last known holdings carry forward. Drafts are excluded. Missing prices use book value and appear in `unpriced`.
Duplicate folders/book identities are refused to avoid counting copies twice.
Output is JSON. Cloud inclusion settings do not apply.

### iris analytics

```bash
iris analytics export --books-dir ~/IrisBooks --out portfolio.duckdb --currency JPY
duckdb -readonly portfolio.duckdb
```

`export` reads posted local journals and the local price log, including unsynced
edits. Install the native DuckDB CLI or pass `--duckdb /path/to/duckdb`.
Supply either `--books-dir` or explicit book folders. The output must be a new
file. Resolve local price conflicts before exporting.

The file contains sources, journal flows, position checkpoints, prices and
coverage issues, plus a `portfolio_at` table macro. You can query or pivot it:

```sql
SELECT account, unit, valuation, cost, inventory_method FROM portfolio_at('2026-10-19', 'JPY', 0);
PIVOT journal_lines ON unit USING sum(debit-credit) GROUP BY book_id, account;
```

`iris yearend` carries complete opening lots and costs into each new book.
Each annual book works alone and contributes only within its fiscal year.
Select historical books to include their historical periods. Missing years
remain gaps; no relationship between books is stored or required.

Acquisition cost is the cost of remaining holdings. It is separate from book
value, cumulative contributions and realized profit. FIFO is the default;
an explicit matching root inventory method overrides a persisted opening
method. Moving average and specific identification are also supported, with
explicit lot selection required for specific disposals. Missing acquisition
history or opening basis remains unknown. `inventory_method` states the
effective method per position. Named Books use their current accepted default native generation. The artifact retains its view/generation identity; unaccepted or stale inputs refuse export.

### iris financial

Prepare a named view without writing, review the JSON statements and generation identity, then retain that exact generation:

```sh
iris financial prepare --view management ./my-book
iris financial prepare --view management --apply --revision GENERATION_ID ./my-book
iris financial accept --generation GENERATION_ID ./my-book
iris report pl --view management --from 2026-01-01 --to 2026-12-31 ./my-book
```

`prepare` defaults to the declared default view. A generation retains original source bytes, typed raw-evidence hashes, selected entries and native engine/state under `calculations/financial/`. Acceptance binds its exact identity; posting source journals is separate. Sources are never rewritten. Source membership, content, view definitions and evidence changes invalidate current acceptance. Historical generations remain available for native replay.

When human posting approval is enabled, retain and sync the draft, then use **Book settings → Accounting view acceptance** in Web. Only a current Owner/Bookkeeper browser session can accept there. Local acceptance records a local action, not an authenticated reviewer identity. Local MCP offers `preview_financial_ledger`, `retain_financial_ledger` (reviewed `revision`) and `accept_financial_ledger` (`generation`); parent mode also requires `book`.

Local/cloud approved reports select one accepted view; comparison composition remains local and unapproved. Report exports include view, generation, horizon and unfinished-source scope. Net Worth/analytics use each Book's accepted default. Close requires every declared view final at one source revision and pins accepted cloud versions; SQLite schema 2 stores each view and its original generation separately, with default figures in ordinary tables. Reopening permits corrections; it does not alter an existing archive.

This contract runs fixed native inventory/current-year depreciation calculations. It does not evaluate regional Overlay recipes or establish filing eligibility. Selected-view opening replay/rollover, exceptional operations, periodic allocation and chart/rule variants remain unsupported. Complete capture is bounded to 1,024 source/reference paths, 512 KiB source text, 64 assets, 8,192 selected lines, 16 MiB per evidence file/128 MiB total evidence and a 1 MiB generation. History is bounded to 1,024 generations/64 MiB. Exceeding a bound refuses complete acceptance; inputs are never truncated.

### iris price

See the [complete fund example](book-format-reference.md#fund-units-partial-sales-and-dated-valuation) for per-10,000 NAV, actual units, independent cash checks and report freshness.

Record/list unit prices offline, and sync them to the server. User-scoped (not
stored in the book).

```bash
iris price add --unit BTC --price 9850000 [--currency JPY] [--date YYYY-MM-DD] [--source S]
iris price list [--unit BTC] [--currency JPY] [--year 2026] [--json]
iris price sync [--json]
iris price conflicts [--json]
iris price resolve --unit BTC --currency JPY --date 2026-10-07 --choose local --revision 43 --edit <edit-id>
```

**Output shapes.** `list --json`:

```text
[ { unit, currency, date, valueMicro, source?, origin, recordedAt,
    revision?, baseRevision?, editId?, conflict?, pending? } ]
```

`valueMicro` is the value of **one whole unit** × 1,000,000, so a ¥9,850,000
bitcoin is `9850000000000`. `origin` is `local` (captured on this machine) or
`server`. `sync --json` returns `{ pushed, pulled, conflicts }`; unresolved
conflicts give exit code 1 after other cells have synced.

Prices are stored by observation calendar year under
`~/.config/irisbooks/prices/YYYY.jsonl`. The old `prices.jsonl` migrates on first
use and is retained. Sync downloads changes after the last successful page;
corrections to older years are included.

For concurrent edits of the same unit/currency/date, identical value and source
converge automatically. Different edits retain both candidates. Local reports
use the accepted server price for known conflicts and identify affected
positions in `priceConflicts`; history annotates each affected point and movers
include both dates. Other prices and bookkeeping reports continue working.
Inspect `price conflicts --json`, then resolve using the displayed server
revision and local edit ID. `--choose local` keeps the correction for the next
sync; `--choose server` discards it. To supply a replacement, keep local and
record the replacement before syncing. Stale resolution choices fail.

## MCP server

### iris mcp

Run a local Model Context Protocol server for one book or a parent folder of books:

```bash
iris mcp serve [--book-path PATH | --books-dir PATH] [--http 127.0.0.1:PORT]
```

Use the live tool schemas for arguments. Unknown fields and incorrect types return
a tool error before execution; strings such as `"true"` are not booleans.
The following sections cover one workflow each.

#### Select a local book

With `--books-dir`, choose an existing parent such as `~/IrisBooks`; its immediate
children are books. Call `list_books`, then pass the child folder name as `book`
on each book operation, for example `validate(book="freelance-2026")`. New books
appear without restarting. Book references cannot be paths; escaping symlinks
are refused. For accountants, restrict the parent and credentials to one client.

`--book-path` serves one book and omits the selector. An absent/empty target is
initialized automatically. The directory flags cannot be combined. Host paths
may differ from assistant-mounted paths; file access is separate from tool access.

#### Create a local book

An empty parent is valid. Use `create_book(book="freelance-2026", name="Acme",
region="JP", fiscal_start_month=1, fiscal_year=2026)` for a new child. Existing
books or non-empty folders are never overwritten; the parent is never a book.
For an existing cloud book, use the clone workflow below instead of creating locally.

#### Author and validate records

Read `AGENTS.md` and use native file tools for source inspection and draft/note
edits. Use MCP for calculations, validation and guarded workflows. `validate`,
`balance`, `report`, `status`, `diff` and `complete_journal` operate on the
selected book; completion previews before revision-checked draft application.
`post` accepts paths or an explicit all-draft sweep, respecting owner policy and
server approval. `dry_run=true` previews. `local=true` posts without syncing or
requiring sign-in; otherwise a linked book syncs automatically, including unrelated
pending changes across the whole book.

Discover the selected overlay with `describe_overlay`. Both modes expose
`list_recipes` and `run_recipe`. Listing returns canonical CLI recipe IDs and
parameter schemas. Run `run_recipe(recipe="jp-declining-balance.teiritsu",
params={...})` to preview. Add `apply=true, out="assets/2026/equipment.md"` to
record a reviewed schedule, or a path under `filings/` for filing figures.
Supplying `out` alone still previews. Keep write controls outside `params`.
Parent mode also requires `book` on both tools.
The arithmetic calculators (including `allocation`), `check_update` and `read_docs`
need no book selector.
`read_docs` returns topic/section outlines by default; select a section to read it.
For reference lookup, use file tools or CLI `iris references`.

#### Authorize cloud access

Call `auth_status` first and reuse `signed_in`. Otherwise call `login`, have the
user approve in the host browser, then require `status="signed_in"` from
`auth_status`. `login` returns an `authorization_url` and a five-minute expiry;
repeating it while pending returns the same URL. `validate=false` on
`auth_status` checks credential presence only.

`login`, `auth_status`, `logout` and `list_cloud_books` need no book selector.
Credentials stay on the host and are shared with CLI/local MCP instances.
`logout` revokes the saved session and cancels pending approval. An
`IRIS_API_TOKEN` environment credential takes precedence; use its existing
permissions, or remove it from host configuration and restart to choose browser
sign-in. Current service authorization guidance is at `/start/cloud/`.

#### Create or attach a cloud mirror

Choose the situation before changing identity:

| Situation | Tool |
| --- | --- |
| Already linked local book | `sync(book=...)` |
| Unlinked local book, new cloud mirror wanted | `create_cloud_book(book=...)`, then `sync` |
| Unlinked local book, untouched existing cloud target wanted | `list_cloud_books`, then `link_book(book=..., cloud_book_id=...)` |
| Existing cloud book, no local folder | Use `clone_book` as described below |

Creation uses the local book's settings and retains a retry key for uncertain
responses. Attachment requires Owner access, compatible fiscal/region/currency
settings and an untouched starter or target without file history. Config, chart
and `AGENTS.md` are adopted atomically before the local link changes. Populated,
edited, sealed or concurrently changed targets refuse; clone them to another
folder for comparison. No force option bypasses these checks. Creation/attachment
refuse archives and already-linked books. Inspect sync rejections and errors.

#### Clone an existing cloud book

After authorization, use `list_cloud_books`, then
`clone_book(book="freelance-2026", cloud_book_id="bk_...")` into an absent/empty
child. Do not call `create_book` first. Clone preserves synced files and policy,
adds missing local guides and initializes sync state/snapshots before publishing
the folder. Ordinary clones start clean; an older book missing `AGENTS.md` gains
a contract that remains pending for its first sync.

The result identifies the host path and book; `list_books` discovers it without
restart. Existing content, symlinks, archives or a pre-existing `<book>.partial`
entry are refused. There is no force option. Clone requires `--books-dir`.

#### Guarded changes and year-end

`list_conflicts` and `resolve_conflict` inspect/resolve sync conflicts. Keeping
mine immediately syncs; keeping cloud removes the sidecar. `list_conflicts`
returns JSON `{conflicts: [{path, local}]}`. `list_sync_issues` returns JSON
`{records: [...]}` with rejection details, and
`retry_sync_issues` inspect/clear rejection suppression; sync explicitly afterward.
Preview destructive changes and follow the book's policy.
Use `seal(period="2026", dry_run=true)` to inspect closing without sealing;
omitting `dry_run` or setting it to false executes closing.

`asset_depreciate` creates drafts. Linked-book `fiscal_years`, `history`, `seal`
and `reopen` require sign-in and the applicable server permissions. Parent-mode
`yearend(book=..., next_book=...)` previews by default; `dry_run=false` executes,
`local=true` skips cloud actions. It may move journals, copy grants and
transfer the inbox; it does not seal the old year. `link_existing` attaches only
an untouched compatible next-year target, retaining its grants/inbox. See
[year-end](cli-reference.md#iris-yearend) for the complete lifecycle.

#### Portfolio and prices

`get_networth` values local posted records, including unsynced edits, without
network/login. Use `books_dir="."` or `books=["business-2026", "personal-2026"]`
inside the configured root. Single-book mode cannot select siblings. Optional
`as_of`, `currency`, `mode="current"|"history"|"movers"`, `months` and `compare`
control the read; mixed currencies require `currency`. `get_holdings` instead
reads the selected linked cloud book.

`list_prices` defaults to the local offline log, matching CLI `iris price list`.
Use `source="cloud"` for the authenticated cloud mirror (`iris api price list`).
`record_price` records a decimal-string observation (at most six fractional
digits); `sync_prices` publishes/pulls prices separately from book sync.
Prices stay in user config, not tax book files. Cloud lists return one page;
follow `nextCursor` with the same filters. `list_price_conflicts` shows candidates;
use `resolve_price_conflict` only with the user's choice and displayed revision
and edit identifiers, then sync. Identical price/source edits converge.
Except `get_holdings`, these portfolio tools need no local book selector.

#### Local HTTP transport

`--http` listens on localhost instead of stdio and requires
`Authorization: Bearer <token>`. The token is created in
`~/.config/irisbooks/mcp-http.token`, readable only by its owner and stable across
restarts. Configure the client header once; deleting the file rotates the token
on next start and requires updating that header.

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

For an LLM running in a VM, use phone approval. The VM needs no browser,
passkey or shared download folder:

```bash
iris api login --device
# Give the user the printed IrisBooks URL and request number.
# On their own phone: sign in, enter the number, review access and approve.
iris api login --device-complete
iris api whoami
```

The user can sign in with a registered passkey or password + authenticator
code. Enter passwords and authenticator codes only in the user's browser;
never give them to the agent. Number entry alone does not approve access:
check the account, permissions and warning before approving. The device name
is supplied by the requesting device and is not verified.

`--device-complete` checks once. A waiting message with exit code 0 means
approval is still pending and no new credential was saved; wait at least five
seconds between checks. Continue only after `Authorized` and a successful
`whoami`. Requests expire ten minutes after start. Starting again replaces
the local pending request; use the latest number. Denied, expired or uncertain
completion needs a new request. Completion uses the original environment.
Only the CLI handles private proof and credential storage; do not inspect or
share its pending/token files. `iris api logout` clears local pending state.

File delivery is also available when the browser's download folder is
accessible to the CLI:

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

### Separate accounts and environments

Use **one private directory per account/environment pair**, outside every Book.
Set `IRISBOOKS_TOKEN_FILE` to that directory's token path before login and keep
it selected for completion and later CLI commands. Endpoint configuration,
pending authorization and user price state also live in the directory.
`personal.json` and `business.json` in one directory are therefore insufficient
isolation. A separate Book folder does not select a different account.

POSIX shell, selecting a personal production profile:

```bash
export IRISBOOKS_TOKEN_FILE="$HOME/.config/irisbooks/profiles/personal-prod/token.json"
unset IRIS_API_TOKEN IRIS_API_ENDPOINT IRISBOOKS_APP_BASE IRISBOOKS_API_BASE
IRISBOOKS_APP_BASE=https://irisbooks.io IRISBOOKS_API_BASE=https://irisbooks.io/api iris api login --device
# Approve on your own device, then keep the same IRISBOOKS_TOKEN_FILE:
iris api login --device-complete
iris api whoami
iris api books list
```

PowerShell, selecting the same kind of profile:

```powershell
$env:IRISBOOKS_TOKEN_FILE = Join-Path $HOME '.config/irisbooks/profiles/personal-prod/token.json'
'IRIS_API_TOKEN','IRIS_API_ENDPOINT','IRISBOOKS_APP_BASE','IRISBOOKS_API_BASE' | ForEach-Object { Remove-Item "Env:$_" -ErrorAction SilentlyContinue }
$env:IRISBOOKS_APP_BASE = 'https://irisbooks.io'
$env:IRISBOOKS_API_BASE = 'https://irisbooks.io/api'
iris api login --device
# Approve on your own device, then keep the same IRISBOOKS_TOKEN_FILE:
iris api login --device-complete
iris api whoami
iris api books list
```

The URL is an example for this service; use the intended service's actual app/API
pair. Directory names are labels; the URL configuration selects the service. Wait for `Authorized` and a successful `whoami`; a pending device check
can exit 0 without saving a credential. Confirm the account and access on the
human approval page. For another account, select a different directory such as
`.../profiles/business-prod/token.json`, then authorize that account. To return,
select the original profile path. Keep endpoint overrides cleared unless
deliberately selecting another service. Do not put credentials or authorization
downloads in `raw/`, notes, chat or any synced Book file.

Cloud API requests resolve `IRIS_API_ENDPOINT`, then `IRISBOOKS_API_BASE`, then
`IRISBOOKS_APP_BASE` plus `/api`, then the selected directory's saved
`config.json`, then the production default. Login selects its app/API through
`IRISBOOKS_APP_BASE` / `IRISBOOKS_API_BASE`; `IRIS_API_ENDPOINT` is a separate
request override, so it can send later commands somewhere else if inherited.
Successful login saves the original selection. `whoami` reports the actual API
endpoint and checks the effective credential: `IRIS_API_TOKEN` wins over a cached
session. It does not report a cached user's name for an environment token or
fall back after that token is rejected. Environment-token identity is unavailable
locally; successful authentication alone does not establish every Book permission.

Starting authorization leaves an existing session intact. Successful completion
replaces only the selected local credential; it does **not** revoke the old
server session. Revoke an unwanted old session in web Settings → API tokens.
`iris api logout` attempts server revocation and removes the selected local
session/pending login. If revocation fails, follow its warning and revoke in the
web app. Saved endpoint configuration and price data remain. Logout does not
remove `IRIS_API_TOKEN`; unset it separately if it should stop applying. Price
sync refuses a store already bound to another endpoint/user; use a fresh profile
directory instead of deleting that binding or mixing another user's data.

A local MCP server uses the host process's credential directory/environment,
not a Book setting or the VM shell's variables. Configure the chosen profile in
that host registration and restart the server; check `auth_status` for the
credential source, endpoint and validated state. CLI and MCP processes using the
same profile share its login. Book/client isolation and grants remain separate.

#### Moving a saved old-production connection

An old profile may still select `irisbooks.jp`; login now prints the resolved
app/API before authorization and the API after completion. A binary upgrade
neither transfers a server session nor changes a Book's cloud identity.
Authorize the intended service in a new private profile, run `whoami` and
`iris api books list`, and inspect that account's actual books. Do not copy an
old token into the new service or assume equal email addresses/Book IDs imply
access. Keep the old profile and a backup of local files. Prefer cloning an
accessible existing cloud Book into an absent/empty folder for comparison.
For an existing local Book, follow the [attachment rules](cli-reference.md#iris-api-books) and
explicitly choose create versus attach before relinking; inspect retained
connection state, conflicts and sync results. Do not rewrite dev/beta profiles
or overwrite another account's data to make the migration appear complete.
This is an explicit migration workflow, not automatic credential or Book copying.

### iris api books

List or create cloud books, or link a local book to one.

```bash
iris api books list [--json]
iris api books new [flags]
iris api books link [--force] <book-id> [path]
```

Run `new` from inside a local book that has no cloud id yet and the new book
is linked to that folder automatically — so
the next `iris sync` just works. The cloud book is created from that folder's
`config/book.yaml` (name, fiscal year, region, currency and fiscal-year
start), so no flags are needed; a flag that contradicts the file is
refused. It starts empty, and that first sync pushes the folder's own files.
`--no-link` skips all of this. Run `new` from inside a
book that is *already* linked and it refuses: a second cloud book there would
sit empty while `iris sync` keeps pushing to the first.

Outside a book folder, provide at least `--name` and `--fy`:

```bash
iris api books new --name "Acme Design" --fy 2026 --region JP
```

Other flags are `--currency`, `--scale`, `--no-link`, and
`--idempotency-key`. Creation prints a retry key; retain it
and reuse `--idempotency-key <key>` if the result is uncertain, to avoid a
duplicate book. Inside a local book, the default key is derived from its
stable local ID, so retrying the same creation uses the same key.

`books link` requires Owner access (and a `role:full` scope when using a PAT).
It accepts an untouched server starter or a cloud book with no file history.
Fiscal year, region, currency, scale and fiscal start must match. The server
adopts local `config/book.yaml` (including units), the chart and `AGENTS.md` together in one
revision-guarded transaction. The local ID changes only after acknowledgement.
A populated, edited, sealed or concurrently changed target refuses: clone it to
a separate folder and compare before choosing which content to keep. `--force`
only permits changing the local identity; it does not override these checks.
An identical attachment can be retried after a lost response. An older server
without the attachment endpoint refuses without changing the local link.

Sync state is bound to both the selected API endpoint and cloud book ID in
`.iris/sync/binding.json`. Changing either, or opening legacy state whose endpoint
cannot be verified, retains the entire old `.iris/sync/` directory as
`.iris/sync-before-link-<suffix>/` and starts fresh. The backup includes queued
operations, receipts, cursor, attention, snapshots and offline settings/seals.
Inspect it for recovery; never copy old receipts into a different connection.
Failed ID writes restore old state. The same ID on the same endpoint retains
state. A running sync/attachment holds a working-tree lock; another command
must finish or be retried after it exits. Local identity and book files remain.
Offline diff and guards only use state matching the current connection; run
`iris sync` after switching endpoints to establish a new baseline.
A cloud book's fiscal year is fixed; a different year requires another book.

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

Show or set per-user preferences. Reporting currency controls cross-book
reports. Default unit scales are a template copied into `config/book.yaml`
by signed-in `iris init` when available; existing books are unchanged.
Without default units, new books start with no explicit unit entries.
Known currencies still use built-in precision; templates can override their
quantity precision or declare custom units.
`--remove-unit` removes a unit from the account template, not existing books.
`iris init --no-user-defaults` skips the template.

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
iris api grants invite --role BOOKKEEPER --email EMAIL <book-id>
iris api grants role --role OWNER|BOOKKEEPER|REVIEWER <book-id> <user-id>
iris api grants revoke <book-id> <user-id>
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
new seal supersedes the old one). `--dry-run` lists the files the seal
would lock, without sealing. Sealing is **refused** while the year
still contains `draft` drafts — a sealed year must be fully resolved. Post
each draft if it belongs in the year, delete it if abandoned, or change its
date into an open year; `--dry-run` lists the blockers.

Run `iris validate` locally before syncing and closing. Local clients check
Overlay rules and replay recorded recipes using definitions retained in the Book;
the cloud does not execute those definitions or certify that those checks passed.
When `config/balance-assertions.yaml` is configured, `--dry-run` shows the native
check's exact recorded/observed/difference values, scope and evidence status for
the accepted synced sources. Unresolved balances or evidence block closing.
Correct the source records or observations locally, review the evidence, sync,
and preview again. Local unsynced changes are outside this preview. A missing or
stale native source mirror after sync needs a server projection rebuild; seek
support from the [Discord community](https://discord.gg/wZDsv9gyb9).

```bash
iris api seal --period YYYY [--type yearly] [--dry-run] <book-id>
```

### iris api balance / holdings / history

```bash
iris api balance [--as-of YYYY-MM-DD] <book-id>              # server-side trial balance (JSON output)
iris api holdings [--as-of YYYY-MM-DD] [--json] <book-id>    # per-unit net positions
iris api history [--path PATH] [--from D] [--to D] [--all] [--limit N] [--json] <book-id> # durable correction/deletion record
```

**Output shapes:**

```text
balance   [ { account, debits, credits, type?, net } ]
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
iris api price add --unit BTC --price 9850000 [--date YYYY-MM-DD] [--source S] [--revision N]
iris api price list [--unit BTC] [--currency JPY] [--year 2026] [--page] [--limit 500] [--cursor C] [--json]
iris api networth --book-id <book-id> [--as-of YYYY-MM-DD] [--json]
```

`iris api price list` follows every server page by default. `--page` returns
`{ items, nextCursor, syncCursor, hasMore, userId }`; follow `nextCursor` using
`--cursor` with the same filters. Page size is 1–1000. Each item includes its
`revision`. Creation uses revision 0; correcting an existing cell requires
`add --revision N` from the displayed row. A stale different edit fails with a
conflict; identical value/source retries acknowledge the accepted row.

`iris api networth` values one explicitly selected cloud book.
Cloud cross-book totals, history, movers and inclusion settings were removed
from the CLI. Use local `iris networth` or the web app instead.
Web and remote MCP cloud cross-book reports share at most one automatic snapshot
generation per user per UTC day. Changing dates or book selections does not
regenerate it. To include synced changes sooner, choose **Run aggregation** on
the web app's Dashboard or Net Worth page. Responses include the generation time
and next automatic refresh time.

## Environment variables

| Variable | Purpose |
| --- | --- |
| `IRIS_API_TOKEN` | Personal Access Token; takes precedence over the cached login token |
| `IRISBOOKS_TOKEN_FILE` | Selected token path; use a separate private directory per account/environment (default `~/.config/irisbooks/token.json`) |
| `IRIS_BOOK` | Default book ID for cloud commands (a positional arg still wins) |
| `IRIS_API_ENDPOINT` | API endpoint override; takes precedence over everything below |
| `IRISBOOKS_APP_BASE` | App base URL (default `https://irisbooks.io`) |
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
