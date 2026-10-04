# Book file-format reference

A book is a folder of plain Markdown and YAML. This page is the reference for
what's in it. You rarely need to hand-write these files — your AI does, and
`iris validate` checks them — but understanding the shape helps.

## Folder layout

```text
your-book/
├── config/
│   ├── book.yaml                 # identity, region, fiscal year, currency
│   ├── chart-of-accounts.yaml    # your accounts
│   ├── rules.yaml                # optional categorization hints (may be empty)
│   └── overlays/                 # optional: this book's own overlay layer (rules, recipes)
├── raw/                          # source documents; any structure, type inferred from content
├── journals/
│   └── YYYY-MM/
│       └── YYYY-MM-DD-<payee>-NN.md
├── assets/
│   └── YYYY/<asset-name>.md       # fixed assets (by acquisition year)
├── filings/
│   └── <fy>/<recipe>.md           # recorded return figures, written by overlay recipes
├── notes/
│   ├── workflow.md  decisions.md  open-questions.md  todos.md
│   └── raw/<mirror of raw/>.md    # parse caches
├── compiled/                      # AI-generated reports (regeneratable)
├── README.md  LLM-GUIDE.md  CLAUDE.md   # human + AI guides
└── .iris/                         # runtime state — never hand-edit
```

Notes:

- A book covers one fiscal year (`fiscal_year` in `book.yaml`). In
  `journals/YYYY-MM/`, the folder is the year and month of the entry's
  accounting date (`date:`) — its first seven characters: `2026-07-15`
  files under `journals/2026-07/`. That holds for any fiscal start month:
  on an April-start book, `2027-02-15` files under `journals/2027-02/`.
  The folder always reflects the accounting date, not the period the
  entry covers.
- The folder is only a cache of the date **in** the file — the file is
  authoritative. Other layouts won't corrupt anything (reports, seals,
  and exports read dates, not folders), and `iris organize` moves
  misplaced journals back to the canonical layout.
- The filename is the entry's permanent identity. Files you or your AI
  write follow `YYYY-MM-DD-<payee>-NN.md`; entries created in the web app or
  through the remote connector are named by the server
  `YYYY-MM-DD-<payee>-jNNN.md`, keeping the payee's own script. Both are
  valid, and the separate numbering means they never collide.
- `.iris/` holds the local book ID and sync state; it's machine-local and
  never synced.

## `config/book.yaml`

```yaml
schema_version: 1
book_id: lb_...                 # minted at init; immutable
name: "Acme Design"
region: JP                      # ISO 3166-1; selects the tax/locale rules
overlay: jp@2026.09.1           # region rules version, pinned at init (see below)
language: ja                    # ISO 639-1; chart language follows this
currency: JPY                   # ISO 4217
scale: 0                        # minor-unit exponent — IMMUTABLE (JPY 0, USD 2, BHD 3)
entity_kind: individual         # individual | company | partnership | trust
fiscal_start_month: 4           # 1–12
fiscal_year: 2026               # the fiscal year this book covers (2026-04-01..2027-03-31 here)
created_at: "2026-06-20T12:34:56Z"

# Optional:
tax_id: "..."                   # opaque per region
opening_balance_equity_account: "資本:元入金"   # where `iris yearend` folds net income
strict_accounts: false          # false = allow accounts not in the chart (default is strict)

units:                          # non-currency units (forex, crypto, metals, shares)
  - symbol: BTC
    scale: 8
    name: "Bitcoin"

consumption_tax:                # JP only — see Japan tax page
  status: taxable
  accounting: tax_included
  method: general
  business_class: 5
```

`scale` is the number of fractional digits the currency uses, and it is
**immutable** — JPY is `0` (whole yen, no decimals), USD/EUR are `2`, the Gulf
dinars are `3`. Region-specific blocks like `consumption_tax` ride along
opaquely: the universal engine ignores them, and the JP overlay reads them.

`fiscal_year` is the fiscal year the book covers, named by the year it starts
in. `iris init` sets it to the year holding today (`--fiscal-year` picks
another), and [`iris yearend`](cli-reference.md#iris-yearend) sets the next
one in the book it creates. It is required: `iris validate` and the cloud
refuse a `book.yaml` without it, and the cloud refuses a change to it — the
next year is a new book, not an edit to this one.

`overlay` names the **region overlay** — the versioned set of country-specific
checks and computations that `iris validate` and the server apply to this book
(for Japan: `toku_rei` regime constraints, the ¥3M/yr 少額減価償却 cap, 消費税
税区分/税率 rules). Japan is the first region with an overlay. A book in a
region without one has no `overlay:` line and gets the universal checks only;
once an overlay for its region is published, `iris overlay upgrade` pins it.
The pin is written once at `iris init` from the version built into your
`iris`, so the rules a book is checked against never change silently. Your `iris` includes
every version released before it was built, so a book pinned to any of them
works offline. Newer versions are released on their own, without a new
`iris`: `iris overlay upgrade` moves the pin to the newest one after checking
it, and `iris overlay fetch` downloads a version newer than your `iris` that a
book already pins (for example, a book set up on another computer). Both
verify the version's signature first. If your `iris` has neither built in
nor downloaded the pinned version, `iris validate` warns and names the version
it used instead. The cloud always checks the version the book pins, and refuses
a pin to a version that has not been published.

## Journal files — `journals/YYYY-MM/*.md`

YAML frontmatter, then a free-form Markdown body.

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

Why this transaction happened (not a restatement of the lines).
```

| Field | Required | Notes |
| --- | --- | --- |
| `date` | yes | `YYYY-MM-DD`; must match the filename prefix |
| `payee` | yes | Native script OK; the filename slug derives from it |
| `status` | yes | `draft` / `posted` |
| `tags` | no | Lowercase, free-form, for grouping |
| `attachments` | no | `{path, type?, locator?}`; a `type` marks a causal source |
| `lines` | yes | 2–999; each has `account` + exactly one of `debit`/`credit` |
| `lines[].memo` | no | Per-line note |
| `lines[].quantity` + `unit` | no | Physical quantity for a unit from `book.yaml` `units` (always positive; direction comes from debit/credit) |
| `lines[].tax` | no | JP consumption tax — see below |
| body | no | Free Markdown after the closing `---` |

**Line count.** A journal takes at most **999 lines**, and you get a warning
from 200 up. Payroll and depreciation entries legitimately run to the
hundreds; four figures means something generated them by mistake. If you
genuinely need more, split the entry — several journals sharing a date and
a tag report identically to one long one.

**Amounts** are written in the currency's natural notation, up to `scale`
decimals. At `scale: 0` (JPY) write whole yen (`1000` = ¥1000, no decimals);
at `scale: 2` write dollars-and-cents (`12.34` = $12.34, and bare `12` =
$12.00, not $0.12). Internally everything is integer minor units.

**Validation:** debits equal credits; every account exists in the chart (or
matches an alias); the date matches the filename; status is valid; YAML parses.
Reports include **only `posted`** entries.

**Per-line `tax` (JP 課税事業者 only):**

```yaml
tax:
  category: taxable_purchase   # taxable_sale | taxable_purchase | exempt_sale |
                               # exempt_purchase | export_sale | out_of_scope | securities_sale
  rate: "10"                   # 10 | 8r | 8o | 5 | 3 | 0
  invoice: true                # holds a qualifying invoice (purchase side)
  business_class: 5            # 簡易課税 事業区分 1..6 (overrides book default)
```

See [Japan tax & compliance](japan-tax-and-compliance.md#consumption-tax-消費税).

## Chart of accounts — `config/chart-of-accounts.yaml`

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
  - path: 資産:事業主貸
    type: asset
    owner: true               # the owner's own money — left out of Net Worth
```

The account's normal side is derived from its `type`. `aliases` let journals
reference an account by another name or language. Add accounts here before
referencing them in a journal.

`owner: true` marks the owner's personal draw and contribution accounts — for
a Japanese sole proprietor, 事業主貸 and 事業主借. They keep their type (so the
balance sheet lays out the way the 青色申告決算書 expects), but they hold the
owner's own money moving in and out of the business, not something the
business owns or owes, so [Net Worth](web-app.md#net-worth) leaves them out.
The Japanese starter charts set it.

## Asset files — `assets/YYYY/*.md`

```yaml
---
schema_version: 1
name: "MacBook Pro 16"
category: equipment.computer       # free-form
acquisition_date: 2026-04-15
acquisition_cost: 480000
salvage_value: 1
useful_life_months: 48
method: straight_line              # straight_line | declining_balance | expensed
asset_account: "資産:工具器具備品"
depreciation_expense_account: "費用:減価償却費"
accumulated_depreciation_account: "資産:減価償却累計額"
acquisition_journal: "[[2026-04-15-apple-01]]"   # optional wikilink
schedule:                          # optional recorded table — see below
  - period: 2027-03                # YYYY-MM, the month the charge lands
    amount: 250000
  - period: 2028-03
    amount: 187500
schedule_source:                   # present when an overlay recipe wrote the table — see below
  overlay: jp@2026.09.1
  recipe: jp.teiritsu
  bindings: 1
  params: {cost: 480000, life: 4, rate: 0.500, guarantee: 0.12499, revised: 1.000, start: 2027-03}
disposal:                          # optional, until disposed
  date: 2029-05-10
  proceeds: 50000
  journal: "[[2029-05-10-apple-disposal-01]]"
---
```

JP-specific fields (用途区分, 特例, 償却資産税 flags) ride along opaquely and
are read by the JP overlay.

Book the purchase of an asset described here to its `asset_account` — an
`expensed` one included — and let `iris asset depreciate` book the charges.
For an `expensed` asset that is one charge: the whole cost, in the
acquisition month. Booking the purchase straight to an expense account as
well would count it twice.

### `schedule:` — recording the table instead of computing it

For straight-line and expensed assets you can leave `schedule` out: iris
computes the charges from `useful_life_months` (an expensed asset: the whole
cost in its acquisition month). For anything else — Japan's
定率法 with its switch to 改定償却率, US MACRS with its straight-line
crossover — the table is recorded on the file (`method: declining_balance`
requires one), and iris uses it verbatim.

Each row is a `period` (`YYYY-MM`) and an `amount`. Annual books write one row
per fiscal year, dated the fiscal year's last month; month-by-month books write
one row per month. Both work.

Your AI assistant builds the table for you. When the book's region overlay
has a **recipe** for the method — Japan's 定率法 is `jp.teiritsu` — it runs
that with the published rates as inputs and the recipe composes the table and
writes it, with its provenance, onto the file (`iris overlay recipe`, or the
matching MCP tool). For a method no recipe covers it composes the arithmetic
from the calculator tools (see [CLI and your AI](cli-and-llm.md)). Once
written, the table is what the books, the reports and the CSV export all use.

iris checks the table is well-formed — rows in order, no negatives, nothing
before the acquisition month or past the useful life or after disposal, and the
rows add up to `acquisition_cost` − `salvage_value` (on a disposed asset, no
more than that — see [Disposing of an asset](#disposing-of-an-asset)). From the rows alone it
cannot check that a switch landed in the right year — that is what
`schedule_source` is for (next section). On a hand-composed table, keep the
rates you used on the file (any extra keys ride along untouched) so your 税理士
can check them against the published table.

### `schedule_source:` — where the table came from, replayed

When a recipe wrote the table, it also recorded its provenance: the overlay
version (`jp@2026.09.1`, or `book:<hash>` for a recipe from your own
`config/overlays/`), the recipe, the engine versions it ran under, and the
inputs you gave — the rates from the published table, the useful life, the
first row's month. `iris validate` **replays** the recipe with those inputs and
refuses the file if the recorded rows differ, so a switch a year late no
longer passes just because the total is right. The inputs stay on the file for
your 税理士 to check against the published table. A table without
`schedule_source` is checked for shape only. If your `iris` ships a different
overlay version than the one recorded, validate says so as a warning and
checks the shape only.

### Disposing of an asset

Add the `disposal:` block with the date and the proceeds. Depreciation runs up
to and including the disposal month at the same monthly charge as before —
disposal ends the schedule, it does not speed it up. What is left of the cost
at that point is the **book value at disposal**. `iris asset schedule` shows it
as `DISPOSAL_NBV` and `iris export assets` as `disposal_nbv`, next to
`accumulated`, the depreciation actually taken. The disposal journal removes
the asset's cost and that accumulated depreciation, records the proceeds, and
books the difference between the proceeds and the book value at disposal as a
gain or a loss.

A computed straight-line schedule stops at the disposal month by itself. A
recorded table is never rewritten for you: delete the rows after the disposal
month, and set the disposal-period row to the charge for the part of that year
the asset was held (in Japan, 月割). The table may then add up to less than
`acquisition_cost` − `salvage_value`, never more. If a recipe wrote the table,
`iris validate` still replays the rows before the disposal month; the
disposal-period row is yours.

Japan's 一括償却資産 (`toku_rei: ikkatsu_3yr`) is the exception: the
one-third-a-year deduction continues after the item is gone. Leave
`disposal:` off those items and note the disposal in the file body instead —
with `disposal:` set, iris would stop the schedule at the disposal month.

## Filings — `filings/<recipe>.md`

The figures a return is filed from, as a recorded file. A figures recipe of
the region overlay (for Japan, `jp.shouhizei-general` and
`jp.shouhizei-simplified` for the 消費税 return) sums the posted journals and
combines them the way the return needs; `iris overlay recipe … --write
filings/jp.shouhizei-general.md` records the result with the same
provenance as a schedule:

```yaml
---
schema_version: 1
filing: jp.shouhizei-general
period: {from: 2026-01-01, to: 2026-12-31}
source:
  overlay: jp@2026.09.1
  recipe: jp.shouhizei-general
  bindings: 1
  params: {from: 2026-01-01, to: 2026-12-31, non_invoice_pct: 80}
figures:
  sales_10: 11000000
  sales_tax_10: 1000000
  deductible_tax: 620000
  net_tax: 380000
  payable: 380000
  # …
---
(a readable table of the same figures)
```

`iris validate` re-runs the recipe over the journals and refuses a filing whose
figures no longer follow from them — so a correction posted after you filed
shows up as an error until you re-run the recipe (or revert the correction).
Your AI fills the government form from `figures`; it never re-adds lines by
hand. Filings sync and are sealed with the book, unlike `compiled/`.

## Your book's overlay layer — `config/overlays/` (optional)

The region overlay — the rules, recipes and derivations your book's region
comes with — is published with iris and pinned by `overlay:` in `book.yaml`.
A book may add its own layer on top:

```text
config/overlays/
├── overlay.yaml        # id: book / extends: jp@2026.09.1
├── functions.yaml      # optional shared expressions
├── rules/*.yaml        # extra checks (an id matching a published rule overrides it)
├── recipes/*.yaml      # extra computations
├── derive/*.yaml       # extra derived-value proposals
└── tests/*.yaml        # golden cases — `iris overlay test` runs them
```

Rules and recipes are written in [CEL](https://cel.dev) expressions over the
book's records — a language with no file or network access and a bounded cost,
which is what makes it safe for your AI to write them. `iris validate` applies
your layer next to the published one, and the cloud applies it to every
member's writes; only the book's Owner can change these files. The first time
a machine meets a version of this layer it shows the files and asks once
(`iris overlay trust` records the answer); until then only the published
overlay applies. A recipe from your layer records `book:<hash>` as its source,
so a reviewer can see a schedule came from a book-specific recipe. The published
overlays are open source (Apache-2.0) in the public
[`irisbooks/overlays`](https://github.com/irisbooks/overlays) repository. A layer
that proves useful beyond one book can be proposed there as a pull request.

## `config/rules.yaml` (optional)

Human-curated hints your AI may use when categorizing; never enforced.

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

## Parse caches — `notes/raw/<source>.md`

When your AI parses a document under `raw/`, it writes a durable, normalized
view here, mirroring the source path. Each row carries a status
(`journaled` / `ignored` / `deferred`) so re-opening the same statement doesn't
redo the work.

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
| 1  | 2026-04-01 | Amazon JP   |  -5000 | journaled | journals/2026-04/2026-04-01-amazon-01.md |
```

## What syncs and what doesn't

With cloud sync, `iris sync` mirrors the **syncable** files to the cloud:

- **Synced:** `journals/`, `assets/`, `filings/`, `notes/` (including parse
  caches), `raw/` (verbatim bytes), `config/book.yaml`,
  `config/chart-of-accounts.yaml`, `config/rules.yaml`, `config/overlays/`.
- **Not synced:** `.iris/` (runtime state), `README.md` / `LLM-GUIDE.md` /
  `CLAUDE.md` (guides), and `compiled/` (regeneratable).

See also: [Core concepts](concepts.md) ·
[CLI command reference](cli-reference.md).
