# Book file-format reference

A book is a folder of plain Markdown and YAML. This page is the reference for
what's in it. You rarely need to hand-write these files — your AI does, and
`iris validate` checks them — but understanding the shape helps.

> Keeping this page honest: the schema mirrors `iris/book/schema.go`. When
> fields change there, update this page (and its Japanese mirror).

## Folder layout

```text
your-book/
├── config/
│   ├── book.yaml                 # identity, region, fiscal year, currency
│   ├── chart-of-accounts.yaml    # your accounts
│   └── rules.yaml                # optional categorization hints (may be empty)
├── raw/                          # source documents; any structure, type inferred from content
├── journals/
│   └── <fy>/<mm>/
│       └── YYYY-MM-DD-<payee>-NN.md
├── assets/
│   └── YYYY/<asset-name>.md       # fixed assets (by acquisition year)
├── notes/
│   ├── workflow.md  decisions.md  open-questions.md  todos.md
│   └── raw/<mirror of raw/>.md    # parse caches
├── compiled/                      # AI-generated reports (regeneratable)
├── README.md  LLM-GUIDE.md  CLAUDE.md   # human + AI guides
└── .iris/                         # runtime state — never hand-edit
```

Notes:

- In `journals/<fy>/<mm>/`, `<fy>` is the **fiscal year** containing the
  entry's accounting date (`date:`) and `<mm>` is the date's calendar
  month. For a calendar-year book (`fiscal_start_month: 1` — every JP
  sole proprietor) the segments are simply the date's own digits:
  `2026-07-15` files under `journals/2026/07/`. On an April-start book,
  `2027-02-15` belongs to FY2026 and files under `journals/2026/02/`.
  The folder always reflects the accounting date, not the period the
  entry covers. The segments are nested folders — `journals/2026/07/`,
  never a single dashed folder like `journals/2026-07/`.
- The folder is only a cache of the date **in** the file — the file is
  authoritative. Other layouts won't corrupt anything (reports, seals,
  and exports read dates, not folders), and `iris organize` moves
  misplaced journals back to the canonical layout.
- `.iris/` holds the local book ID and sync state; it's machine-local and
  never synced.

## `config/book.yaml`

```yaml
schema_version: 1
book_id: lb_...                 # minted at init; immutable
name: "Acme Design"
region: JP                      # ISO 3166-1; selects the tax/locale rules
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

## Journal files — `journals/<fy>/<mm>/*.md`

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
| `lines` | yes | ≥2; each has `account` + exactly one of `debit`/`credit` |
| `lines[].memo` | no | Per-line note |
| `lines[].quantity` + `unit` | no | Physical quantity for a unit from `book.yaml` `units` (always positive; direction comes from debit/credit) |
| `lines[].tax` | no | JP consumption tax — see below |
| body | no | Free Markdown after the closing `---` |

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
```

The account's normal side is derived from its `type`. `aliases` let journals
reference an account by another name or language. Add accounts here before
referencing them in a journal.

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
| 1  | 2026-04-01 | Amazon JP   |  -5000 | journaled | journals/2026/04/2026-04-01-amazon-01.md |
```

## What syncs and what doesn't

On a paid plan, `iris sync` mirrors the **syncable** files to the cloud:

- **Synced:** `journals/`, `assets/`, `notes/` (including parse caches),
  `raw/` (verbatim bytes), `config/book.yaml`,
  `config/chart-of-accounts.yaml`, `config/rules.yaml`.
- **Not synced:** `.iris/` (runtime state), `README.md` / `LLM-GUIDE.md` /
  `CLAUDE.md` (guides), and `compiled/` (regeneratable).

See also: [Core concepts](concepts.md) ·
[CLI command reference](cli-reference.md).
