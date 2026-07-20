# IrisBooks — AI-facing manual

<!--
  This is the AI-FACING equivalent of the human user manual (manual/en/*.md).
  Audience: an AI assistant (Claude, Cursor, Copilot, any MCP-capable agent)
  helping a user run IrisBooks — answering product questions, operating the
  CLI, and working with book files.

  Keeping this honest: this file is a consolidation of the eleven pages in
  manual/en/. When you change a manual page, update the matching section
  here IN THE SAME CHANGE (same discipline as the en/ja mirror rule).

  Relation to other AI docs: every book also ships an LLM-GUIDE.md at its
  root — the in-book working contract (parse caches, filename rules,
  cross-reference graph, what-not-to-do). Inside a book, LLM-GUIDE.md wins
  on workflow detail; this file is the product-wide reference (plans, web
  app, cloud, compliance, full CLI) that LLM-GUIDE.md deliberately omits.
-->

## Product model — facts to reason from

- **A book is a folder of plain Markdown + YAML on disk.** There is no hidden
  database; the files *are* the accounting records. The `iris` CLI and the web
  app are two lenses onto the same folder (a third, the remote connector,
  reaches the cloud copy — see its section below). Nothing is proprietary —
  the folder can be zipped, diffed, backed up, handed to an accountant.
- **One book = one business.** A sole proprietor with a side business keeps
  two books; that's normal.
- **Double-entry.** Every transaction is one journal file; debits must equal
  credits.
- **Reports are computed, never stored.** Trial balance, P&L, balance sheet,
  and ledgers are derived from posted journals on every request — there is no
  "balance sheet file" to get stale.
- **Reports include only `posted` entries.** This is the single most common
  user confusion: a `draft` entry never appears in `iris balance`, the
  P&L, the balance sheet, or the web app's reports.
- **Sync is explicit.** Nothing uploads until the user (or you) runs
  `iris sync`, `iris post`, or clicks Sync in the app. There is no background
  watcher.
- **Seals are hard locks.** Sealing a fiscal year closes AND locks it: every
  write into the sealed year is refused on every surface (`iris post` refuses
  locally, sync pushes are rejected by the server with PERIOD_SEALED, web and
  remote-connector writes are refused too). To amend, `iris reopen <fy>`
  unlocks the seal — edits made while reopened are permanently flagged as
  post-seal edits in the audit trail — then re-seal (the new seal supersedes
  the old one).
- **The durable correction/deletion history lives on the server only** (paid).
  Local git history is *not* auditor-trustable and does not satisfy Japan's
  訂正・削除の履歴 requirement.
- **Built for Japan.** Target users are freelancers / sole proprietors
  (個人事業主) and SMBs filing 青色申告 / 確定申告, plus the accountants
  (税理士) who serve them.

### The division of labor

1. The **user** drops source documents into `raw/`.
2. The **AI** (you) reads them and proposes journal entries as files.
3. **`iris`** is the deterministic referee: validates structure and math,
   computes reports.
4. The **human** reviews and promotes entries to `posted`.

You do the transcription; `iris` checks it; the human controls what becomes
final. For forms that change yearly (tax returns, municipal variants) the
engine produces the numbers and *you* fill the form, then the result is
reconciled back against the engine's figures.

## Plans

| | Free | Personal | Pro | Pro (Accountant) |
| --- | :---: | :---: | :---: | :---: |
| Local book + AI | ✓ | ✓ | ✓ | ✓ |
| Sync + web app + period seals | | ✓ | ✓ | ✓ |
| Books you own | 1 | 2 | unlimited | 2 |
| Be invited to others' books | | up to 2 | up to 2 | up to 500 |
| Invite others to your book | | 1 | unlimited | unlimited |

- **Free** is complete offline bookkeeping: double-entry, validation, reports,
  and the offline compliance views (`iris search`, `iris show`). No account,
  no network.
- **Paid** adds: cloud sync, the web app, multi-device access, collaboration
  (roles/invites), period seals, receipts-by-email, the remote AI connector,
  Net Worth, and the durable server-side correction/deletion history that
  (optional) 優良電子帳簿 status requires.
- **Pro (Accountant)** is for 税理士 / firms: invited into up to 500 client
  books, each kept fully separate (no cross-client aggregation, by design).

When a user asks for something history- or audit-shaped ("who changed this",
"prove this wasn't edited"), the answer is the server history — a paid
capability. Don't offer git as a substitute.

## The book on disk

```text
your-book/
├── config/
│   ├── book.yaml                 # identity, region, fiscal year, currency
│   ├── chart-of-accounts.yaml    # the accounts
│   └── rules.yaml                # optional categorization hints (may be empty)
├── raw/                          # source documents; any structure, type inferred from content
├── journals/<fy>/<mm>/           # one Markdown file per entry
│   └── YYYY-MM-DD-<payee>-NN.md
├── assets/YYYY/<name>.md         # fixed assets, by acquisition year
├── notes/
│   ├── workflow.md  decisions.md  open-questions.md  todos.md
│   └── raw/<mirror of raw/>.md   # parse caches
├── compiled/                     # AI-generated reports — regeneratable, never hand-edit
├── README.md  LLM-GUIDE.md  CLAUDE.md   # human + AI guides
└── .iris/                        # runtime state — machine-local, never hand-edit, never synced
```

- In `journals/<fy>/<mm>/`, `<fy>` is the **fiscal year** containing the
  entry's accounting date (`date:`, per `fiscal_start_month`) and `<mm>` is
  the date's calendar month. Calendar-year book: copy the date's digits
  (`2026-07-15` → `journals/2026/07/`). April-start book: `2027-02-15` is
  FY2026 → `journals/2026/02/`. The folder reflects the accounting date,
  not the period the entry covers. The segments are nested folders —
  `journals/2026/07/`, never a single dashed folder like `journals/2026-07/`.
- The folder is a cache of the date in the file; the file is authoritative.
  Misplaced journals don't corrupt anything — `iris organize` moves them
  back to the canonical layout.
- The journal **filename is the entry's permanent identity** — it stays put as
  status changes.

### What syncs (paid plans)

- **Synced:** `journals/`, `assets/`, `notes/` (incl. parse caches), `raw/`
  (verbatim bytes), `config/book.yaml`, `config/chart-of-accounts.yaml`,
  `config/rules.yaml`.
- **Not synced:** `.iris/`, `README.md` / `LLM-GUIDE.md` / `CLAUDE.md`,
  `compiled/`.

### `config/book.yaml`

```yaml
schema_version: 1
book_id: lb_...                 # minted at init; immutable
name: "Acme Design"
region: JP                      # ISO 3166-1; selects tax/locale rules
language: ja                    # ISO 639-1; chart language follows this
currency: JPY                   # ISO 4217
scale: 0                        # minor-unit exponent — IMMUTABLE (JPY 0, USD 2, BHD 3)
entity_kind: individual         # individual | company | partnership | trust
fiscal_start_month: 4           # 1–12
created_at: "2026-06-20T12:34:56Z"

# Optional:
tax_id: "..."                   # opaque per region
opening_balance_equity_account: "資本:元入金"   # where `iris yearend` folds net income
strict_accounts: false          # false = allow accounts not in the chart (default is strict)

units:                          # non-currency units (forex, crypto, metals, shares)
  - symbol: BTC
    scale: 8
    name: "Bitcoin"

consumption_tax:                # JP only — see the Japan section
  status: taxable
  accounting: tax_included
  method: general
  business_class: 5
```

Region-specific blocks like `consumption_tax` ride along opaquely: the
universal engine ignores them; the region overlay reads them.

### Journal files — `journals/<fy>/<mm>/*.md`

YAML frontmatter, then a free-form Markdown body that says *why* the
transaction happened (not a restatement of the lines).

```markdown
---
schema_version: 1
date: 2026-05-04
payee: EXAMPLE.COM
status: draft                 # draft | posted
tags: [sales, withholding]
attachments:
  - path: raw/2026-05-example-com-invoice.pdf
    type: invoice               # invoice | receipt | bank_statement (a causal source)
    locator: "page=1"           # optional fragment pointer ("L47", "p3")
lines:
  - account: 資産:売掛金
    debit: 89790
  - account: 資産:事業主貸
    debit: 10210
  - account: 収益:売上
    credit: 100000
---

May invoice for the EXAMPLE.COM redesign engagement.
```

| Field | Required | Notes |
| --- | --- | --- |
| `date` | yes | `YYYY-MM-DD`; must match the filename prefix |
| `payee` | yes | Native script OK; the filename slug derives from it |
| `status` | yes | `draft` / `posted` |
| `tags` | no | Lowercase, free-form, for grouping |
| `attachments` | no | `{path, type?, locator?}`; a `type` marks a causal source, untyped = supporting material |
| `lines` | yes | ≥2; each has `account` + exactly one of `debit`/`credit` |
| `lines[].memo` | no | Per-line note |
| `lines[].quantity` + `unit` | no | Physical quantity for a unit from `book.yaml` `units` (always positive; direction comes from debit/credit) |
| `lines[].tax` | no | JP consumption tax — 課税事業者 only; see the Japan section |
| body | no | Free Markdown after the closing `---` |

**Amounts** are written in the currency's natural notation, up to `scale`
decimals. At `scale: 0` (JPY) write whole yen (`1000` = ¥1000, no decimals).
At `scale: 2`, `12.34` = $12.34 and bare `12` = $12.00 — **not** $0.12.
Internally everything is integer minor units.

**Validation** (`iris validate`): YAML parses; debits equal credits; every
account exists in the chart (or matches an alias); `date` matches the filename
prefix; `status` is valid; per-line `tax` is coherent (JP taxable books).

### Status lifecycle

| Status | Meaning |
| --- | --- |
| `draft` | Draft — being entered or still uncertain. What you propose. Not on the books; excluded from reports and balances until posted. |
| `posted` | On the books. **Only posted entries appear in reports.** |

Reviewing IS the flip to `posted` — there is no stored intermediate state.
(`working` is the pre-release spelling of `draft`; older books may still
carry it in frontmatter. It parses as `draft` and is rewritten on the next
write — always write `draft` yourself.)

Every book declares a **posting policy** in its LLM-GUIDE.md (chosen at
`iris init`, changeable by editing that section): **approve** (default —
leave entries at `draft`; the user flips them) or **auto** (post
everything that validates with `iris post --all`, every session — the
hands-off mode for users who use their assistant's output as-is).
Amending a posted entry on a normal book: demote it to `draft`, fix it,
then follow the policy for the re-flip (approve: leave it as a draft and
tell the user — their re-post approves the amendment; auto: re-post the
same session). Sealed years refuse writes — use a correcting/reversing
entry in the open period.

A book owner can additionally turn on **posting approval** (web app →
Settings): the flip to `posted` — and any edit, delete, or demote of an
already-posted entry — then works only from the web app. `iris post`
refuses locally, and the server rejects agent/PAT writes that touch posted
entries with `APPROVAL_REQUIRED`. The workflow under approval:

- **New entries** — write them as `status: draft`, `iris sync`, then tell
  the user their approval queue is the web app's Journals list (one-click
  Post / Post selected). If you already wrote `posted`, set it back to
  `draft` and re-sync.
- **Amending a posted entry** — don't edit the file; every sync write to it
  is refused, demotion included. Ask the user to amend/delete it in the web
  app, or demote it to a draft there, then `iris sync` and edit the
  draft.

`closed` is a **derived** display status, never written to frontmatter: any
journal whose date falls in a sealed fiscal year shows as `closed` — in the
web app (list, Closed filter, detail), in `iris search` (which also accepts
`--status closed`), and in the remote connector (`get_journal` returns
`closed: true`). Reopening the year makes the stored status visible again.
The web app additionally shows an `incomplete` marker for drafts that aren't
ready. Promote with `iris post <file>` or by editing the `status:` field;
`post` also balance-checks, refuses journals dated in a sealed FY, and (if
the book is cloud-linked) syncs.

### Chart of accounts — `config/chart-of-accounts.yaml`

```yaml
schema_version: 1
accounts:
  - path: 資産:普通預金        # hierarchical, colon-separated; this is the identity
    type: asset               # asset | liability | equity | income | expense
    code: "1010"              # optional external code
    aliases: [bank, 銀行, Assets:Bank]
  - path: 収益:売上
    type: income
    aliases: [sales]
```

- The account's normal side (whether debits increase it) is **derived from its
  `type`** — never declared.
- `aliases` let journals reference an account in another language or shorter
  name.
- **Never invent account paths inside a journal.** Add the account to the
  chart first, or propose it in `notes/open-questions.md` and wait for the
  human.

### Asset files — `assets/YYYY/*.md`

```yaml
---
schema_version: 1
name: "MacBook Pro 16"
category: equipment.computer       # free-form
acquisition_date: 2026-04-15
acquisition_cost: 480000
salvage_value: 1
useful_life_months: 48             # 耐用年数 4 years × 12
method: straight_line              # straight_line | declining_balance | expensed
declining_rate: 417                # basis points/month, only for declining_balance
asset_account: "資産:工具器具備品"
depreciation_expense_account: "費用:減価償却費"
accumulated_depreciation_account: "資産:減価償却累計額"
acquisition_journal: "[[2026-04-15-apple-01]]"   # optional wikilink
disposal:                          # optional, until disposed
  date: 2029-05-10
  proceeds: 50000
  journal: "[[2029-05-10-apple-disposal-01]]"
---
```

JP-specific fields (用途区分, 特例, 償却資産税 flags) ride along opaquely and
are read by the JP overlay.

### `config/rules.yaml` (optional)

Human-curated hints you *may* use when categorizing; never enforced.

```yaml
schema_version: 1
categorization:
  - when:
      payee_matches: "Amazon"
      amount_max: 50000
    propose:
      account: "費用:消耗品費"
      confidence: 0.85
```

### Parse caches — `notes/raw/<source>.md`

When you parse a document under `raw/`, write a durable, normalized view here,
mirroring the source path. Each row carries a status
(`journaled` / `ignored` / `deferred`) so re-opening the same statement never
redoes the work.

```markdown
---
source: raw/2026-04-sbi.csv
source_sha: <iris hash>
parsed_at: 2026-05-11
counts: { total: 47, journaled: 42, ignored: 3, deferred: 2 }
---

## Rows
| id | date       | description | amount | status    | target / reason                          |
|----|------------|-------------|--------|-----------|------------------------------------------|
| 1  | 2026-04-01 | Amazon JP   |  -5000 | journaled | journals/2026/04/2026-04-01-amazon-01.md |
```

### Cross-references

A journal points at its evidence via `attachments`; the link walks both ways:

- From a journal: which documents it cites.
- From a document: which journals cite it — `iris show <path>` on the CLI, the
  **Cited by** panel in the web app's Raw documents browser.

This two-way link is one of Japan's three 優良電子帳簿 requirements
(帳簿間の相互関連性). Don't leave dangling references — if a target moves or
disappears, fix the pointing side.

## Workflows

### Creating a book (CLI)

```bash
iris init                      # guided wizard in an empty directory
iris init --name "Acme Design" --region JP --language en \
  --entity-kind individual --fiscal-start-month 4     # flags skip the prompts
```

`--sample` seeds ~40 demo journals to explore and delete. `--chart` picks a
chart variant (general / it / food). `--book-id` pre-links to an existing
server book (advanced).

After init, the human should: adjust `config/chart-of-accounts.yaml` to the
business, then record **opening balances** (cash, bank, receivables, payables,
loans) as the first journal entries, tagged `opening-balance` — reports treat
the latest entry with that tag as the starting point for balance
computations, and year-end carry-forwards (`iris yearend`) get the same tag
automatically. Reconcile to the previous system's trial balance at the
cutover date if migrating. `notes/todos.md` carries a reminder. Never assume
zero balances mean an empty business — flag a missing opening balance in
`notes/open-questions.md`.

### Connecting the AI (one-time)

```bash
iris onboard
```

Registers `iris mcp serve` with MCP-capable clients (Claude Code's `.mcp.json`
always; Claude Desktop, the Codex CLI, Cursor, Gemini CLI, and VS Code when
detected or forced by flag) and writes a Claude Code skill. Every book ships
`LLM-GUIDE.md` at its root — read it before working in a book.

`iris onboard --status --json` reports what is registered where (including
whether each registration's binary still exists) — use it to diagnose a
broken integration before re-running `iris onboard`, which is always safe
(registrations update in place, never duplicate). `iris offboard` is the
inverse: it removes the MCP registrations and the skill, touching neither
book data nor sign-in. `iris uninstall` goes further and removes iris itself
from the machine (binaries, sign-in, skill, machine-level MCP registrations)
— it prints the exact deletion list and asks first, and never touches books.

### The everyday loop

1. A document (bank CSV, receipt scan, PDF invoice) lands anywhere under
   `raw/` — subfolders by date or vendor are fine; identify files by content,
   not location or filename.
2. Read the file **in full**, write the parse cache to `notes/raw/<source>.md`,
   and propose one journal per real transaction with `status: draft`. File
   anything ambiguous in `notes/open-questions.md` instead of guessing.
3. `iris validate` — fix and re-run until clean.
4. Read the books:

```bash
iris balance                                     # trial balance today (posted only)
iris report pl --from 2026-04-01 --to 2026-06-30
iris report bs --as-of 2026-06-30
iris search --payee amazon --from 2026-04-01     # find entries
iris show raw/2026-05-invoice.pdf                # what cites this document
```

Use `iris search` / `iris show` (deterministic, offline) instead of scanning
folders yourself when asked "find …" or "what cites …".

5. The human promotes: `iris post journals/2026/05/2026-05-04-example-com-01.md`
   (`--dry-run` to check without changing anything).

### Going online (paid)

```bash
iris api login            # browser sign-in; this device gets its own CLI session
iris api books new        # create a cloud book…
iris api books link <book-id>   # …or link this folder to an existing one
iris sync                 # one explicit push + pull pass
```

- `iris sync` pushes local changes, pulls remote ones (e.g. entries the
  accountant added in the web app), and reports per-file accept/reject.
- `iris diff` shows exactly what *would* be pushed before syncing.
- `iris clone <book-id>` fetches a server book to disk (lifecycle peer of
  `init`). Works immediately on a brand-new book created in the web app or
  with `iris api books new` — server-created books are born with
  `config/book.yaml` + a starter chart of accounts.
- The local file-first workflow doesn't change — the book simply gains sync,
  the web app, collaboration, seals, and the durable history.

### Sync conflicts

When a push conflicts (409), **the server version takes the canonical path**
and the local version becomes a `<file>.conflicted` sidecar. `iris sync`
refuses to proceed while any sidecar exists — nothing is lost.

```bash
iris conflicts list
# usual resolution: merge by hand — edit the canonical file, fold in what you
# need from the sidecar, delete the sidecar, then `iris sync`.
iris conflicts resolve <path> --keep mine     # or take one side wholesale
iris conflicts resolve <path> --keep cloud
```

### Server-side rejections (the attention queue)

`iris validate` checks *file* state; the server runs additional rules on push
(chart-projection orphans, a journal referencing a `raw/` file that isn't
uploaded, schema/immutability violations). A rejected push shows up as a
`iris validate` footer like *"N file(s) blocked in the sync queue"* — the
files are fine; the *push* was rejected.

1. `iris attention list` — read the field-level reason.
2. Fix the cause (commonly: add the missing account to the chart, or make sure
   the referenced `raw/...` file is present and synced).
3. **Re-save the rejected journal** — its content hash changes, the engine
   drops the per-file suppression, and the push retries on the next sync.
4. If the fix was in a *different* file and the rejected journal won't be
   re-saved: `iris attention retry` (or `--path <relpath>` for one file).

### Fixed assets and depreciation

Describe each depreciable asset in `assets/YYYY/<name>.md` (schema above),
then:

```bash
iris asset schedule                       # each asset's depreciation plan
iris asset depreciate --year 2026         # annual: one FY-total entry per asset at FY end
iris asset depreciate --month 2026-05     # monthly: that month's entries
iris export assets                        # per-asset schedule as CSV
```

Annual filers (most JP sole proprietors and small companies) use `--year` —
one FY-total 決算整理 proposal per asset, dated the FY's last day, mid-year
acquisitions prorated by month. Books that close monthly use `--month`. One
cadence per fiscal year: the command refuses to mix the two (double-count
guard). Generated entries are proposals (`status: draft`) the human reviews
and posts like any other journal.

### Exporting

```bash
iris export                 # journals.csv, trial-balance.csv, ledger-*.csv
iris export --year 2026     # restrict to a fiscal year
iris export assets          # per-asset depreciation schedule
```

CSVs are UTF-8 **with a BOM** so Excel opens Japanese correctly. On a paid
plan, `iris api export audit <book-id>` produces the auditor-facing bundle
(see Year-end close).

### Receipts by email (paid)

Every cloud book has a private receiving address, generated at book creation,
never changes, looks like `k7f3x9q2m4p8w1r5@in.irisbooks.jp` (random so it
can't be guessed and spammed — treat as semi-secret).

```bash
iris api inbox show <book-id>                        # the address
iris api inbox allow billing@stripe.com <book-id>    # exact sender
iris api inbox allow '*@amazon.co.jp' <book-id>      # whole domain
iris api inbox disallow '*@amazon.co.jp' <book-id>
iris api inbox quarantine <book-id>                  # review rejected mail
```

A message is ingested only when **all three** hold: (1) sender matches the
allowlist (which starts with the user's own login email, so self-forwarding
works out of the box); (2) SPF, DKIM, and DMARC all pass; (3) the virus scan
(GuardDuty malware protection) is clean. Everything else lands in quarantine —
nothing is silently dropped. Managing the allowlist needs write access
(OWNER or BOOKKEEPER). Also manageable in the web app under
**Settings → Inbound email** (with one-click "Allow sender" from quarantine).

Each accepted message becomes one folder:

```text
raw/email/2026-07/<message-id>/
├── email.md          # envelope (from, to, date, subject, attachment list) as frontmatter + message text
├── receipt.pdf       # attachments, decoded and ready to reference
└── invoice-0042.pdf
```

Read `email.md` for context and journal the attachments with references to the
exact file. Files arrive locally on the next `iris sync`. Attachments over
10MB are skipped (noted in `email.md`); the original message is retained
server-side as the audit copy.

Quarantine reasons:

| Reason | Meaning |
| --- | --- |
| `sender_not_allowlisted` | Sender matched no allowlist pattern. Allowlist and re-send. |
| `auth_fail` | SPF/DKIM/DMARC failed — possibly spoofed, or mangled by an auto-forwarding rule. |
| `malware` | Virus scan found a threat; the message never touched the book. |
| `scan_failed` | Scan couldn't complete (e.g. password-protected archive). |
| `ingest_failed` | Passed the gate but writing to the book failed. |

Caveat worth volunteering: **automatic** forwarding rules (re-sending as the
original sender) often break SPF → quarantined as `auth_fail` even when
allowlisted. Manual forwarding from the user's own mail client works, because
the mail is then authenticated as coming from them.

### Year-end close

The close has an accounting half (free, offline) and a compliance half
(paid, cloud):

1. **Carry forward — `iris yearend 2025`.** Writes FY2026's opening-balances
   journal (期首残高, `journals/2026/MM/0000-opening-balances.md`, tagged
   `opening-balance`) from FY2025's closing balances: balance-sheet accounts
   carry at their closing net, income/expense reset to zero, net income folds
   into `opening_balance_equity_account` (or the sole equity account).
   Reports treat the latest opening-balances entry as the starting point for
   balance computations, so each fiscal year is self-contained and a closed
   year's figures never shift when an earlier year is amended. Safe to re-run
   while the next year is open (late corrections flow in); once the next year
   is sealed the entry is frozen — mismatches are reported, never silently
   rewritten. Warns about unposted drafts (they don't carry).
2. **Seal + archive (paid).** Sealing marks the period closed — by whom,
   when — and **locks** it: every write into the sealed year is refused on
   every surface. An archive snapshot (zip + queryable SQLite) is built
   server-side. The working tree is untouched. Sealed-year entries display as
   `closed` everywhere.

```bash
iris yearend 2025                                 # write FY2026's opening balances
iris sync                                         # push the entry
iris api seal --period 2025 --preview <book-id>   # see exactly what will be sealed
iris api seal --period 2025 <book-id>             # seal it
iris api archive download --year 2025 <book-id>   # download the sealed archive zip
```

Sealing is REFUSED while the year still contains `draft` drafts
(UNRESOLVED_DRAFTS) — a sealed year must be fully resolved. Post each draft
if it belongs in the year, delete it if abandoned, or change its date into an
open year, then seal again; `--preview` lists the blockers.

To amend a sealed year:

```bash
iris reopen 2025      # unlock the seal; the year's files are already in the working tree
# …make corrections…
iris sync             # the server flags these as post-seal edits
iris yearend 2025     # refresh FY2026's opening balances (while 2026 is still open)
iris api seal --period 2025 <book-id>   # close the year again (supersedes the old seal)
```

`iris reopen` unlocks the seal (writes are accepted again, permanently
flagged as post-seal edits in `iris api history`); there is nothing to
restore because sealing never removes files. Post-seal edits are allowed and
auditable, not hidden — badged in the web app's Activity log and per-journal
History. Re-sealing supersedes the old seal in the audit chain. If the NEXT
year is also sealed, `iris yearend` leaves its opening entry frozen as filed
and reports the mismatch — book a current-period correction (前期損益修正)
or reopen that year too.

**Audit handoff:** `iris api export audit <book-id>` bundles a per-fiscal-year
snapshot (queryable SQLite), Excel-friendly CSV views, and the complete event
log including post-close edits — a self-contained package for an auditor or
税理士.

## Japan tax & compliance

### 優良電子帳簿 — the three requirements

Context first: the full 65万円 青色申告 deduction requires the 55万円
conditions plus *either* e-Tax electronic filing *or* keeping 優良電子帳簿
under 電子帳簿保存法 — 優良 status is one of two routes, not a requirement.
Its own distinct benefit is a 5% reduction of 過少申告加算税, and it must be
declared to the tax office in advance (届出). Qualifying as 優良電子帳簿
takes three capabilities:

| Requirement | Meaning | In IrisBooks | Plan |
| --- | --- | --- | --- |
| 訂正・削除の履歴の確保 | Record of every correction and deletion | Durable server history: `iris api history`, web app **Activity** + per-journal **History** | Paid |
| 帳簿間の相互関連性の確保 | Books cross-reference their sources | `iris show`, web app **Cited by** panel | Free, offline |
| 検索機能の確保 | Search by date, amount, counterparty (combinable) | `iris search`, web app **Journals** filters | Free, offline |

The history must be trustworthy to an auditor, which only the server-side
record provides — hence paid, and hence git doesn't count.

Scope of the 優良 claim: all three capabilities must hold together, so it
applies only to books on a paid plan with cloud sync — a free, local-only
book is NOT covered (no auditor-trustable correction/deletion history). It
also holds only while the book stays on the service: deleting a book
(permanent purge of all server data, including history and sealed archives,
after a 30-day window) or ending the subscription removes the durable
history and the book stops qualifying. The statutory retention duty
(7 years, up to 10 in some corporate cases) stays with the user — advise
running `iris api export audit` before any deletion or cancellation.

### Consumption tax (消費税)

The book's status is declared once in `config/book.yaml`:

```yaml
consumption_tax:
  status: taxable          # taxable (課税事業者) | exempt (免税事業者)
  accounting: tax_included # tax_included (税込) | tax_excluded (税抜)
  method: general          # general (本則) | simplified (簡易課税)
  business_class: 5        # 1..6, only for simplified
```

- **免税事業者** (no `consumption_tax` block, or `status: exempt`): record
  tax-inclusive amounts as ordinary 売上 / 経費 with **no** `tax:` blocks; no
  consumption-tax return.
- **課税事業者**: classify each relevant journal **line** with a `tax` block,
  all year. Year-end totals by category and rate drive the 消費税申告書 —
  which *you* fill against the figures the engine sums:

  ```bash
  iris report sum --by tax.category,tax.rate --from 2026-01-01 --to 2026-12-31
  iris report sum --by tax.category,tax.rate,tax.invoice ...   # 本則: split by invoice flag
  iris report sum --by tax.category,tax.rate,tax.business_class ...  # 簡易: by 事業区分
  ```

  Never sum line amounts yourself — take the engine's buckets, then apply the
  per-bucket form math (課税標準 = tax-inclusive total × 100/110 under 税込経理,
  みなし仕入率, 経過措置 percentages) and show your work. The 課税期間 is the
  **calendar year** for individuals (`--from/--to`), the fiscal year for 法人
  (`--year`). The empty-keys bucket holds every line without a `tax` block —
  mostly legitimate counter-lines (bank, receivables), but also any
  classification you missed; scan it for revenue/expense lines before filing.

```yaml
lines:
  - account: 収益:売上
    credit: 100000
    tax:
      category: taxable_sale   # 課税売上
      rate: "10"
  - account: 費用:消耗品費
    debit: 5000
    tax:
      category: taxable_purchase
      rate: "10"
      invoice: true            # holds a qualifying invoice (適格請求書)
```

| `category` token | 税区分 | Carries a rate? |
| --- | --- | --- |
| `taxable_sale` | 課税売上 | yes (positive) |
| `taxable_purchase` | 課税仕入 | yes (positive) |
| `exempt_sale` | 非課税売上 | no |
| `exempt_purchase` | 非課税仕入 | no |
| `export_sale` | 免税売上(輸出) | `0` (or omit) |
| `out_of_scope` | 不課税 / 対象外 | no |
| `securities_sale` | 有価証券譲渡 | no |

**Rate tokens:** `"10"` (standard), `"8r"` (軽減税率 8%), `"8o"` (旧/経過措置
8%, distinct from `8r`), `"5"`, `"3"` (legacy), `"0"` (export).

**`invoice`** (purchase side): whether a qualifying invoice is held under the
適格請求書等保存方式 (Oct 2023 onward). **`business_class`** (simplified
method): each 課税売上 line needs a 事業区分 (第1〜6種); defaults to the
book-level value, overridable per line.

`iris validate` checks coherence (known category; rate matches category —
`taxable_sale` needs a positive rate, `export_sale` is 0%; simplified sales
have a valid business class). Classification itself is tax law *you* apply —
verify against the NTA's current pages, not from memory:

- **Category before rate.** Decide 課税/非課税/免税/不課税 first via the four
  taxability requirements (NTA No.6105 / No.6209: ①domestic ②by a business
  ③for consideration ④a transfer of assets or services — miss one →
  `out_of_scope`), then pick the rate token.
- **Entity status** (課税事業者 vs 免税事業者 — NTA No.6501 / No.6531):
  基準期間 (two years prior) taxable sales ≤ ¥10M → exempt in principle;
  registering as an invoice issuer (適格請求書発行事業者) makes the business
  taxable regardless of sales. Never flip `consumption_tax.status` on your
  own judgment — flag it in `notes/open-questions.md` for the human.
- **Volatile lookups** — みなし仕入率 by 事業区分 (simplified method) and the
  invoice 経過措置 percentages with their sunset dates change; fetch current
  values from the NTA when you need them.

### Depreciation, JP specifics

- **`useful_life_months`** comes from the 耐用年数省令 tables — *you* look up
  the right life on the NTA's current pages and record the resolved number on
  the asset file, so the book carries its own justification. Sources: 耐用年数
  省令 別表第一 (general) / 別表第二 (machinery) at
  `https://www.nta.go.jp/law/joho-zeikaishaku/hojin/sintaiyo/menu.htm`; for
  定率法, the 償却率/改定償却率/保証率 table (別表第十). If `yotaikai_class`
  is missing, ask the user what the asset is, classify, and write both fields.
- **`declining_rate` conversion:** the NTA table gives an *annual* rate; the
  field is *basis points per month* — `bp = annual_rate × 10000 / 12`, rounded
  to an integer (annual 0.500 → `declining_rate: 417`). Assets acquired
  2012-04-01 or later use the 200% 定率法 table; 2007-04〜2012-03 the 250%
  table — an asset keeps its original table for life.
- **Methods:** `straight_line` (定額法), `declining_balance` (定率法, with
  `declining_rate`), `expensed` (immediate write-off).
- **Known limitation:** `declining_balance` does not yet implement the JP
  two-phase switch to 改定償却率 when book value falls below the 保証額. For
  assets that reach that point, *you* compute the switch and record a
  correcting entry.
- **Filings** (固定資産台帳, 償却資産税 申告書, 別表16): *you* produce them
  from the asset files plus the engine's FY figures (`iris export assets
  --year` / `iris asset schedule --year`) and the current-year official form
  spec — fetch this year's layout from the NTA or the municipality; layouts
  change yearly. Write outputs under `compiled/jp/<form>/<year>/`. Take
  `opening_nbv` / `period_dep` / `closing_nbv` from the CSV — never recompute
  engine math — and self-check that your totals match the CSV before
  finishing.
- **償却資産税 traps:** the 評価額 (assessed value) is computed from
  acquisition cost with the 減価残存率 table — it is **not** the CSV's
  `closing_nbv` (that's the income-tax book value). Items with `toku_rei:
  shoutoku_300k` are still declarable; `toku_rei: ikkatsu_3yr` items are
  exempt (地方税法施行令49条) — mark them `shoukyaku_shisanzei.exempt: true`.
  The return is calendar-year (assessment date Jan 1, due Jan 31) even for
  non-January fiscal years.

### Compliance checklist (what "am I compliant?" means)

- `config/book.yaml` has the right `region: JP`, `entity_kind`,
  `fiscal_start_month`.
- If 課税事業者: `consumption_tax` set, lines classified, `iris validate`
  clean.
- Fixed assets described in `assets/` with correct `useful_life_months`.
- (Optional) If 優良電子帳簿 treatment is wanted: paid plan (for the durable
  correction/deletion history) and the advance notification (届出) filed with
  the tax office. The book must stay on the service for the retention
  period — deleting the book or unsubscribing ends 優良 eligibility (advise
  `iris api export audit` first).
- At year-end: seal, download the archive, and (for handoff)
  `iris api export audit`.

## The web app (paid) — what it does, so you can direct users

Works against the cloud copy; needs sign-in and network. Accounts are
email + password (sign-up confirms via emailed code; "Forgot password" resets
via code). An invited user must sign up / log in with the **exact invited
email** — the book is then already there. The **CLI authorization** page is
where `iris api login` sends the browser; the user confirms email + tool and
approves.

Sidebar: **Across all books** (Dashboard, My Books when 2+, Net Worth) and
**Current book** (book switcher — each book gets its own accent color — then
Journals, Activity, Reports, and Manage: Accounts, Raw documents, Notes,
Settings).

| Page | What's there |
| --- | --- |
| **Dashboard** | Headline numbers, P&L flow chart, balance-sheet treemap, incomplete-entries banner; with 2+ books adds net-worth tile, cross-book action queue, consolidated P&L, top movers. |
| **Journals** | Filter/search by date range, payee, free text, status (incl. the derived `closed`), amount (=/>/<); CSV export; open/create/edit/delete entries (delete is soft — the entry moves to the Deleted view); entries in a sealed FY display as `closed` and refuse edit/delete/post until the year is reopened; one-click **Post** on draft entries (detail page) and checkbox **Post selected** for batches (list) — the review path for connector/email drafts when the user isn't at the CLI; **Deleted** view lists soft-deleted entries with who/when and a per-row **Restore** action. |
| Journal detail → **History** | Full per-file audit trail (put/delete/move, who, when, source, reason); **"after seal"** badge on post-seal changes. |
| **Reports** | General Ledger (per account, optional opening balance), Trial Balance (warns if D≠C), P&L, Balance Sheet. Date/as-of filters, hide-zero-rows toggle, CSV export. Posted only; "freshness" note + "incompletes" banner. |
| **Accounts** | Chart grouped by type; click through to an account's ledger. |
| **Raw documents** | Two-pane browser of `raw/`; inline rendering (images, PDFs, parsed CSV tables, text); **Cited by** panel → the journals that reference the document. |
| **Notes** | Read-only Markdown viewer of `notes/` (incl. parse caches, which link back to their source). |
| **Activity** | Book-wide audit log of every file operation; filter by actor/path/operation; expandable content **diff**; **Recover** button when a prior version exists; post-seal changes badged. |
| **Settings** | Interface language (EN/日本語), book ID + fiscal year, Posting approval (owners only — makes posting + posted-entry changes web-only; cannot be changed from CLI/tokens), Inbound email (address, allowlist, quarantine), Grants (owners only), Danger zone (owners only — delete the book; see below), Personal Access Tokens, Connect your AI (connector URL), Connected apps (list + disconnect connector consents). |
| **Net Worth** | Cross-book holdings valuation (cash + non-currency units); total, month-over-month change, trend, movers, composition; per-book include/exclude in its Settings tab. Best-effort, not audited; units without a recorded price are listed as missing. |

### Roles and collaboration

| Role | Can do |
| --- | --- |
| **Owner** | Everything, including managing members and roles. |
| **Bookkeeper** | Create and edit entries. |
| **Reviewer** | Read-only review. |

**Book deletion** is a web-only Owner ceremony (Settings → Danger zone,
typed-name confirm): the book vanishes immediately for every member and is
hard-purged — including its correction/deletion history — after a 30-day
retention window. No CLI command, PAT, or connector token can delete a book;
an agent asked to delete one should direct the user to the web page. Local
clones are never touched: `iris sync` against a deleted book exits 3 with
`disconnectReason: "deleted"` (and `iris status` shows `remoteDeleted`), the
files stay, and the guidance is to either set `book_id` in `config/book.yaml`
back to the local id or create + link a new cloud book.

Owners invite by email from Settings → Grants (or `iris api grants …`); roles
can be changed or revoked anytime. This is how an owner and an accountant
share a book — owner typically via CLI + AI, accountant via the web app, both
meeting at the same server book.

### Personal Access Tokens (PATs)

Long-lived credentials for scripts and the CLI, scoped by role
(**viewer / bookkeeper / full**). Created in Settings, shown **once**, used as
`IRIS_API_TOKEN`. A token expires after 90 days unused (each use renews it,
up to one year from creation). Tokens show last-used time and expiry; revocable
immediately — in Settings, or via `iris api token list|revoke` (a
Full-access PAT can revoke tokens too, including itself, so a headless
run can clean up after itself; minting stays web-only). Accountants use
PATs to script `iris api …` across many client books.

### Accountant daily shape

**My Books** is the client directory — per book: draft count, fiscal-year
status, last activity. Switch into a client book to review/approve entries,
check Activity, run reports. Year-end: seal each client's FY, produce the
audit bundle. Client books stay fully separate — no cross-client aggregation.

## The remote connector (paid) — the user's books away from their computer

`https://irisbooks.jp/mcp` is a remote MCP server over the **cloud copy** of
the user's synced books — how an AI app with no access to the book folder
(phone, claude.ai on the web, a sandboxed client) still answers questions and
captures expenses. The user adds it as a custom connector; sign-in is OAuth
with a scope choice at consent: **Bookkeeper** (reads + draft-only writes,
the default) or **Viewer** (read-only). Effective access is the AND of that
scope and the user's per-book role — a Bookkeeper connection still can't
draft into a book where the user is only a Reviewer.

If you are running on the user's computer and the local `irisbooks` MCP
server is available, **prefer it** — it sees unsynced local edits and is the
only server that runs commands. The remote server's figures are as of the
last `iris sync` from a machine; reports carry a `figures_as_of` timestamp —
mention it when presenting numbers.

Tools: `list_books`; `get_report` (trial-balance | profit-and-loss |
balance-sheet | cashflow; posted entries only); `list_accounts` (call before
drafting — account paths, not guesses); `search_journals`; `get_journal`;
`draft_journal` / `update_draft` (full-replace) / `delete_draft` — all three
draft-only, status pinned `draft`, entries identified by `journal_path`;
`get_inbox_address`; `create_upload_link`.

The write surface **drafts, never posts**: a remote draft appears in the
local book at the next `iris sync` and is posted there. Posting, sealing,
touching `posted`/`closed` entries, and any write into a sealed fiscal year
(`draft_journal` / `update_draft` / `delete_draft`) are refused by
construction. `search_journals` shows sealed-FY entries as
`closed` (and accepts `closed` in its status filter); `get_journal` returns
`closed: true` for them. File bytes can't travel through tool calls: a document in the
user's hand → `create_upload_link` (single-use, 15-minute expiry, image/PDF
≤ 10 MB; scanned, lands in `raw/uploads/`, auto-attaches to a draft);
a document already in their email → `get_inbox_address` (lands in
`raw/email/`). The upload page confirms **delivery**, not just the upload:
tell the user the receipt is in the book only when the page says so (usually
under a minute); reopening the same link later shows the delivery status,
and a scan/ingest rejection is reported on the page instead of a silent
success. Remote-originated changes are labeled (`source=mcp-remote`)
in the audit history.

Disconnecting: removing the connector in the AI app revokes its access, and
the web app's Settings → Connected apps lists every connected AI app with a
server-side **Disconnect** — point users there when they've lost the device
or app. Revocation propagates within a few minutes.

## CLI reference (condensed)

Two surfaces:

- **File-mode** commands operate on a local book folder. With no path argument
  they walk up from the current directory to find the book — run them from
  anywhere inside the book tree.
- **Cloud** commands (`iris api …`) operate on a **book ID**, and need
  `iris api login` or `IRIS_API_TOKEN`.

`iris <command> -h` is authoritative for flags; `iris -h` and `iris api -h`
list everything.

| Command | Purpose |
| --- | --- |
| `iris init [flags] [path]` | Create a book. `--name --region --language --entity-kind --chart(general/it/food) --currency --fiscal-start-month --sample --book-id` |
| `iris onboard [--book PATH] [--claude-desktop] [--codex] [--cursor] [--gemini] [--vscode] [--install-path] [--no-skill] [--dry-run]` | Wire the AI: register MCP (Claude Code always; other clients when detected/forced), write the Claude Code skill |
| `iris onboard --status [--json]` | Read-only report: what is registered where, and whether each registered binary still exists |
| `iris offboard [--book PATH] [--keep-skill] [--remove-path] [--dry-run]` | Inverse of onboard: remove MCP registrations + skill (book data and sign-in untouched) |
| `iris uninstall [--yes] [--dry-run]` | Remove iris itself from the machine: binaries, `~/.config/irisbooks` (CLI session revoked server-side first), skill, machine-level MCP registrations, PATH entry. Prints the exact deletion list and asks first; books and per-book `.mcp.json` are never touched (run `iris offboard` per book beforehand if wanted) |
| `iris clone <book-id> [dest] [--force]` | Fetch a server book to disk (needs sign-in); works immediately on a brand-new server-created book |
| `iris status [--json] [path]` | Book identity, FY start, archive flags, draft count (`draftCount` in JSON — drafts are not in reports) |
| `iris validate [--v] [--json] [path]` | Full validation; `--json` emits issues + counts, exits 1 on errors |
| `iris hash [--raw] <file>` | Canonical content hash of one file |
| `iris organize [--apply] [--fix …] [--json] [path]` | Canonicalize layout (dry-run by default; fixes: fy-folders, extensions, empty-raw, config-typos) |
| `iris balance [--as-of D] [path]` | Trial balance (posted only). JSON output |
| `iris report tb\|pl\|bs\|ledger\|sum …` | Statements; `pl` takes `--from/--to`, `tb`/`bs` take `--as-of`, `ledger` takes `--account`. `sum --by KEY[,KEY...] [--from D] [--to D] [--year FY]` is the generic group-by over posted lines — keys are `account`, `unit`, `payee`, `month`, or dotted concern fields like `tax.category`; lines missing a key surface as an explicit empty group. Output is always JSON (minor units); `--json` is accepted as a no-op |
| `iris search [--from D] [--to D] [--min N] [--max N] [--payee S] [--status draft,posted,closed] [--account S] [--tag S] [--json] [path]` | Find journals; filters AND-combined; deterministic, offline. Status column shows the effective status (sealed-FY journals show as `closed`; `--status closed` filters them) |
| `iris show [--json] <path> [path]` | Cross-references both directions |
| `iris export [--out DIR] [--year YYYY] [--as-of D] [path]` / `iris export assets` | CSVs (UTF-8 + BOM) |
| `iris asset schedule\|depreciate --month YYYY-MM\|--year YYYY [path]` | Depreciation plan / month's entries / FY-total annual entries (one cadence per FY — mixing refused) |
| `iris post [--dry-run] <file>...` / `iris post --all` | Promote to `posted` (validates non-empty + balanced), then sync if linked. `--all` sweeps every draft — incl. phone/connector + email drafts (the auto-post ritual). Refused entirely when the owner turned on posting approval (post from the web app instead). Refuses journals dated in a sealed FY ("FY \<n\> is sealed (closed period) — run `iris reopen <n>` to amend it, then re-seal") |
| `iris diff [<relpath>] [--paths]` | What would be pushed vs the last-synced snapshot |
| `iris sync [--quiet] [--json] [--allow-bulk-delete] [path]` | One explicit push+pull pass; per-file accept/reject. The server refuses a pass that would delete most of the book's cloud files (`BULK_DELETE_REFUSED`); re-run with `--allow-bulk-delete` only when the mass deletion is intentional |
| `iris conflicts list` / `resolve <path> --keep mine\|cloud` | Conflict sidecar management |
| `iris attention list` / `retry [--path <relpath>]` | Server-rejection queue |
| `iris yearend <fiscal-year> [path]` | Write FY+1's opening-balances journal (期首残高, tagged `opening-balance`) from the year's closing balances. Re-run while FY+1 is open to pick up late corrections; frozen once FY+1 is sealed. Offline, free tier |
| `iris reopen <fiscal-year> [path]` | Unlock a sealed FY (writes accepted again, flagged as post-seal edits). The year's files never left the working tree — edit directly, then `iris sync`, `iris yearend` to refresh the carry-forward, and re-seal with `iris api seal` |
| `iris price add\|list\|sync` | Unit prices, user-scoped (not stored in the book), offline + sync |
| `iris mcp serve [--book PATH] [--http 127.0.0.1:PORT]` | MCP server pinned to one book. Local tools: validate, diff, balance, report, status; cloud (when authed): sync, seal, export_from_cloud |
| `iris version` | Version |

Cloud (`iris api …`, book-ID–scoped unless noted):

| Command | Purpose |
| --- | --- |
| `iris api login` / `whoami` / `logout` | Browser sign-in (device-specific CLI session: web logout doesn't affect it, expires after 90 days unused, revocable in web Settings → API tokens) / validate / revoke+remove |
| `iris api token list\|revoke <token-id>` | List / revoke PATs (mint is web-only). Needs a signed-in session or a Full-access PAT — a headless run can revoke the PAT it used when it finishes |
| `iris api books list\|new\|link <book-id> [path]` | List/create cloud books, link a local folder |
| `iris api config [set --base-currency … --set-unit BTC:8,XAU:4 --remove-unit …]` | Per-user preferences, merged into new books at init |
| `iris api grants list\|invite --email E\|role --user U --to OWNER\|BOOKKEEPER\|REVIEWER\|revoke --user U <book-id>` | Book access (owner-only) |
| `iris api inbox show\|allow <pat>\|disallow <pat>\|quarantine <book-id>` | Inbound email |
| `iris api seal --period YYYY [--type yearly] [--preview] <book-id>` | Period seal: closes AND locks the FY (all writes refused until `iris reopen`) + builds the archive snapshot (working tree untouched); re-sealing supersedes the prior seal |
| `iris api archive download --year YYYY [--out DIR] [--timeout 5m] [--interval 5s] <book-id>` | Sealed-FY archive zip |
| `iris api balance [--as-of D] <book-id>` | Server-side trial balance (JSON output) |
| `iris api holdings [--as-of D] [--json] <book-id>` | Per-unit net positions |
| `iris api history [--path PATH] [--limit N] [--json] <book-id>` | The durable correction/deletion record |
| `iris api export [--out DIR] [--year YYYY] [--as-of D] <book-id>` / `export audit <book-id>` | Server CSVs / auditor bundle. `--year` restricts to journals dated in that FY; sealed years stay in the live tree and export like any other |
| `iris api price add\|list` | Server-side unit prices |
| `iris api networth [--book id] [--as-of D]` / `settings [--include\|--exclude\|--reset id]` / `history [--months N] [--refresh]` / `movers [--as-of D] [--compare D]` | Cross-book Net Worth (paid) |

**Recording prices (Net Worth):** `--price` is the value of **one whole
unit** in the reporting currency (decimals OK); `--unit` is the symbol
exactly as it appears on journal lines; re-recording the same
unit+currency+date overwrites. FX rates auto-fill from the ECB — record only
crypto / metals / stocks / manual valuations. Look prices up as a *personal*
lookup (a public price page, the user's own brokerage statement); **never
scrape a licensed market-data feed** (e.g. JPX/TSE) — when in doubt, take
the figure from the user's own statement. Net Worth is best-effort,
management-only — it never touches the tax path or any filing.

Environment variables:

| Variable | Purpose |
| --- | --- |
| `IRIS_API_TOKEN` | PAT; takes precedence over the cached login token |
| `IRIS_BOOK` | Default book ID for cloud commands (positional arg wins) |
| `IRIS_API_ENDPOINT` | API endpoint override; takes precedence over everything below |
| `IRISBOOKS_APP_BASE` | App base URL (default `https://irisbooks.jp`) |
| `IRISBOOKS_API_BASE` | API base URL (default `<app-base>/api`) |

With no endpoint variables set, commands use the endpoint saved by the
last `iris api login`, so a session stays pointed at the environment it
signed in to.

Exit codes: `0` success · `1` validation errors / rejections / I/O · `2` usage
or setup (not in a book, bad flags) · `3` terminal disconnect (sync commands
only: book deleted, access revoked, session expired).

## Troubleshooting — symptom → cause → fix

| Symptom | Cause | Fix |
| --- | --- | --- |
| Entry missing from reports | Status is `draft` — reports are posted-only | `iris post <file>` or edit `status:` |
| `iris validate` errors | Unbalanced entry; unknown account; `date:` ≠ filename prefix; bad status; YAML parse; incoherent JP `tax` block | Fix the named file; re-run. Add missing accounts to the chart — never invent paths in the journal |
| `iris: command not found` | Binary not installed on this host | Install: `curl -fsSL https://irisbooks.jp/install.sh \| sh` (macOS/Linux) or `irm https://irisbooks.jp/install.ps1 \| iex` (Windows PowerShell), confirm with `iris version`. Sandboxed agents: there is **no** bundled copy in the book — use the host's `iris mcp serve` over MCP |
| Validate footer: "N file(s) blocked in the sync queue" | Server rejected a push (not a file problem) | `iris attention list` → fix cause → re-save the journal (or `iris attention retry`) |
| Sync conflict | Same file changed on both sides; server took the canonical path, yours is a `.conflicted` sidecar | Merge by hand, delete the sidecar, `iris sync`; or `iris conflicts resolve --keep mine\|cloud` |
| `iris sync` exit code 3 | Terminal disconnect — `--json` carries `disconnectReason`: `"deleted"` (owner deleted the cloud book; local files intact), `"forbidden"` (grant revoked), `"auth_expired"` (session gone) | deleted → keep working locally (reset `book_id` to the local id) or `iris api books new` + `link --force`; forbidden → ask the owner to re-invite; auth_expired → `iris api login` |
| Need to change a sealed year | Sealed FY is locked (post/sync/web/connector writes refused; sync rejects PERIOD_SEALED); its files stay in the working tree | `iris reopen <year>` (unlocks; nothing to restore) → edit → `iris sync` (flagged as post-seal edits — by design, auditable not hidden) → re-seal with `iris api seal` |
| Web app numbers ≠ CLI numbers | Unpushed local changes, or drafts, or projection lag | `iris diff` then `iris sync`; remember posted-only; check the report "freshness" note |
| Email to the book quarantined as `auth_fail` despite allowlisting | Automatic forwarding rule broke SPF | Forward manually from the user's own mail client instead |

If confusion persists, it is almost always about `status` (drafts vs posted)
or what sync does. Ambiguous bookkeeping items live in
`notes/open-questions.md`; for JP tax rules, apply the Japan section above
and verify volatile values against the NTA's current pages.

## Conduct rules (product-wide)

The in-book `LLM-GUIDE.md` is the binding contract when working inside a book;
these are the product-level constants:

- Don't mass-edit `posted` entries — propose a correcting/reversing entry.
- Don't hand-edit `compiled/` (regeneratable) or `.iris/` (runtime state).
- Don't invent accounts, account types, or tax jurisdictions.
- Don't generate entries from memory — always read the source document.
- Run `iris validate` after every write to `config/` or `journals/` and report
  the result.
- Uncertain? `status: draft` + a note in `notes/open-questions.md`. Never
  guess silently.
- Sync only when asked — it's explicit by design.
