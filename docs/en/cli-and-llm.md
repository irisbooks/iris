# Bookkeeping with the CLI and your own LLM

This is the file-first way to keep your books: you bring your own
AI assistant (Claude, Cursor, Copilot, or any MCP-capable agent), it reads and
writes the book's files, and the `iris` CLI checks the work and calculates
reports. Accounting records use Markdown with YAML frontmatter; configuration
uses standalone YAML. Local `iris` works offline without an account; your
chosen AI service may need its own internet connection.

## CLI use and support

The `iris` CLI is free and provided **as is**, without warranties. Individual
support, bug fixes and continued updates are not guaranteed. Review its output
and keep independent backups of your books. Questions and bug reports are
welcome in the [Discord community](https://discord.gg/wZDsv9gyb9); replies are
not guaranteed.

## The mental model

Start with what you want to record or understand:

1. Share a document, point your AI to an accessible file, or tell it what
   happened. With the tools and access you grant, it can also retrieve a statement.
2. Your **AI** files available originals under the book's `raw/`, interprets
   the information and proposes **journal entries** and a summary.
3. **`iris`** validates the structure and the math and computes reports.
4. **You** review, approve or ask questions. Review before posting is the
   default; follow the book's chosen policy if you authorize automatic posting.

The AI reasons and explains; `iris` checks and calculates. You do not need to
organize files manually or learn the file formats. Validation checks encoded
rules; it does not prove that a source was interpreted correctly.

## Personal tracking can stay relaxed

For everyday personal spending, keep as much detail as is useful to you.
You do not need every receipt. Report your current cash and let your AI ask
a few broad questions about spending since the last check-in, accounting for
cash added or transferred. Or use a credit-card or bank statement: keep its
amounts and let the AI infer broad categories. Estimates and unexplained
differences should stay visible rather than become invented purchases.

Business books need precise amounts, dates, classifications and supporting
evidence; personal records used for tax or reimbursement need the same care.
Ask your AI to save your preferred detail level in `notes/workflow.md` and
keep assumptions in the entries or notes. These files also preserve decisions
and questions for your next session or a different assistant. Optional sync
adds a cloud mirror and server-side change history.

## Receipt detail, personal summaries and backfill

Agree the detail level in `notes/workflow.md` before recording a period. Use
receipt-level business records when that is the chosen policy; preserve original
item detail even when one journal totals the receipt. For everyday personal
management, a confirmed total with explicitly inferred categories can be useful.
Keep purchases at or above an owner-selected threshold separate and explain
whether the owner tracks them as expense or assets. Business asset/tax handling follows the asset workflow and
actual eligibility, not the personal example's amount or classification.

These are two independent synthetic management Books, not paired halves of the
same spending. The examples assume JPY scale 0, a calendar 2026 FY and no selected
optional packages. Define bank/cash as assets, opening equity as equity and the
shown expense paths in each Book's chart. The examples below show their final
posted form; create/review drafts and post only within that Book's policy and
your authority. Tax and reimbursement evidence requirements still apply where
relevant. [NTA No.2080](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2080.htm)
also describes daily aggregation for white-return bookkeeping; per-receipt detail
here is a working policy, not a universal legal requirement (law as of April 1,
2026; checked October 24, 2026).

### Keep the receipt and bank row attached to one business payment

The business Book opens with bank 100,000, cash 10,000 and opening equity
110,000. The January 5 stationery receipt has two items but one payment:

```csv
date,merchant,item,amount,currency
2026-01-05,Synthetic Stationer,Paper,1000,JPY
2026-01-05,Synthetic Stationer,Pens,320,JPY
```

```yaml
schema_version: 1
date: 2026-01-05
status: posted
lines:
  - {account: Expenses:Supplies, debit: 1320}
  - {account: Assets:Cash, credit: 1320}
attachments:
  - {path: raw/receipts/stationery.csv, type: receipt, locator: L2-L3}
```

A January 12 software receipt and its card row both support the same 3,300
charge: debit `Expenses:Software`, credit `Liabilities:Card` once, and attach both
sources. Reconcile every card charge against existing receipt entries before
adding uncovered charges. For a January 18 rail charge of 2,200, the owner
confirms date, amount, payer and business purpose but has no receipt:

```csv
date,merchant,amount,purpose,receipt_status
2026-01-18,Synthetic Rail,2200,Owner confirms client meeting travel,missing
```

```yaml
schema_version: 1
date: 2026-01-18
status: posted
tags: [no-receipt]
lines:
  - {account: Expenses:Travel, debit: 2200}
  - {account: Liabilities:Card, credit: 2200}
attachments:
  - {path: raw/cards/2026-01.csv, type: bank_statement, locator: L4}
  - {path: raw/statement-review.csv, locator: L2}
```

Keep `no-receipt` and the missing original in `notes/open-questions.md`.
The statement proves the charge; owner review supplies the stated purpose.
This management entry does not establish invoice eligibility or tax deductibility.
If the nature or amount itself is unresolved, defer classification and ask for
the missing fact instead of guessing an expense. The later bank deduction
settles the card liability; it is not another purchase. The January 20 withdrawal debits `Assets:Cash` 5,000 and credits
`Assets:Bank` 5,000. It transfers money without creating expense. A separately
recovered January 28 client-folder receipt records `Expenses:Supplies` 1,100
against cash. Describe its discovery/review in notes while retaining the actual
transaction date. Do not use a monthly personal estimate as business evidence or
infer tax eligibility from a receipt's filename. Mixed-use allocation has its
own dated-basis workflow in the [format reference](book-format-reference.md#businessprivate-expense-allocation).

### Keep personal estimates and large purchases distinguishable

The personal Book opens with bank 200,000, cash 10,000 and opening equity
210,000. A January 10 withdrawal moves 10,000 from bank to cash. The owner
confirms 9,000 total ordinary cash spending for January; the 8,000/1,000 category
split is inferred. Individual merchant/date details are unavailable:

```csv
period_from,period_through,total_cash_paid,groceries_estimate,transport_estimate,currency
2026-01-01,2026-01-31,9000,8000,1000,JPY
```

```yaml
schema_version: 1
date: 2026-01-31
status: posted
lines:
  - {account: Expenses:Groceries, debit: 8000}
  - {account: Expenses:Transport, debit: 1000}
  - {account: Assets:Cash, credit: 9000}
attachments:
  - {path: raw/interview.csv, locator: L2}
```

January 31 is the agreed period-end summary date, not an invented date for
each purchase. Keep the confirmed total, inferred category split, covered period
and exclusions in the body. If precise receipts later replace part of a summary,
review and replace/reclassify that covered portion; adding them on top would
duplicate spending. This relaxed record is personal management, not receipt-level
tax/reimbursement substantiation.

The owner selects an individual-purchase threshold of **JPY 50,000 or more**.
The 60,000 sofa is a separate January 15 card purchase, excluded from both
cash and card summaries. The
owner explicitly chooses expense tracking for it in this personal Book; the
example establishes no business capitalization threshold or tax treatment:

```csv
date,merchant,description,amount,currency
2026-01-15,Synthetic Furniture,Personal sofa,60000,JPY
```

```yaml
schema_version: 1
date: 2026-01-15
status: posted
lines:
  - {account: Expenses:Furniture, debit: 60000}
  - {account: Liabilities:Card, credit: 60000}
attachments:
  - {path: raw/receipts/sofa.csv, type: receipt, locator: L2}
  - {path: raw/cards/2026-01.csv, locator: L4-L5}
```

### Preserve the statement, row state and physical locators

The personal card original is `raw/cards/2026-01.csv`. Its sofa description
contains a quoted line break; do not rewrite the source to flatten it:

```csv
date,description,charge,payment,balance
2026-01-01,Opening,0,0,0
2026-01-07,Synthetic Market,12000,0,12000
2026-01-15,"Sofa delivery
order S-15",60000,0,72000
2026-01-19,Synthetic Rail,8000,0,80000
2026-01-31,Closing balance,0,0,80000
```

The personal card category summary covers only the 12,000 market and 8,000
rail charges. The inferred categories stay explicit; actual amounts come from
the statement. The 60,000 sofa is excluded: **20,000 summary + 60,000 individual
= 80,000 statement charges**. Keep its original January 15 date and source.
Cash spending is the separate 9,000 summary above, not part of this card total.

```yaml
schema_version: 1
date: 2026-01-31
status: posted
lines:
  - {account: Expenses:Groceries, debit: 12000}
  - {account: Expenses:Transport, debit: 8000}
  - {account: Liabilities:Card, credit: 20000}
attachments:
  - {path: raw/cards/2026-01.csv, type: bank_statement, locator: L3}
  - {path: raw/cards/2026-01.csv, locator: L6}
```

Mirror the full raw path beneath `notes/`, preserving the original extension:
`raw/cards/2026-01.csv` → `notes/raw/cards/2026-01.csv.md`.
Bank sources use the same rule, for example `raw/bank/2026-01.csv` →
`notes/raw/bank/2026-01.csv.md`. This parse note is
assistant-maintained coordination data, not an automatic importer or duplicate
guarantee. Its completed targets are stable. Opening/closing balance metadata
have explicit ignore reasons; do not ignore an unknown cash outflow merely to
finish the file. Leave genuinely unresolved transaction rows `deferred` and
explain the missing fact in `notes/open-questions.md`.

```markdown
---
source: raw/cards/2026-01.csv
source_sha: sha256:9bfde1fbdc1a8cffcdf724cb867a3dd1980dabdf03efaa2734682bcbe386991b
parsed_at: 2026-10-24
counts: {total: 5, journaled: 3, ignored: 2, deferred: 0}
---

## Rows

| id | date | description | amount | status | target / reason | locator |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-01-01 | Opening | 0 | ignored | Zero opening liability; no transaction | L2 |
| 2 | 2026-01-07 | Synthetic Market | -12000 | journaled | journals/2026-01/2026-01-31-card-summary.md | L3 |
| 3 | 2026-01-15 | Sofa delivery / order S-15 | -60000 | journaled | journals/2026-01/2026-01-15-sofa.md | L4-L5 |
| 4 | 2026-01-19 | Synthetic Rail | -8000 | journaled | journals/2026-01/2026-01-31-card-summary.md | L6 |
| 5 | 2026-01-31 | Closing balance | 0 | ignored | Balance-only observation; no transaction | L7 |

IDs count data records, excluding the header. Locators count actual physical
lines, including the header and quoted line breaks. Ignored opening/closing
rows are balance metadata, not skipped spending. Negative charge amounts in
this note are statement presentation; liability assertions use credit-positive
account direction. This assistant-maintained note is not a native importer or
automatic duplicate guarantee. Preserve completed targets before backfilling.
```

Data-record ID 3 corresponds to physical lines `L4-L5`; ID 4 starts at `L6`.
IDs exclude the header and quoted line breaks, while `L` locators include both.
Native CSV parsing and the Web preview keep these same physical record spans.
Compare `source_sha` with `iris hash` before reusing the note. If a statement is
reissued, preserve it separately, compare changed rows with existing targets,
and retain completed decisions; updating only the hash does not reconcile it.
The receipt and statement still represent one event, not two expenses.

### Resolve backfill from evidence and reconcile cash separately

The personal cash count is 10,970 on January 31:

```csv
date,owner_reported_cash
2026-01-31,10970
```

Before the recovered receipt is posted, the ledger says 11,000, so
`iris reconcile` reports actual 11,000 / expected 10,970 / difference +30 and
exits 1. The bank still matches 190,000. Keep this unexplained difference visible;
do not invent a 30 purchase or reduce the assertion to make the check pass.
On October 24 the original January 29 copy receipt is genuinely found and
confirmed to be outside the 9,000 summary. Retain it and its actual date:

```csv
date,merchant,description,amount,currency
2026-01-29,Synthetic Library,Personal copies,30,JPY
```

```yaml
schema_version: 1
date: 2026-01-29
status: posted
lines:
  - {account: Expenses:Copies, debit: 30}
  - {account: Assets:Cash, credit: 30}
attachments:
  - {path: raw/receipts/backfill.csv, type: receipt, locator: L2}
```

Explain discovery/review time in `notes/backfill.md`; it does not replace the
transaction date or filename. Check for existing coverage before authoring a
draft. Posting needs the Book's ordinary authority and seal guards. This example
assumes an unsealed 2026 FY. For a closed/prior year, use the authorized
reopen/correction workflow rather than shifting the transaction into today or
changing sealed inputs. Record any still-missing evidence as an open question.

Add [balance assertions](book-format-reference.md#balance-assertions) with
`scope: posted` and `unit: JPY`; a CSV does not automatically create observations.
The business Book observes January cash 13,680 on the 27th, then cash 12,580,
bank 95,000 and credit-positive card liability 5,500 on the 31st. The personal
observations below cover January bank/cash/card and February bank/card settlement:

```yaml
schema_version: 1
assertions:
  - id: cash-close
    date: 2026-01-31
    account: Assets:Cash
    measure: amount
    unit: JPY
    scope: posted
    expected: 10970
    evidence: {path: raw/cash-count.csv, sha: sha256:397b3eadca51ca10e939460e0ee82390a7aec7312db5e633b011e3a6054654e8, locator: L2}
  - id: bank-close
    date: 2026-01-31
    account: Assets:Bank
    measure: amount
    unit: JPY
    scope: posted
    expected: 190000
    evidence: {path: raw/bank/2026-01.csv, sha: sha256:a175549e16e2ccdda81172918c7ec2a89c3731c299d5b127d050ddeda48889c7, locator: L4}
  - id: card-close
    date: 2026-01-31
    account: Liabilities:Card
    measure: amount
    unit: JPY
    scope: posted
    expected: 80000
    evidence: {path: raw/cards/2026-01.csv, sha: sha256:9bfde1fbdc1a8cffcdf724cb867a3dd1980dabdf03efaa2734682bcbe386991b, locator: L7}
  - id: bank-after-card-payment
    date: 2026-02-28
    account: Assets:Bank
    measure: amount
    unit: JPY
    scope: posted
    expected: 110000
    evidence: {path: raw/bank/2026-02.csv, sha: sha256:6ad346750ec1cdbe6ed31cf4cfeaa8f07143cd1614c565ef2ae7168845cd04e2, locator: L3}
  - id: card-after-payment
    date: 2026-02-28
    account: Liabilities:Card
    measure: amount
    unit: JPY
    scope: posted
    expected: 0
    evidence: {path: raw/cards/settlement.csv, sha: sha256:b3b8cf9395f45432e2072b7858cd8d7770c0404c659af4e391416442b2e9674f, locator: L2}
```

After reviewing/posting the real backfill, run these read-only checks:

```bash
iris validate --json /path/to/business
iris reconcile /path/to/business
iris report pl --from 2026-01-01 --to 2026-01-31 /path/to/business
iris report pl --from 2026-02-01 --to 2026-02-28 /path/to/business
iris validate --json /path/to/personal
iris reconcile /path/to/personal
iris report pl --from 2026-01-01 --to 2026-01-31 /path/to/personal
iris report pl --from 2026-02-01 --to 2026-02-28 /path/to/personal
```

| January closing figure | Business | Personal |
| --- | ---: | ---: |
| Bank | 95,000 | 190,000 |
| Cash | 12,580 | 10,970 |
| Card liability | 5,500 | 80,000 |
| Expense | 7,920 | 89,030 |
| Income | 0 | 0 |
| Net assets | 102,080 | 120,970 |

The February 10 deductions debit `Liabilities:Card` and credit `Assets:Bank`:
5,500 business and 80,000 personal. February 28 banks are 89,500/110,000 and
card liabilities zero. Cash and net assets stay unchanged; February income and
expense are zero. Observe those balances from the February bank/card originals
too: six business observations and five personal observations in total.

Each checked Book has seven journals, original bank/card files and exact-hash
parse notes, independent counted-cash evidence, a detail policy and backfill notes.
Business expense is 1,320 + 3,300 + 2,200 + 1,100. Personal expense is
60,000 + 20,000 + 9,000 + 30.
Matching the bank alone would miss the personal cash difference; matching both
cash accounts and total expense still would not prove that the sofa kept its
own classification and source. These checks test detail as well as totals.

## Accountants: use a separate work folder for each client

Accountants should also prepare and validate work in book files with their
own AI. Keep each client's books in a separate persistent folder. Give a
dedicated assistant session or VM, such as a Cowork session for Client A,
access only to Client A's folder. It can contain that client's books for
several fiscal years; do not mount the firm's all-client parent folder.

Clone existing shared books into that folder and sync through an authorized
workflow. Read their guides and notes, prepare corrections, validate and
follow the book's posting policy. Save context in the client's files so the
next session can continue. Keep a persistent copy outside temporary VM storage.

Check connected tools and credentials too. A shared host MCP server can have
broader cloud access than its file root, and PAT roles do not limit a token
to one client. Keep broad firm credentials and batch tools outside the client
session; if needed, clone/sync separately and give the AI only the selected
files and tools that cannot access other clients. Verify the actual boundary.

Use the [web app](web-app.md) for reports, review, permitted approvals and
history. It complements the accountant's file work.

## One-time setup: connect your AI

If your assistant already has CLI execution and file access, it can work without
MCP registration. Use `iris onboard` when you want an MCP integration or need
to add missing local guide files.

```bash
iris onboard
```

`iris onboard` registers `iris mcp serve` (a small server that exposes the
`iris` verbs as tools) with your MCP-capable assistants — Claude Code always,
plus Claude Desktop, Codex, Cursor, Gemini CLI, and VS Code when they're
installed — and writes a Claude Code skill. After that, your assistant can
call `validate`, `diff`, `balance`, `report`, `status`, and — once you're
signed in — `sync` directly, instead of guessing at ledger state.

Check what's wired up at any time with `iris onboard --status` (add `--json`
for your AI). Re-running `iris onboard` is always safe — registrations update
in place. To undo everything, `iris offboard` removes the registrations and
the skill without touching your books or sign-in.

This wiring is for the machine the book folder lives on. With a cloud-linked
book you can also read its synced reports and records away from that machine.
The remote connector is read-only; changes require the local setup. See
[Your AI on the go (remote connector)](remote-connector.md).

Every new book has an English `AGENTS.md` at its root: a concise working
contract with the posting policy, integrity rules, a minimal journal and
reference lookup. Local CLI/MCP creation and web/API creation use the same
template. The file syncs with the book, and cloning preserves its contents.
`README.md` briefly explains the folder; `CLAUDE.md` points agents to `AGENTS.md`.
An Owner can customize the contract; changing it in the cloud requires Owner access.
For an older local book, `iris onboard` adds missing entry files and preserves
an existing `LLM-GUIDE.md` policy in `AGENTS.md`, without overwriting custom guides.

> **Sandboxed assistants** (e.g. agents in a VM without the `iris` binary):
> there is no bundled copy inside the book. If using host MCP, the host runs
> `iris mcp serve` and the assistant calls its tools against the same folder.
> For client work, the host connection must respect the client boundary above.

For Cowork's `.mcpb` extension, choose a **parent folder of books**, such as
`~/IrisBooks`, with each book in its own immediate child folder. Give Cowork
file access to the folder you will work in too. The extension can start with
an empty parent: ask your assistant to create a book with `create_book`.
It finds books with `list_books` and names the target book on every operation.
Adding another child book requires no change to the global MCP settings.
For manual setup, use `iris mcp serve --books-dir ~/IrisBooks`; `--book-path PATH`
continues to serve a single book. See [MCP commands](cli-reference.md#iris-mcp).

For accountant work, the parent must contain only one client's books, such
as `~/IrisBooks/ClientA/2026` and `~/IrisBooks/ClientA/2027`. Configure that
client's assistant connection to `~/IrisBooks/ClientA`, and check its cloud
credentials separately. A separate chat alone does not restrict access.

## Online docs and optional downloads

Your assistant reads the book's `AGENTS.md`, its current workflow summary and
relevant questions/decisions. It can then use installed command help or tool
schemas. `iris docs` lists bundled English topics; `iris docs <topic>` lists
sections and sizes. `--section <id>` reads one; `--full` explicitly reads the
chapter. Local MCP `read_docs` has equivalent `topic`, `section` and `full`
selectors without a book argument. No login, download or network is required.

For requested setup, use the [start guide](/start/); current cloud authorization
is in [cloud setup](/start/cloud/). Older tools without bundled lookup can use
the [docs index](/llms.txt). The [complete AI manual](/llms-full.txt) is optional.
An optional Markdown cache belongs outside bookkeeping records, with source URL
and release tag: `https://raw.githubusercontent.com/irisbooks/iris/<release-tag>/docs/llm.md`.
Match `iris version` where available and search only needed sections. Use the
book's selected overlays for its rules; reference material does not authorize actions.

## Check and update iris

```bash
iris update --check --json     # installed/latest versions and executable path
iris update                   # verify and replace the running executable
```

Checks contact the release server only when requested. They need no sign-in;
bookkeeping commands continue to work offline. A failed check means the
latest version is unknown. Development/prerelease builds are reported as
`development` and are not replaced automatically; newer stable builds are
never downgraded.

After updating, run `iris onboard` in your book to refresh agent guidance,
then restart the IrisBooks MCP server. Ask your AI to call `check_update` to
confirm the server's running version. Its report identifies PATH conflicts
and gives instructions for the executable the agent actually uses.

A `.mcpb` extension contains a separate binary. Its update report links the
matching bundle; reinstall it through your client's extension settings with
the same parent folder and restart. When upgrading an older bundle that asked
for one book, choose that book's parent folder in the new configuration.
Updating the CLI alone does not update the bundled server.
On Windows, stop IrisBooks MCP servers and retry if the executable is locked.

Older binaries without `iris update` can be upgraded by rerunning the
[installer](getting-started.md), then `iris onboard`. Ask before installing
an update unless the user has already authorized it.

## The everyday loop

### 1. Share information with your AI

You can attach a bank CSV, receipt scan or PDF invoice in chat, point to an
accessible folder, or ask the AI to retrieve it with tools and access you
grant. The AI can save the original under the book's `raw/`; you can also put
files there yourself if you prefer. Subfolders by date or vendor are fine.
For personal cash tracking, a reported balance and a short interview can be
enough without a document.

### 2. Ask your AI to process it

Tell your assistant something like *"record this statement"* or
*"help me catch up on my personal cash spending"*.
Following `AGENTS.md`, it will:

- For a document, read it in full and write a **parse cache** to
  `notes/raw/<source>.md` — a durable table marking each row `journaled`,
  `ignored`, or `deferred`. This means re-opening the same statement later
  doesn't redo the work.
- For an interview, save what you reported and any assumptions in the entry's
  body or book notes.
- Propose journals as `journals/YYYY-MM/…-NN.md` with `status: draft` at the
  agreed detail level.
- Record unresolved business questions or material unknowns in
  `notes/open-questions.md`; make personal estimates and inferred categories explicit.

### 3. Validate

```bash
iris validate
```

This checks every file: YAML parses, debits equal credits, accounts exist in
your chart, dates are consistent, statuses are valid, and (for Japanese
taxable businesses) tax classifications are coherent. Fix any errors — usually
a missing account in the chart, or an unbalanced entry — and re-run. Your AI
can do this loop for you.

If `iris validate` ends with a note about files *blocked in the sync queue*,
that's a server-side rejection, not a file problem — see
[Troubleshooting](troubleshooting.md#sync-rejections-needs-attention).

### 4. Review and read the books

```bash
iris balance                         # trial balance today (posted only)
iris report pl --from 2026-04-01 --to 2026-06-30
iris report bs --as-of 2026-06-30
iris search --payee amazon --from 2026-04-01     # find entries
iris references raw/2026-05-invoice.pdf                # what cites this document
```

Use filesystem tools (`rg`/`grep`, `find`, `cat`, `sed`, or a file editor) for
routine file listing, reading, text searches and draft/note edits when the
book folder is accessible. Keep operations within the selected book and run
validation after bookkeeping edits. Local MCP is for accounting calculations,
validation, authentication, sync and guarded workflows
such as posting, seals, depreciation and year-end. Structured search and other
inspection tools are optional helpers, useful for structured filters,
derived closed status or when the client cannot access files directly.

`iris search` and `iris references` remain available for structured offline views.

### 5. Promote to `posted`

A `draft` entry stays out of your reports and balances until posted. When
you're happy with one, promote it:

```bash
iris post journals/2026-05/2026-05-04-example-com-01.md
```

`iris post` validates the file (non-empty, balanced), sets `status: posted`,
and — if the book is linked to the cloud — syncs it. Use `--dry-run` to check
without changing anything. You can also just edit the `status:` field by hand;
`post` is the convenience that also balances-checks and syncs.

## Going online (cloud)

Linking a local book to the cloud unlocks the web app, multi-device access,
collaboration, period seals, and the durable history. The local
file-first workflow above doesn't change — you simply gain `iris sync`.

```bash
iris api login            # browser sign-in; this device gets its own CLI session
iris api whoami           # confirm the effective credential and API endpoint
iris api books new        # create a cloud book…
# …or link this folder to an existing one:
iris api books link <book-id>
iris sync                 # one explicit push + pull pass
```

Browser login needs a reachable callback. For remote/headless execution or
approval in another browser profile, use `iris api login --device`, approve on
your own device, then run `iris api login --device-complete` and `iris api whoami`.
A waiting result is not authorization. See [login modes and account profiles](cli-reference.md#iris-api-login).

During browser approval, select the books this CLI may access. Enable
**Allow creating books** to create your first book or next year's book: books
created by this credential are automatically included with the same permissions.
Other later books are excluded. Callback, downloaded-file and device approval
use the same picker. Year-end continuation still requires Owner on the source
book and Full token scope.

After that:

- `iris sync` pushes your local changes and pulls anything new (e.g. entries
  your accountant prepared and synced from their files). It reports per-file accept/reject.
- `iris diff` shows exactly what *would* be pushed before you sync.
- `iris api history --path journals/2026-05/...md <book-id>` shows the durable
  correction/deletion record for a file.

Sync stays **explicit** — it runs when you ask, never in the background.

## Fixed assets and depreciation

If you own depreciable assets, describe each one in `assets/YYYY/<name>.md`
(acquisition cost, useful life, method). Then:

```bash
iris asset schedule                       # see each asset's depreciation plan
iris asset depreciate --year 2026         # one year-end entry per asset
iris asset depreciate --month 2026-05     # or that month's entries, if you close monthly
```

`iris asset depreciate` writes proposed entries (`status: draft`) you review
and post like any other. Details and the Japan-specific rules are in
[Japan tax & compliance](japan-tax-and-compliance.md#fixed-assets-and-depreciation).

### Depreciation your AI can't get wrong

Straight-line iris computes itself. Methods with a country-specific twist —
Japan's 定率法, US MACRS — work differently: your AI looks up the rates and
decides where the method switches, then hands the arithmetic to iris and records
the finished table on the asset file under `schedule:`.

Over the MCP connection your AI has these asset tools for this:

| Tool | What it does |
| --- | --- |
| `asset_schedule` | the engine's per-asset figures — use these for filings verbatim |
| `declining_table` | a declining-balance table at a rate you supply |
| `flat_table` | a fixed charge per period until the asset is written down |
| `straight_line_table` | a basis split evenly over N periods |
| `list_recipes` / `run_recipe` | the region overlay's ready-made composition — preferred whenever one exists |

Both MCP modes use `list_recipes` to discover canonical recipe IDs and schemas,
then `run_recipe(recipe=..., params={...})` to preview. Add `apply=true` and a
book-relative `out` to record the result; `out` alone still previews. Parent mode
also requires `book`.

The point is that your AI never multiplies a balance forward by hand — that's
where arithmetic slips happen, and a slip that still adds up to the right total
is one iris cannot detect. It composes exact tables instead. Better still, when
the book's region overlay has a **recipe** for the method — Japan's 定率法 is
`jp-declining-balance.teiritsu` — it calls `run_recipe` with that ID: the recipe composes the tables in the prescribed
order and records where the rows came from, so `iris validate` can replay them
and catch a switch that landed a year late. Composing by hand is the fallback
for a method no recipe covers. See
[`schedule:`](book-format-reference.md#schedule-recording-the-table-instead-of-computing-it)
for the file format and what iris checks.

## Exporting

```bash
iris export                 # journals.csv, trial-balance.csv, ledger-*.csv
iris export --year 2026     # restrict to a fiscal year
iris export assets          # per-asset depreciation schedule
```

CSVs are written UTF-8 with a BOM so Excel opens non-ASCII text, such as
Japanese, correctly. A text cell (payee, memo, tags, account or asset name)
that starts with `=`, `+`, `-` or `@` is written with a leading `'`, so a
spreadsheet shows it as text
instead of running it as a formula; amounts are never changed. For a
cloud-linked book, `iris api history --all --json <book-id>` writes the
book's — that year's — correction/deletion record as a file.

## A note on what *not* to do

These rules keep your books trustworthy (your AI follows them too):

- Don't mass-edit `posted` entries — record a correcting entry instead.
- Don't hand-edit `compiled/` — it's regeneratable output.
- Don't invent accounts inside a journal — add them to the chart first.

Next: the graphical side in [Using the web app](web-app.md), or the full
command list in the [CLI command reference](cli-reference.md).
