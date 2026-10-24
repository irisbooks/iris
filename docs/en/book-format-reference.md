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
│   ├── balance-assertions.yaml   # optional observed account balances and evidence
│   └── overlays/                 # optional: this book's own overlay layer (rules, recipes)
├── raw/                          # source documents; any structure, type inferred from content
├── journals/
│   └── YYYY-MM/
│       └── YYYY-MM-DD-<payee>-NN.md
├── assets/
│   └── YYYY/<asset-name>.md       # fixed assets (by acquisition year)
├── filings/
│   └── <recipe>.md                # recorded return figures, written by overlay recipes
├── notes/
│   ├── workflow.md  decisions.md  open-questions.md  todos.md
│   └── raw/<mirror of raw/>.md    # parse caches
├── compiled/                      # AI-generated reports (regeneratable)
├── README.md  AGENTS.md  CLAUDE.md   # human + AI guides
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
book_id: lb_...                 # local ID at init; replaced by cloud ID when linked
name: "Acme Design"
region: JP                      # ISO 3166-1; locale and region compatibility
overlays:
  - journal-balance@2026.10.1
  - inventory-disposal@2026.10.1
  - jp-tax-classification@2026.10.1
  - jp-tax-amount@2026.10.1
  - jp-tax-filing@2026.10.1
  - jp-small-asset-deduction@2026.10.1
  - jp-declining-balance@2026.10.1
language: ja                    # ISO 639-1; chart language follows this
currency: JPY                   # ISO 4217
scale: 0                        # minor-unit exponent — IMMUTABLE (JPY 0, USD 2, BHD 3)
fiscal_start_month: 4           # 1–12
fiscal_year: 2026               # the fiscal year this book covers (2026-04-01..2027-03-31 here)
created_at: "2026-06-20T12:34:56Z"

# Optional:
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

`units` is optional and starts empty in new books. Known currencies use
built-in quantity precision (JPY: 0, USD/EUR: 2, KWD: 3), without entries
in this list. An explicit `units` entry overrides that currency's quantity
precision; custom units such as BTC or shares require a declaration.
Unknown symbols must include `scale`; even whole-unit custom units must
explicitly specify `scale: 0`. Omitting it (or writing `null`) is rejected
by local parsing, synced book uploads, and account unit-template API writes.
For example, `- {symbol: USD, scale: 4}` permits four fractional digits
in a USD `quantity`. It does not change the precision of journal amounts:
those use the book's top-level `scale`, which defaults from `currency` when
omitted. An explicit top-level `scale: 0` remains zero, even for USD.
Cloud Book amount precision supports 0–6 fractional digits; declared quantity
unit precision supports 0–18.
Signed-in `iris init` copies available account unit templates;
`--no-user-defaults` skips them. Account preferences affect new books only.
The BTC entry above is an example, not a preinstalled default.

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

`overlay` selects one exact function version;
`overlays` selects several exact versions. Local clients execute only definitions
stored in the Book at `config/overlay-packages/`. This store is separate from
`config/overlays/`, the active trusted local layer, and from `.iris/` runtime state.

A package is **available** when its verified copy is in the Book, **enabled**
when selected, and **applicable** only where its conditions match. Stored copies
do not activate themselves. Omitted or empty selections enable no optional
packages. Common completion requires explicit `journal-balance@<version>` and/or
`inventory-disposal@<version>` copies and selections.
Core accounting/structural checks remain active. Region never supplies a hidden
selection. A missing or changed exact copy is diagnosed without substitution;
use `iris overlay install` explicitly to copy selected distribution versions.
Cloud preserves these files/settings but never evaluates Overlay definitions.

Copies installed from a binary verify their complete source files against its
trusted release fingerprints; runtime reads do not need the binary's old package
body. Downloaded copies verify their release signature. The Book's stored bundle
hash still binds its exact bytes. A fingerprint or signature never supplies a
missing definition or enables a package by itself.

Bindings v4 excludes journal workflow status and approval/closure metadata,
including nested record data. Definitions that read `journal.status` or target
lifecycle fields fail with an explicit compatibility error. Domain facts such
as `consumption_tax.status` remain available. The host enforces draft-only
completion, posting permissions, seals and status-aware report inclusion.

Bindings v5 adds explicit concern-field preparation before journal completion.
A package can export `points.yaml` with a qualified point ID, interface version,
`classify` or `calculate` stage, one scalar line field and declared scalar inputs.
Providers use `derive/*.yaml` with `point` and `point_version`; they see only
`inputs` and their typed `params`. Helpers stay private. Points use their owner's
field schemas; a separate provider declares compatible owner package versions.
Each point accepts one provider. Missing required providers, incompatible
interfaces, competing providers, output conflicts and dependency cycles reject
the selection. Optional points require an explicit `fallback: recorded`.
Once a point applies, every declared input marked `required` in its schema
must be present; the point's condition controls preparation applicability.

Preparation only fills missing concern fields in an already balanced draft.
It preserves recorded values and cannot change core postings or lifecycle state.
The fixed stages run once, with declared `after` dependencies from classification
to calculation. Limits include 16 points, 64 lines, scalar strings of 4,096 bytes,
64 KiB of inputs/parameters per call and 256 trace entries totaling 64 KiB.
Expressions and reachable helpers have a 4,096-node limit and cannot contain
comprehensions. Calls have a 100,000 cost limit, and the complete run has a
1,000,000 preparation-expression cost limit, including private helpers and
string allocations. Ordinary validation checks the completed candidate afterward.

Filled fields retain exact owner/provider identities and saved inputs/parameters
under each line's `preparation_source`, mirroring the field path. This host-owned
metadata is excluded from point inputs and outputs. Local apply retains any
referenced `book:<hash>` definition before writing the journal. `iris validate`
replays saved fields from those exact Book copies even after disabling them;
changed source facts/results fail verification, while an unavailable copy gives
an explicit warning. Current book settings do not replace saved inputs.
Validation never runs a preparation chain to repair a candidate.

Local Overlay checks share a budget across the complete validation request,
including field guards, private helper bodies, native ledger operations,
derivation hints and recorded-result replay. The CLI uses one session for the
whole Book; autocomplete and task-context requests also share their own session.
Limits are 50,000,000 aggregate cost units, 1,000,000 expression evaluations,
512 MiB of processed input and 10,000 issues totaling 1 MiB. Ordinary expressions
have a 5,000,000 cost ceiling and 32,768 expanded nodes. Preparation retains its
stricter limits above. Native tables and ledger groups are capped at 4,096 rows;
ledger inputs at 100,000 lines; historical definition lookups at 64 identities.
Native result conversion is limited to 256 KiB, 16 levels and 4,096 values;
rendered messages to 16 KiB. Limits are checked before native table allocation
and unbounded input/result expansion. Exhaustion reports an
`overlay.checks-incomplete` error; `iris validate --apply` writes no proposals
when any Overlay check cannot finish. Ordinary type/evaluation warnings remain
distinct, and native accounting checks continue.

Analytics artifact schema v5 retains config, asset and journal-line extensions in a
fixed `record_fields` relation, with the original book, path and line index.
Values remain passive JSON, including large integers, nulls and arrays. Each
extension object is limited to 256 KiB, 16 nested levels and 4,096 values; the
compiler also saves original JSON text by field pointer, before numeric
extraction can round tiny or wide values. This index is limited to 4 MiB before
escaping per object; total metadata, including the index, is limited to 64 MiB.
Application-owned queries support
bounded field reads, exact-value filters, typed groups and exact integer
`SUM`/`COUNT`. Integer aggregation uses 38-digit decimal values and retains every
digit. Fractional sums use ordered compensated floating-point addition and are
marked approximate (`≈`); a value or sum outside the supported range is
unavailable. Numeric strings are not coerced. Source values remain visible even
when they cannot be summed. Filtering/grouping compares captured JSON text, so
different number spellings can form separate groups. Plain JSON-form numeric
extension scalars beyond YAML's native range retain their numeric text; quoted
numbers remain strings, including after a local rewrite. Typed accounting
amounts retain their existing integer rules. Asset fields use `kind = 'asset'` and `line_index = -1`, one row per
original asset. Cloud capture extracts them from accepted reference bytes
without executing definitions. Arrays and objects remain one record and never
multiply accounting rows.

## Pin several published overlays

`overlays` selects an **unordered set of exact versions**. Use it instead of
`overlay`; the two forms cannot appear together. For example, a published
specialist package could accompany tax classification:

```yaml
# Illustrative: jp-rsu must be published before this configuration can load.
overlays:
  - jp-tax-classification@2026.10.1
  - jp-rsu@2026.10.1
```

Every member must have an exact verified Book copy, installed explicitly with
`iris overlay install`. Cache-only `fetch` does not change Book execution. An
unavailable member stops local validation; neither pin form substitutes a version. Duplicate package IDs, incompatible regions or dependencies,
and conflicting published rule IDs or field definitions are errors. Pin order
does not determine precedence. Each package keeps its own CEL helpers; a recipe
records the exact version of the package that owns it.

A package can declare `region: JP` and exact supported dependency versions in
`overlay.yaml`, for example `requires_overlays: {jp-tax-classification: ['2026.10.1']}`. Packages
using the new selectors or parameter contract declare `requires_bindings: 2`.
`iris overlay upgrade --dry-run` checks the candidate set, golden tests,
book-layer compatibility and settings before showing the proposed pins.
`--to jp-rsu@<version>` changes that member; without `--to`, upgrade checks
the latest release of every pinned member together.

The initial function catalog contains seven independently selectable candidates,
all version `2026.10.1` and requiring bindings 5:

| Catalog category | Individual Overlay IDs |
| --- | --- |
| Common completion | `journal-balance`, `inventory-disposal` |
| Japanese consumption tax | `jp-tax-classification`, `jp-tax-amount`, `jp-tax-filing` |
| Japanese fixed assets | `jp-small-asset-deduction`, `jp-declining-balance` |

Categories organize discovery/distribution; they are not activation switches.
New Japanese business presets copy/select all seven functions. Personal and
non-JP business setup select the two common functions. Existing Books keep their
actual function pins, including off. Retired combined packages are removed
without a production migration. Signed publication remains pending.

`jp-tax-amount` and `jp-tax-filing` each require an explicitly selected
`jp-tax-classification@2026.10.1`; neither requires the other. Classification owns
the tax-setting schemas and task context. Keep classification enabled while
removing amount proposals or filing calculations independently. Balancing and
inventory disposal are independent, as are deduction checks and declining balance.
A missing dependency refuses selection without an implicit fetch or cascade.

Each function carries its necessary checks, fields, task, guide and executable
examples. Native structural/double-entry checks stay active. Recipe invocation
is explicit. Tax status, elections and eligibility remain confirmed facts;
pooled depreciation and partial-year declining balance remain unsupported.
The combined `default`/`jp` and superseded aggregate candidates are retired.

The binary carries a curated offline installation catalog. Other versions use
signed GitHub downloads followed by explicit installation. Runtime and historical
replay read retained exact Book copies; disabling a function preserves its
recorded results and sources. Trusted fingerprints survive when older bodies
are omitted from a later binary.

## Discover field choices and workflow guides

`iris overlay list --json` exposes pins, rules (including `when` and `assert`),
parameter schemas, field definitions, tasks and guide IDs. Start with the
compact `iris context` / local MCP `get_book_context` for a domain task; technical
inspection remains available. Guide `#section` selectors match the bundled
manual's heading conventions. `iris overlay example <task> <file#case>` and MCP
`read_overlay_example` return actual checked fixture cases. Local MCP provides the
same information through `describe_overlay`; a parent-folder server also takes
`book`. These definitions describe the versions this book actually uses.

Published packages may include an optional `fields.yaml`:

```yaml
fields:
  line.sales.channel:               # path: target.concern.field
    type: string
    description: {en: Sales channel, ja: 販売チャネル}
    enum:
      - {value: online, label: {en: Online, ja: オンライン}}
      - {value: store, label: {en: Store, ja: 店舗}}
```

Here `online` and `store` are the stored values; the labels are display text.
Absent fields are optional unless `required: true` is declared. A field may
also have a CEL `when` condition. Present values are checked against their
types and choices. Older packages without field definitions still expose their
rule assertions, including any lists of accepted values; structured metadata
requires a new published version or an additional book-local field definition.

A package's `guides/*.md` describes its workflow. Read a discovered guide with
`iris overlay guide <id> [path]` or local MCP `read_overlay_guide` (`guide`).
The text is reference data from the pinned package; it does not grant authority
to edit or submit anything.

Web and remote MCP read the same stored declarations and reference text without
the local evaluator. A declared `required`/`when` condition is not a cloud verdict.
The response identifies the synced Book revision and excludes unsynced edits.
Book-local Markdown guides under `config/overlays/guides/` sync as bounded inert
files (64 KiB each); their presence does not establish trust or enable a package.

## Configure shared rules and recipes for your book

Rules are validations: they run `when` and then check `assert`. A matching rule
does not create a report. Derivations propose field values; recipes compute
schedules or figures. All three may declare `params` with a name, type,
optional default and optional `enum`. Rule and derivation expressions read
`params.<name>`; recipe expressions retain their named input variables.

For example, a sales rule could declare an account selector and require a memo:

```yaml
rules:
  - id: sales.memo-required
    target: line
    params:
      - {name: accounts, type: account_selector, default: {exact: ['収益:Sales']}}
    when: account_matches(line.account, params.accounts)
    assert: line.memo != ''
    message: {en: A selected sales line needs a memo., ja: 対象の売上明細にはメモが必要です}
```

Book-specific inputs go in `config/book.yaml.overlay_settings`, under the
package ID, then `rules`, `derivations` or `recipes`, then the item ID:

```yaml
# Illustrative settings for a package defining these items.
overlay_settings:
  jp-sales-demo:
    rules:
      sales.memo-required:
        params:
          accounts: {contains: うりあげ}  # literal, case-sensitive substring
    derivations:
      sales.channel:
        params: {channel: store}         # must be in the declared enum
    recipes:
      monthly-sales:
        params:
          accounts: {exact: ['収益:Sales']}
          from: '2026-09-01'
          to: '2026-09-30'
```

An `account_selector` contains exactly one of `exact` (a non-empty list of
account references), `subtree` (a path and its colon-separated descendants),
or `contains` (a literal substring). It never assumes that `うりあげ`, `売上`
and `Sales` are synonyms. CEL `account_matches` tests one reference;
`select_accounts(journals, selector)` supplies selected lines to `sums`.

Quote dates and timestamps in settings, including inside maps and lists:
`cutoff: '2026-09-01'`. Unquoted YAML dates are rejected before sync. Whole
numbers inside map/list parameters use integer arithmetic locally and on the
server; fractional values use doubles. A declared scalar `double` keeps that
type.

Unknown settings, absent required rule inputs, wrong types and invalid choices
are errors. Recipe invocation values override book defaults. Before a recipe
runs, name selectors resolve to sorted exact references found in the journals;
no match is an error. Those resolved inputs are saved in provenance. Replay
uses the saved inputs even if book defaults later change, while changed
journal figures still make a saved filing stale. A monthly-sales computation
is a reusable example; it is not itself a statutory tax return.

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
| `date` | yes | `YYYY-MM-DD`; must match the filename prefix, except generated `0000-opening-balances.md` |
| `payee` | no (recommended) | Native script OK; the filename slug derives from it |
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

## Defaults and inferred values

Keep shared settings in `config/book.yaml`. An ordinary journal records its
date, status and account/amount lines; optional payee, evidence and notes add
context. The following values do not need to be repeated on every line:

| Value | What IrisBooks uses | Where you specify it |
| --- | --- | --- |
| Amount currency | The book's `currency` | Once in `config/book.yaml` |
| Amount precision | The book's `scale`; if omitted, the currency's built-in precision | Set at book creation; it is immutable afterward |
| Quantity precision | An explicit `units` entry, otherwise built-in precision for known currencies | Declare custom units once in `config/book.yaml`; include `scale: 0` for whole units |
| Direction | The `debit` or `credit` key | Use exactly one on each line; `quantity` stays positive |
| Journal identity | The filename | No journal ID field is needed |

For money-only lines, omit both `quantity` and `unit`. For a commodity holding,
add both to the line that moves it. For example, in a JPY book with `FUND`
declared at `scale: 0` and the two accounts in the chart, save this as
`journals/2026-10/2026-10-20-fund-01.md`:

```markdown
---
schema_version: 1
date: 2026-10-20
status: draft
lines:
  - account: Assets:Investments
    debit: 100000
    quantity: 10
    unit: FUND
  - account: Assets:Bank
    credit: 100000
---
```

This records ten units bought for ¥100,000. Currency, quantity direction and
unit precision need no extra journal attributes. The date and status remain
explicit; the draft stays out of ordinary reports until posted.

For [portfolio analytics](cli-reference.md#iris-analytics), acquisition lot
identities can be derived from the purchase lines, so a simple purchase needs
no `lot` label. **FIFO is the default** for disposal cost allocation: the
earliest acquisitions are consumed first, independently per account and
commodity. An explicit matching `inventory.params.method` takes precedence;
otherwise analytics keeps the method in opening inventory, then falls back
to FIFO. Supported methods are `fifo`, `specific` and `moving-average`.
Specific identification requires a lot selection on each disposal. Missing
acquisition history or opening basis leaves acquisition cost unknown.

Local report comparisons calculate disposal cost and adjust gain/loss without
editing or posting journals. If a cost adjustment is needed, specify the gain
account once in `config/book.yaml`:

```yaml
inventory:
  params:
    gain_account: Income:Gain
```

The account must exist in a strict book's chart. The method may be omitted for
FIFO; set `method: moving-average` to change it, including in a selected view.
An omitted `accounts.exact` selector covers commodity asset accounts; add it
to restrict the scope. The optional `commodity` filter restricts the unit.
Use `iris report pl --mode comparison` to inspect the calculated ledger.
Comparison JSON lists `selection.inventoryMethods`; portfolio SQL exposes
`inventory_method`, and Net Worth shows the method beside each commodity
account. Ordinary validation and approved reports use the recorded ledger;
computed comparisons stay unapproved.

To complete a sale draft, record the proceeds and quantity, and mark its cost
as `credit: null`. With the gain account above configured and the purchase
above posted, save this as `journals/2026-10/2026-10-21-sale.md`:

```markdown
---
schema_version: 1
date: 2026-10-21
status: draft
lines:
  - account: Assets:Bank
    debit: 70000
  - account: Assets:Investments
    credit: null
    quantity: 5
    unit: FUND
---
```

Run `iris journal complete journals/2026-10/2026-10-21-sale.md` to preview a ¥50,000
inventory credit and a ¥20,000 gain credit. Apply the preview with `--apply`
and its `--revision`. An explicitly selected Book copy of the `inventory-disposal` Overlay supplies inventory
completion without additional journal attributes. Confirm the selection with
`iris context`; an off/missing package does not acquire completion implicitly. Fees, when present, remain explicit expense postings.
With `journal-balance` selected, an ordinary money-only journal can leave one balancing amount as
`debit: null` or `credit: null`. Completion keeps drafts unposted; validation
checks the resulting recorded amounts. See [iris journal complete](cli-reference.md#iris-journal-complete).

## Fund units, partial sales and dated valuation

This complete synthetic management Book buys 100,000 whole fund units for
JPY 100,000, sells 20,000 for JPY 26,000, and retains 80,000 units with known
cost JPY 80,000. Use a fresh sample folder. All bank, broker and price evidence
below is fictional; the example chooses no tax regime, fund or investment.

Save `config/book.yaml` and `config/chart-of-accounts.yaml` as follows. Quantity
scale is the fractional precision of one whole fund unit; it is independent of
a quotation per 10,000 units. This example explicitly selects the generic
`moving-average` management method. With one acquisition, the supported generic
methods give the same cost; this does not establish a statutory tax method.

```yaml
schema_version: 1
book_id: fund-2026
name: Synthetic fund management example
region: JP
language: en
currency: JPY
fiscal_year: 2026
fiscal_start_month: 1
overlays: []
units:
  - {symbol: SYNTHFUND, name: Synthetic fund (one whole unit), scale: 0}
inventory:
  params: {method: moving-average, gain_account: Income:FundGain}
```

```yaml
schema_version: 1
accounts:
  - {path: Assets:Bank, type: asset}
  - {path: Assets:Fund, type: asset}
  - {path: Equity:Opening, type: equity}
  - {path: Income:FundGain, type: income}
```

Save the opening, purchase and sale frontmatter in the named Markdown files,
inside `---` delimiters. These blocks show the fixture's final posted state.
For real work, author/review drafts and post under the Book's policy. Posting can
normalize YAML quoting; quantities, amounts, evidence, extra fields and body
must survive. A linked Book's posting command can also sync it.

`journals/2026-01/2026-01-01-opening.md`:

```yaml
schema_version: 1
date: 2026-01-01
status: posted
tags: [opening-balance]
lines:
  - {account: Assets:Bank, debit: 1000000}
  - {account: Equity:Opening, credit: 1000000}
attachments:
  - {path: raw/bank.csv, locator: L2}
```

`journals/2026-06/2026-06-01-fund-purchase.md`:

```yaml
schema_version: 1
date: 2026-06-01
status: posted
payee: Synthetic broker
lines:
  - {account: Assets:Fund, debit: 100000, quantity: 100000, unit: SYNTHFUND}
  - {account: Assets:Bank, credit: 100000}
attachments:
  - {path: raw/trades.csv, locator: L2}
  - {path: raw/bank.csv, locator: L3}
```

`journals/2026-08/2026-08-01-fund-sale.md`:

```yaml
schema_version: 1
date: 2026-08-01
status: posted
payee: Synthetic broker
lines:
  - {account: Assets:Bank, debit: 26000}
  - {account: Assets:Fund, credit: 20000, quantity: 20000, unit: SYNTHFUND}
  - {account: Income:FundGain, credit: 6000}
attachments:
  - {path: raw/trades.csv, locator: L3}
  - {path: raw/bank.csv, locator: L5}
```

Retain the independent synthetic evidence. The sale statement supplies the
JPY 20,000 disposed cost and JPY 6,000 gain; the bank receives the full JPY 26,000.
The example has no fees, taxes withheld, FX, distributions or corporate actions.

`raw/trades.csv`:

```csv
id,date,side,units,cash_jpy,disposed_cost_jpy,realized_gain_jpy
BUY-1,2026-06-01,buy,100000,100000,0,0
SELL-1,2026-08-01,sell,20000,26000,20000,6000
```

`raw/bank.csv`:

```csv
date,balance_jpy
2026-01-01,1000000
2026-06-01,900000
2026-06-30,900000
2026-08-01,926000
2026-08-31,926000
```

`raw/holdings.csv`:

```csv
date,unit,units,carrying_cost_jpy
2026-06-30,SYNTHFUND,100000,100000
2026-08-31,SYNTHFUND,80000,80000
```

`raw/nav.csv`:

```csv
date,unit,quoted_nav_jpy,quoted_units
2026-06-30,SYNTHFUND,12345,10000
2026-08-31,SYNTHFUND,15000,10000
```

The quote is per 10,000 units. JPY 12,345 / 10,000 is **JPY 1.2345 per whole
unit**, and JPY 15,000 / 10,000 is JPY 1.5. Price capture accepts up to six
fractional digits; `valueMicro` is the per-unit price multiplied by 1,000,000,
so these observations are 1,234,500 and 1,500,000. Preserve the actual 100,000 /
80,000 holdings quantities. The quotation denominator is not a quantity scale
or a reason to shrink the units recorded in a journal.

For this synthetic exercise, select a token-file path in a new empty temporary
directory before capturing prices. Keep that selection for every command so
the sample uses an isolated user price log. Within the sample Book:

```bash
export IRISBOOKS_TOKEN_FILE="$(mktemp -d)/token.json"
iris price add --unit SYNTHFUND --currency JPY --date 2026-06-30 --price 1.2345 --source "Synthetic raw/nav.csv L2"
iris price add --unit SYNTHFUND --currency JPY --date 2026-08-31 --price 1.5 --source "Synthetic raw/nav.csv L3"
iris price list --unit SYNTHFUND --currency JPY --year 2026 --json
iris networth --as-of 2026-07-31 .
iris networth --as-of 2026-08-31 .
```

A price is user-scoped, outside the Book. Recording it neither registers the
unit nor creates a holding, posts a journal or changes its cost. Local CLI and
local MCP `get_networth` use pending local prices immediately. Single-book MCP
uses `books: ["."]`; parent mode uses the selected child folder. Both require
explicit local folders and read posted entries.

Check independent quantities and cash before relying on valuation. Save the
following as `config/balance-assertions.yaml`; its hashes bind the exact CSV
bytes above and its `L` locators identify physical lines including the header.

```yaml
schema_version: 1
assertions:
  - id: bank-june
    date: 2026-06-30
    account: Assets:Bank
    measure: amount
    unit: JPY
    scope: posted
    expected: 900000
    evidence: {path: raw/bank.csv, sha: sha256:5668d77fe567be6f02992a4f7a6074acc1f51826e93ecbc2e634b3b9fba6aad9, locator: L4}
  - id: units-june
    date: 2026-06-30
    account: Assets:Fund
    measure: quantity
    unit: SYNTHFUND
    scope: posted
    expected: 100000
    evidence: {path: raw/holdings.csv, sha: sha256:c46a0507db7a04982d2724d1aacb0127b28df3c66a79f36ac24ca98c5a0d37c7, locator: L2}
  - id: cost-june
    date: 2026-06-30
    account: Assets:Fund
    measure: amount
    unit: JPY
    scope: posted
    expected: 100000
    evidence: {path: raw/holdings.csv, sha: sha256:c46a0507db7a04982d2724d1aacb0127b28df3c66a79f36ac24ca98c5a0d37c7, locator: L2}
  - id: bank-august
    date: 2026-08-31
    account: Assets:Bank
    measure: amount
    unit: JPY
    scope: posted
    expected: 926000
    evidence: {path: raw/bank.csv, sha: sha256:5668d77fe567be6f02992a4f7a6074acc1f51826e93ecbc2e634b3b9fba6aad9, locator: L6}
  - id: units-august
    date: 2026-08-31
    account: Assets:Fund
    measure: quantity
    unit: SYNTHFUND
    scope: posted
    expected: 80000
    evidence: {path: raw/holdings.csv, sha: sha256:c46a0507db7a04982d2724d1aacb0127b28df3c66a79f36ac24ca98c5a0d37c7, locator: L3}
  - id: cost-august
    date: 2026-08-31
    account: Assets:Fund
    measure: amount
    unit: JPY
    scope: posted
    expected: 80000
    evidence: {path: raw/holdings.csv, sha: sha256:c46a0507db7a04982d2724d1aacb0127b28df3c66a79f36ac24ca98c5a0d37c7, locator: L3}
```

```bash
iris validate
iris reconcile
iris report pl --mode comparison --from 2026-01-01 --to 2026-08-31
```

Expected results:

| As of | Cash | Whole units | Remaining acquisition/carrying cost | Selected price date | Fund market value | Total worth |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| 2026-07-31 | 900,000 | 100,000 | 100,000 | 2026-06-30 | 123,450 | 1,023,450 |
| 2026-08-31 | 926,000 | 80,000 | 80,000 | 2026-08-31 | 120,000 | 1,046,000 |

This Book selects inventory calculation, so local P&L uses `--mode comparison`
and is explicitly unapproved. Retained financial acceptance is not implemented;
the default approved local report refuses this calculated inventory selection.

The posted P&L contains income/net JPY 6,000 and no expense. Book net assets
are JPY 1,006,000. The remaining JPY 40,000 market uplift is management valuation,
not another posted income. July uses June's price and excludes the future August
observation. `asOf` is the valuation date; `priceDate` identifies the observation
actually used, which may be old.

These three omissions have different results:

| Missing fact | Result and remedy |
| --- | --- |
| Market price | Known 80,000 units and cost remain. August worth falls back to JPY 1,006,000, with `SYNTHFUND` marked `unpriced`; record a dated per-unit price. |
| Quantity/unit on trade lines | A price cannot recover units. The money-only ledger can stay balanced and cash can reconcile while quantity assertions fail; restore quantities from the broker statement. |
| Proven opening acquisition basis | A standalone opening can carry known units and book value while acquisition cost remains unknown. Market valuation can still work; retain verified opening inventory rather than inferring tax cost from a current quote. |

The checked `iris yearend --local --to ../fund-2027` workflow carries 80,000
units and the separately proven JPY 80,000 acquisition basis. Prices remain in
the user store; carrying an old observation into January does not make it a
new market observation.

With actual records and sync authority, Book sync publishes journals/units and
`iris price sync` reconciles the separate user price log. Price sync does not
regenerate a report. A successful price acknowledgement also does not prove
that the Book's sync was accepted.

| Surface | Inputs and freshness |
| --- | --- |
| Local CLI / local MCP | Current posted local files plus effective local prices, including pending captures; reruns reread them. |
| Single-book `iris api networth --book-id …` | Accepted cloud projections and the caller's accepted prices; excludes unsynced local inputs. |
| Web Net Worth / remote MCP | A frozen analytics generation. Check generation/snapshot `generatedAt`, selected source revisions and each `priceDate`; a price correction can wait for automatic daily generation or an authorized Web refresh. The previous successful report can remain visible during regeneration. |

The SQL fixture checks that correcting the August price to JPY 1.6 leaves the
old JPY 1,046,000 report intact until a new generation is built. The refreshed
value is JPY 1,054,000, with the same quantities and acquisition costs.

**Tax/regime references, checked 2026-10-24:** the fund manager's
[NAV explanation](https://direct.smd-am.co.jp/learn/guide/price/) demonstrates a
per-10,000 quotation. [NTA No.1464](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1464.htm)
(law reference date 2026-04-01) describes acquisition costs and the method for
repeated purchases; a generic FIFO or moving-average label is not a Japanese
tax determination. For an actual NISA account, confirm the broker's account
classification, the [FSA NISA rules](https://www.fsa.go.jp/policy/nisa2/know/index.html)
and [current eligible-product references](https://www.fsa.go.jp/policy/nisa2/products/).
A unit symbol, a note saying NISA or a successful validation does not establish
eligibility. Tax-return mapping and automatic product/regime classification
remain outside this management example.

## Balance assertions

A balanced journal can still leave the bank ten yen wrong. Record an observed
balance and compare it with the local ledger using `iris reconcile`. This is a
read-only check; it never creates adjusting entries. Save observations in the
optional `config/balance-assertions.yaml` file.

For example, a posted ¥1,000 opening and ¥10 payment leave ¥990 in `Assets:Bank`.
A statement saved as `raw/statement.csv` contains:

```csv
date,description,closing_balance
2026-01-31,Month end,990
```

Use `iris hash raw/statement.csv` for the canonical source hash. This example's
hash below belongs to exactly those bytes. Save the observation as:

```yaml
schema_version: 1
assertions:
  - id: bank-jan31
    date: 2026-01-31
    account: Assets:Bank
    measure: amount
    unit: JPY
    scope: posted
    expected: 990
    evidence:
      path: raw/statement.csv
      sha: sha256:47413ca394cff9cf18438ee55b45076994c84426b511e06fe5daafc3d05847bd
      locator: line 2 closing_balance
```

Run `iris reconcile` from the Book folder. It reports actual `990`, expected `990`
and difference `0`. If both sides of the payment are mistakenly recorded as ¥20,
double entry still balances, but reconciliation reports `980`, `990`, `-10`.
`iris validate` also reports failed observations.

- `date` is inclusive and must fall in the Book's fiscal year. Record opening
  balances in that year; included journals from another year are refused.
- `account` is one exact declared chart path, with no automatic child-account
  rollup. Expected balances use its normal direction: assets/expenses are
  debit-positive; liabilities/equity/income are credit-positive.
- `measure: amount` uses the Book's currency and amount precision. For a foreign
  denomination or fund units, use `measure: quantity` and that exact `unit`.
  Quantity follows debit/credit direction and the unit's precision; it does not
  use valuation prices. Missing quantities are not estimated.
- `scope` defaults to `posted`. Choose `posted-and-drafts` explicitly for an
  unapproved planning check. Expected values are natural decimal numbers or
  quoted decimal text at the relevant precision; they are never rounded to fit.
- Evidence requires a syncable `raw/` path, its `sha256:` hash and a locator such
  as a physical CSV line or PDF page. Missing/changed bytes stay unverified even
  when amounts match. Hash equality proves file identity, not bank authenticity
  or correct transcription of the observation.

The optional file supports at most 256 uniquely named observations. An empty
`assertions: []` checks none. Reads are bounded to 10,000 journals, 1,000,000 lines,
16 MiB per evidence file and 128 MiB of input. The output revision binds the
captured config, chart, assertions, journals and referenced evidence; it is not a
cloud acceptance receipt. Sync/clone keep the declarations; config seals protect
them. Rollover leaves them in the original Book so old observations are not
reused next year. Storage alone does not evaluate observations. Cloud close
previews run this same native check against accepted synced sources, and closing
is refused for mismatches or unavailable/changed evidence. The check binds accepted
source versions; it does not fetch an unpinned latest object or run Overlay code.
If a preview reports missing/stale source data after sync, the server's projections
need rebuilding before that Book can close. Financial ZIPs do not automatically
include raw evidence. Cloud close checks every accepted native view separately. Local root-only reconciliation still refuses unresolved view sources.

## Business/private expense allocation

Use `iris allocation` to split a documented gross expense charge by an explicit
business fraction. It returns exact amounts without changing files or posting
entries. Confirm the basis and treatment first; an account name cannot establish
a business percentage. The [NTA's necessary-expense guidance](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2210.htm)
requires records distinguishing the business portion of household-related costs.
The 1/4 fraction below is a synthetic owner-reviewed example, not a recommended rate.

Save this request as `raw/allocation-jan.json`:

```json
{
  "schema_version": 1,
  "gross_amount": "10001",
  "currency": "JPY",
  "scale": 0,
  "charge_kind": "expense",
  "period": {
    "from": "2026-01-01",
    "through": "2026-01-31"
  },
  "source": {
    "path": "raw/rent.csv",
    "sha": "sha256:e5a22bf56e640afc4880a0ef16dd353c3c56ead85111cd715d9b21dbe3652454",
    "locator": "L2"
  },
  "basis": {
    "id": "home-office-q1",
    "description": "One of four measured area units; synthetic owner-reviewed example",
    "numerator": 1,
    "denominator": 4,
    "period": {
      "from": "2026-01-01",
      "through": "2026-03-31"
    },
    "rounding": "floor",
    "evidence": {
      "path": "raw/area.csv",
      "sha": "sha256:b6303be8397f238136d4d6c925a41b20f5ffe70c0e737aeb3fb006876dc635de",
      "locator": "L2"
    }
  }
}
```

The source hashes refer to these exact synthetic CSV bytes, including their final
newlines. `L2` means physical line 2. Both source files stay in `raw/`:

`raw/rent.csv`:

```csv
period_from,period_through,description,gross_amount,currency
2026-01-01,2026-01-31,January rent,10001,JPY
```

`raw/area.csv`:

```csv
id,effective_from,effective_through,business_area_units,total_area_units,rounding
home-office-q1,2026-01-01,2026-03-31,1,4,floor
```

```bash
iris allocation --schema
iris allocation --input raw/allocation-jan.json
```

The result is gross `10001`, business `2500`, private `7501` JPY. Amounts and minor
units are exact strings. `evidence_verification: unchecked` means the calculator
has not opened the evidence files; review those sources separately. Retain the
request, calculation version, input hash and result in your Book's notes.
`input_sha` hashes the parsed request in canonical field order; formatting changes
preserve it.

All dates are inclusive. The whole charge period must fit inside one basis
period; a mid-period change needs an explicit source split first. Supply scale,
fraction and rounding: `floor` drops the business fraction of one minor unit,
`half_up` rounds a half up, and `ceil` rounds a nonzero fraction up. The private
share is always the exact remainder. Never independently round both shares or
allocate an already allocated amount again. The denominator is 1..1,000,000,000;
the numerator is 0..denominator. There is no default rate or rounding.

For two management Books owned by the same person, the paying personal Book can
record the following, using the Book's actual chart paths:

```yaml
schema_version: 1
date: 2026-01-10
status: posted
allocation_ref: notes/allocation-january.md
counterpart_book: allocation-business
counterpart_journal: journals/2026-01/2026-01-10-rent.md
lines:
  - {account: Expenses:Rent, debit: 7501}
  - {account: Assets:BusinessClearing, debit: 2500}
  - {account: Assets:Bank, credit: 10001}
attachments:
  - {path: raw/rent.csv, type: receipt, locator: L2}
  - {path: raw/bank.csv, locator: L3}
  - {path: raw/area.csv, locator: L2}
```

The business Book records the matching expense and clearing liability:

```yaml
schema_version: 1
date: 2026-01-10
status: posted
allocation_ref: notes/allocation-january.md
counterpart_book: allocation-personal
counterpart_journal: journals/2026-01/2026-01-10-rent.md
lines:
  - {account: Expenses:Rent, debit: 2500}
  - {account: Liabilities:PersonalClearing, credit: 2500}
attachments:
  - {path: raw/rent.csv, type: receipt, locator: L2}
  - {path: raw/area.csv, locator: L2}
```

Use the actual `book_id` values for the example's counterpart Book IDs.
These `counterpart_*` and `allocation_ref` fields are retained reference data;
they do not trigger cross-Book writes or posting. The full paying-bank movement
is **JPY 10,001**. When the business bank later pays JPY 2,500, debit its clearing
liability and credit its bank; in the personal Book debit the bank and credit
the receivable. This settlement adds no income or expense in this example.
A separate JPY 5,000 owner transfer uses equity/owner-transfer accounts in both
Books. Map accounts explicitly; analytical clearing is not a determination of
legal debts, related-party tax treatment or corporate accounting.

With personal/business opening banks of JPY 100,000/20,000, the complete checked
example ends at JPY 97,499/12,500 after settlement and that owner transfer. Both
clearing balances are zero. Consolidated expense is JPY 10,001 and income zero;
check those totals separately, since a duplicated expense and reimbursement
misclassified as income can leave net profit apparently correct. Use
`iris reconcile` for each Book's independently evidenced bank/clearing observations.

For `charge_kind: depreciation`, supply an already calculated **gross schedule
charge**. Keep the acquisition payment, original acquisition cost, method and
schedule book values intact. This calculator does not choose a depreciation
regime, allocate acquisition cost, decide asset ownership or automate mixed-use
asset posting. The existing asset task retains that limit. A full reversal
reverses the original recorded shares; partial refunds need a separate explicit
treatment. Neither tax eligibility nor posting/sync authority follows from a
successful calculation.

### Mixed-use equipment with a full acquisition basis

This checked manual pattern keeps one complete physical asset in the owner's
business management Book. The personal Book records its private-use expense;
it does not duplicate the asset. The method, 48-month life, JPY 1 residual and
3/5 use fraction are explicit assumptions for this example. They do not establish
tax eligibility, a statutory life, an allowed tax method or corporate treatment.

The business bank pays **JPY 240,049 in full**. Record debit `Assets:Equipment`
240,049 and credit `Assets:Bank` 240,049, with the original purchase reference.
Keep the original asset cost; do not replace it with the business fraction.
The example's asset frontmatter is:

```yaml
schema_version: 1
name: Shared equipment
category: equipment
acquisition_date: 2026-05-01
acquisition_cost: 240049
salvage_value: 1
useful_life_months: 48
method: straight_line
asset_account: Assets:Equipment
depreciation_expense_account: Expenses:Depreciation
accumulated_depreciation_account: Assets:AccumulatedDepreciation
acquisition_journal: '[[2026-05-01-equipment]]'
```

Read the native gross schedule and choose one posting cadence:

```bash
iris asset schedule --year 2026
iris export assets --year 2026 --out raw/assets-2026.csv
iris asset depreciate --year 2026
```

The engine calculates eight May–December charges of JPY 5,001: gross depreciation
JPY 40,008 and closing carrying value JPY 200,041. `depreciate` writes a draft,
not a posted journal. Review it under the Book's authority before posting.
Its gross debit to depreciation expense and credit to accumulated depreciation
must remain exactly once. Reruns preserve existing proposals; monthly and annual
cadences cannot be mixed. A known sealed year, another active writer or a year
outside this Book refuses new proposals. A missing seal mirror is not a live
cloud-state check.

For the worked example, `raw/gross-depreciation.csv` is a retained compact snapshot
of those native figures and the asset source hash. It is generated calculation
support, not an original supplier or bank statement. Tests compare its figures
with the actual engine and native export. `raw/use.csv` holds the assumed use
basis. These exact synthetic bytes match the request's hashes:

`raw/gross-depreciation.csv`:

```csv
period_from,period_through,gross_depreciation,closing_book_value,asset_sha
2026-05-01,2026-12-31,40008,200041,sha256:b0b0c527112dd0b042442edc23fb30bd0485969cc5fa97cf7ae7b5b62a4be4c9
```

`raw/use.csv`:

```csv
id,effective_from,effective_through,business_use_units,total_use_units,rounding
equipment-2026,2026-05-01,2026-12-31,3,5,floor
```

Save the request as `raw/allocation-depreciation.json` and calculate the split:

```json
{
  "schema_version": 1,
  "gross_amount": "40008",
  "currency": "JPY",
  "scale": 0,
  "charge_kind": "depreciation",
  "period": {
    "from": "2026-05-01",
    "through": "2026-12-31"
  },
  "source": {
    "path": "raw/gross-depreciation.csv",
    "sha": "sha256:bb3d3bea2f8047617501c95b6328d76f2c98a5c29e9c0d389c9bf8cf2716172f",
    "locator": "L2"
  },
  "basis": {
    "id": "equipment-2026",
    "description": "Three of five recorded use units; synthetic owner-reviewed annual charge",
    "numerator": 3,
    "denominator": 5,
    "period": {
      "from": "2026-05-01",
      "through": "2026-12-31"
    },
    "rounding": "floor",
    "evidence": {
      "path": "raw/use.csv",
      "sha": "sha256:69bf6934a2e83cf7712fb7fc2d5afd90aad2809232f99b52c3502a5a10729c3a",
      "locator": "L2"
    }
  }
}
```

```bash
iris allocation --input raw/allocation-depreciation.json
```

The result is business `24004`, private `16004` JPY. This is **one annual rounding
operation**. Allocating and flooring each JPY 5,001 monthly charge would instead
give JPY 24,000 business expense. Record the chosen charge grain and keep it
consistent; never silently substitute monthly rounding for the annual choice.
A basis change inside the charge period requires an explicit split first.

After keeping the gross depreciation once, author this separate reclassification
in the business Book, using the actual account paths and counterpart Book ID:

```yaml
schema_version: 1
date: 2026-12-31
status: posted
tags: [private-use-reclassification]
allocation_ref: notes/equipment-allocation.md
source_journal: journals/2026-12/auto/dep-annual-equipment.md
counterpart_book: equipment-personal
counterpart_journal: journals/2026-12/2026-12-31-equipment-use.md
lines:
  - {account: Equity:OwnerDrawings, debit: 16004}
  - {account: Expenses:Depreciation, credit: 16004}
attachments:
  - {path: raw/gross-depreciation.csv, locator: L2}
  - {path: raw/use.csv, locator: L2}
```

The personal management Book records the matching private expense/equity entry:

```yaml
schema_version: 1
date: 2026-12-31
status: posted
allocation_ref: notes/equipment-allocation.md
counterpart_book: equipment-business
counterpart_journal: journals/2026-12/2026-12-31-private-use.md
lines:
  - {account: Expenses:EquipmentUse, debit: 16004}
  - {account: Equity:BusinessUseContribution, credit: 16004}
attachments:
  - {path: raw/gross-depreciation.csv, locator: L2}
  - {path: raw/use.csv, locator: L2}
```

Both entries above show the fixture's final posted form. Author/review drafts and
post only under the Book's policy. These references are passive data; the
calculator creates no entries and writes neither Book. No bank moves for this
private-use recognition, and accumulated depreciation is not credited again.

The checked closing figures are:

| Figure | Business | Personal | Combined |
| --- | ---: | ---: | ---: |
| Bank | 259,951 | 100,000 | 359,951 |
| Expense | 24,004 | 16,004 | 40,008 |
| Income | 0 | 0 | 0 |
| Net assets | 459,992 | 100,000 | 559,992 |

The business asset remains gross cost 240,049 less accumulated depreciation
40,008 = carrying value 200,041. Check original basis, bank, asset balances and
separate/consolidated income and expense totals. Structural validation and bank
reconciliation alone can still pass if the purchase is expensed again or the
private reclassification is repeated; the complete fixture's controls reject
those mistakes. Retain the request, result and references, review the ledger,
and run `iris validate` / `iris reconcile` before authorized sync. Tax-return
mapping and automatic mixed-use asset posting remain unsupported.

### Update a home-office basis from its effective date

Extend the earlier January rent example with a separately evidenced April
charge. Keep January's `raw/area.csv`, request, note, bank observations and
journals unchanged. Its 1/4 basis ends March 31. The newly measured 1/3 basis
starts April 1 and has its own source path, hash and inclusive effective period:

```csv
basis_id,effective_from,effective_through,business_units,total_units,rounding
home-office-april,2026-04-01,2026-12-31,1,3,floor
```

```csv
period_from,period_through,supplier,gross_amount,currency
2026-04-01,2026-04-30,Synthetic landlord,10001,JPY
```

Save the explicit request as `raw/allocation-april.json` in both Books:

```json
{
  "schema_version": 1,
  "gross_amount": "10001",
  "currency": "JPY",
  "scale": 0,
  "charge_kind": "expense",
  "period": {
    "from": "2026-04-01",
    "through": "2026-04-30"
  },
  "source": {
    "path": "raw/rent-april.csv",
    "sha": "sha256:b84be0483163d0b181009ef285f5b55d851ff53da0d728b8ba6cc2c9265c2636",
    "locator": "L2"
  },
  "basis": {
    "id": "home-office-april",
    "description": "One of three newly measured area units; effective April 1 only",
    "numerator": 1,
    "denominator": 3,
    "period": {
      "from": "2026-04-01",
      "through": "2026-12-31"
    },
    "rounding": "floor",
    "evidence": {
      "path": "raw/area-april.csv",
      "sha": "sha256:04f1cbc2994f0866b4db28bd52707223dbfa8e6ec41d7e1132ce38a700594d64",
      "locator": "L2"
    }
  }
}
```

Run the same pure calculator; it returns gross 10,001, business 3,333,
private 6,668 and `evidence_verification: unchecked`. Verify the cited source
bytes and facts separately, and retain the result/input hash in
`notes/allocation-april.md`. Personal pays the full 10,001 on April 10:

```bash
iris allocation --input raw/allocation-april.json
```

`personal/journals/2026-04/2026-04-10-rent.md`:

```yaml
schema_version: 1
date: 2026-04-10
status: posted
allocation_ref: notes/allocation-april.md
counterpart_book: allocation-business
counterpart_journal: journals/2026-04/2026-04-10-rent.md
lines:
  - {account: Expenses:Rent, debit: 6668}
  - {account: Assets:BusinessClearing, debit: 3333}
  - {account: Assets:Bank, credit: 10001}
attachments:
  - {path: raw/rent-april.csv, locator: L2}
  - {path: raw/area-april.csv, locator: L2}
  - {path: raw/bank-april.csv, locator: L2}
```

`business/journals/2026-04/2026-04-10-rent.md`:

```yaml
schema_version: 1
date: 2026-04-10
status: posted
allocation_ref: notes/allocation-april.md
counterpart_book: allocation-personal
counterpart_journal: journals/2026-04/2026-04-10-rent.md
lines:
  - {account: Expenses:Rent, debit: 3333}
  - {account: Liabilities:PersonalClearing, credit: 3333}
attachments:
  - {path: raw/rent-april.csv, locator: L2}
  - {path: raw/area-april.csv, locator: L2}
  - {path: raw/bank-april.csv, locator: L2}
```

On April 20 the business Book debits `Liabilities:PersonalClearing` 3,333
and credits `Assets:Bank` 3,333. The personal Book debits `Assets:Bank` 3,333
and credits `Assets:BusinessClearing` 3,333. Income/expense does not change on
reimbursement. Keep the original January 5,000 owner transfer in equity.

| Through April 30, January and April charges only | Business | Personal | Combined |
| --- | ---: | ---: | ---: |
| Bank | 9,167 | 90,831 | 99,998 |
| Rent expense | 5,833 | 14,169 | 20,002 |
| Income | 0 | 0 | 0 |
| Clearing balance | 0 | 0 | 0 |

```bash
iris validate --json /path/to/business
iris reconcile /path/to/business
iris report pl --from 2026-01-01 --to 2026-04-30 /path/to/business
iris validate --json /path/to/personal
iris reconcile /path/to/personal
iris report pl --from 2026-01-01 --to 2026-04-30 /path/to/personal
```

The pure calculator rejects April's basis for January, January's expired basis
for April, and a whole charge spanning March 15–April 15 under either basis.
It does not select a latest ratio or invent proration. Obtain separately
evidenced charge amounts for each period before calculating; the example does
not establish a deductible percentage, legal expense allocation or tax-return
mapping. For Japanese income-tax evidence requirements, see
[NTA No. 2210](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2210.htm)
(law as of April 1, 2026; checked October 24, 2026). Reversals must retain the original rounded shares. Correcting an old
source is a separate reviewed correction with its original identity retained.

The checked complete example retains all original January files plus April
sources and eight observations per Book. Checks bind
the old bytes, new dated evidence, exact results, full cash movements and
separate expense totals. A balanced retroactive 1/3 reallocation of January
keeps bank reconciliation but fails the clearing and expense checks.

## Shared-household advances and refundable deposits

Use separate personal Books for parties who each maintain their own records.
This synthetic management example assumes unrelated co-tenants Ari and Kei
jointly own refundable deposit claims of JPY 40,000 and 20,000 under their
original agreement. Confirm the actual rights, payer and settlement terms first.
Who paid and who lives together do not establish ownership or a tax treatment.
For disputed rights or deductions, keep the disputed claim explicit and obtain
advice before recognizing a final loss. No package automates either Book.

Retain `raw/agreement.csv` in both Books:

```csv
date,deposit_total,ari_claim,kei_claim,currency
2026-05-01,60000,40000,20000,JPY
```

Ari pays the full 60,000 on May 1. Ari retains their own 40,000 deposit asset
and a 20,000 receivable from Kei. Kei recognizes a 20,000 deposit asset and a
20,000 payable to Ari. The final posted forms are below; author/review drafts
and post only under each Book's policy. The `allocation_ref` and reciprocal
counterpart fields are passive references. They grant no access or write authority.

`ari/journals/2026-05/2026-05-01-deposit.md`:

```yaml
schema_version: 1
date: 2026-05-01
status: posted
allocation_ref: notes/deposit-settlement.md
counterpart_book: household-kei
counterpart_journal: journals/2026-05/2026-05-01-deposit.md
lines:
  - {account: Assets:RefundableDeposit, debit: 40000}
  - {account: Assets:KeiReceivable, debit: 20000}
  - {account: Assets:Bank, credit: 60000}
attachments:
  - {path: raw/agreement.csv, locator: L2}
  - {path: raw/bank.csv, locator: L3}
```

`kei/journals/2026-05/2026-05-01-deposit.md`:

```yaml
schema_version: 1
date: 2026-05-01
status: posted
allocation_ref: notes/deposit-settlement.md
counterpart_book: household-ari
counterpart_journal: journals/2026-05/2026-05-01-deposit.md
lines:
  - {account: Assets:RefundableDeposit, debit: 20000}
  - {account: Liabilities:AriPayable, credit: 20000}
attachments:
  - {path: raw/agreement.csv, locator: L2}
  - {path: raw/bank.csv, locator: L3}
```

Keep each independent bank statement as `raw/bank.csv`. The full payment
leaves Ari's bank, and Kei's bank changes only on reimbursement and payout.

`ari/raw/bank.csv`:

```csv
date,description,outflow,inflow,balance
2026-01-01,Opening,0,0,200000
2026-05-01,Landlord deposit,60000,0,140000
2026-05-03,Kei reimbursement,0,20000,160000
2026-12-28,Landlord refund,0,54000,214000
2026-12-30,Kei refund payout,18000,0,196000
```

`kei/raw/bank.csv`:

```csv
date,description,outflow,inflow,balance
2026-01-01,Opening,0,0,100000
2026-05-01,No bank payment,0,0,100000
2026-05-03,Ari reimbursement,20000,0,80000
2026-12-28,Refund held by Ari,0,0,80000
2026-12-30,Ari refund payout,0,18000,98000
```

On December 28 the settlement confirms an actual 6,000 deduction, with
4,000/2,000 shares, and a 54,000 refund to Ari. Retain the original settlement,
including the payer and physical row locator, in both Books:

```csv
date,original_deposit,actual_deduction,bank_refund,ari_refund,kei_refund,currency
2026-12-28,60000,6000,54000,36000,18000,JPY
```

The deposit assets now clear. Only the actual deduction becomes expense.
Ari owes Kei the remaining 18,000 until the separate December 30 payout.

`ari/journals/2026-12/2026-12-28-refund.md`:

```yaml
schema_version: 1
date: 2026-12-28
status: posted
allocation_ref: notes/deposit-settlement.md
counterpart_book: household-kei
counterpart_journal: journals/2026-12/2026-12-28-refund.md
lines:
  - {account: Assets:Bank, debit: 54000}
  - {account: Expenses:MoveOut, debit: 4000}
  - {account: Assets:RefundableDeposit, credit: 40000}
  - {account: Liabilities:KeiPayable, credit: 18000}
attachments:
  - {path: raw/settlement.csv, locator: L2}
  - {path: raw/bank.csv, locator: L5}
```

`kei/journals/2026-12/2026-12-28-refund.md`:

```yaml
schema_version: 1
date: 2026-12-28
status: posted
allocation_ref: notes/deposit-settlement.md
counterpart_book: household-ari
counterpart_journal: journals/2026-12/2026-12-28-refund.md
lines:
  - {account: Assets:AriReceivable, debit: 18000}
  - {account: Expenses:MoveOut, debit: 2000}
  - {account: Assets:RefundableDeposit, credit: 20000}
attachments:
  - {path: raw/settlement.csv, locator: L2}
  - {path: raw/bank.csv, locator: L5}
```

Record the remaining entries explicitly in each Book:

| Date / event | Ari | Kei |
| --- | --- | --- |
| January 1 opening | Dr Bank 200,000 / Cr Opening equity 200,000 | Dr Bank 100,000 / Cr Opening equity 100,000 |
| May 3 reimbursement | Dr Bank 20,000 / Cr KeiReceivable 20,000 | Dr AriPayable 20,000 / Cr Bank 20,000 |
| December 30 payout | Dr KeiPayable 18,000 / Cr Bank 18,000 | Dr Bank 18,000 / Cr AriReceivable 18,000 |

Use `Assets:Bank`, `Assets:RefundableDeposit` and `Assets:<Name>Receivable` as
asset accounts, `Liabilities:<Name>Payable` as liability, `Equity:Opening` as
equity and `Expenses:MoveOut` as expense. `<Name>` is the other person's name.
Repayments/refunds add no income. Before the actual deduction, the deposit is
still an asset; treating the initial payment as an expense loses the claim.

| Observation | Ari bank | Kei bank | Deposit assets, combined | Reciprocal debt |
| --- | ---: | ---: | ---: | ---: |
| May 2, before reimbursement | 140,000 | 100,000 | 60,000 | 20,000 |
| May 4, after reimbursement | 160,000 | 80,000 | 60,000 | 0 |
| December 29, before payout | 214,000 | 80,000 | 0 | 18,000 |
| December 31, after payout | 196,000 | 98,000 | 0 | 0 |

Reconcile banks, deposit claims and both sides of outstanding debt using dated
balance assertions with exact source hashes/locators; a successful bank check
alone does not prove the deposit or income/expense classification. With the
records and observations in place, run these read-only checks:

```bash
iris validate --json /path/to/ari
iris reconcile /path/to/ari
iris report pl --from 2026-01-01 --to 2026-12-31 /path/to/ari
iris validate --json /path/to/kei
iris reconcile /path/to/kei
iris report pl --from 2026-01-01 --to 2026-12-31 /path/to/kei
```

Expect income zero in each Book, expense 4,000/2,000, all deposit/clearing
balances zero, and combined cash 294,000 = opening 300,000 − actual loss 6,000.
The two-Book totals are a manual management check, not a new consolidation
command. The complete checked example has five journals and ten evidence-backed
observations per Book.
It also checks balanced mistakes: deposit expensing, refund income, a missing
counterparty bank movement, premature settlement and a repeated payout.
Real agreements can assign different rights; do not copy these assumptions
into a sole-tenant, business, disputed or otherwise different arrangement.
For lease-source review, [MLIT's model lease and explanatory material](https://www.mlit.go.jp/jutakukentiku/house/jutakukentiku_house_tk3_000023.html)
are a reference (checked October 24, 2026); they do not establish the particular
joint claims or deduction shares assumed here.

## Chart of accounts — `config/chart-of-accounts.yaml`

Typed config, chart, rule, journal and asset readers refuse unresolved root
`views`, including a key supplied through a YAML merge. Resolve the selected
accounting view before typed decoding, and edit the original document to retain
other payloads. Structured journal replacement also refuses stored views because
its reduced DTO cannot preserve them. Removing `views` loses alternative data.

Cloud storage accepts bounded view-bearing `config/book.yaml`, journal and asset sources
without executing Overlay code. Declare at most 16 Book views and one default;
all variants must pass native parsing, balance, account/reference and sealed-period
checks. Views share Book identity, fiscal bounds, currency, unit precision and host
integrity settings. Journal lifecycle status belongs to the shared root and cannot
be overridden in a payload. Sync and clone preserve the unresolved source.

Web displays the default as an **unapproved view preview**. Human posting approves
the exact shared source version, not its view-specific financial results. Named-view approved reports require separately retained native financial acceptance. See [financial generations](cli-reference.md#iris-financial). Close requires every declared view accepted and final; SQLite stores each separately and keeps the default in its ordinary tables.
Adding declarations or changing the default while journal or asset view payloads exist requires
a coherent rebuild and is currently refused. Referenced declarations cannot be removed.
Chart and rule sources with their own `views` remain unsupported in cloud ingestion.

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
  - path: 資本:元入金
    type: equity
    retained_earnings: true   # optional — where `iris yearend` folds net income
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

`retained_earnings: true` marks the equity account
[`iris yearend`](cli-reference.md#iris-yearend) folds the year's net income
into — 資本:元入金 for a sole proprietor, 純資産:繰越利益剰余金 for a company.
At most one account may set it, and it must be `type: equity`; `iris validate`
and the cloud refuse a chart that breaks either rule. When no account sets it,
`iris yearend` uses the chart's only equity account, so the starter charts
(which have exactly one) leave it out. Set it once your chart has more than
one equity account.

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
  overlay: jp-declining-balance@2026.10.1
  recipe: jp-declining-balance.teiritsu
  bindings: 5
  primitives: {declining_table: 2, flat_table: 2}
  params: {full_year_confirmed: true, cost: 480000, life: 4, rate: 0.500, guarantee: 0.12499, revised: 1.000, start: 2027-03}
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

Native calculation accepts at most 4,096 schedule rows and 4,096 useful-life
months per asset. Table calculators check the derived row count and calendar
range before allocating; no generated month may exceed year 9999. These are
implementation limits, not tax rules. Local schedule, depreciation and asset
export requests also stop at 4,096 asset files, 64 MiB of source or 100,000 total schedule rows.
Asset files are bounded to 256 KiB and must be regular files. An invalid or
excessive schedule fails the request; it never becomes a successful zero-valued
summary or partial CSV. New recipe executions record table primitive version 2; retained
version-1 records replay their original arithmetic within the same host limits.
Replay never substitutes the latest version for missing or unknown provenance.

MCP table tools take integer minor units and accept exact decimal integer
strings for large amounts. Read `amount_exact` / `total_exact` or the generated
YAML rather than converting large numeric fields to floating point. Set the
tool's `scale` to the destination Book's scale; its default is 0. For example,
12,345 minor units with `scale: 2` becomes YAML `amount: 123.45`, which parses
back to the same 12,345 units. The result reports the scale used.

Your AI assistant builds the table for you. When the book's region overlay
has a **recipe** for the method — Japan's 定率法 is `jp-declining-balance.teiritsu` — it runs
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
version (`jp-declining-balance@2026.10.1`, or `book:<hash>` for a recipe from your own
`config/overlays/`), the recipe, the engine versions it ran under, and the
inputs you gave — the rates from the published table, the useful life, the
first row's month. `iris validate` **replays** the recipe with those inputs and
refuses the file if the recorded rows differ, so a switch a year late no
longer passes just because the total is right. The inputs stay on the file for
your 税理士 to check against the published table. A table without
`schedule_source` is checked for shape only. Replay uses the exact recorded
version retained inside the Book, even when it differs from the current
selection. Embedded bodies and the download cache never substitute for a missing
Book source. Missing definitions, changed local hashes and unavailable engine
capabilities are reported explicitly.

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
the region overlay (for Japan, `jp-tax-filing.shouhizei-general` and
`jp-tax-filing.shouhizei-simplified` for the 消費税 return) sums the posted journals and
combines them the way the return needs; `iris overlay recipe … --apply --out
filings/jp-tax-filing.shouhizei-general.md` records the result with the same
provenance as a schedule:

```yaml
---
schema_version: 1
filing: jp-tax-filing.shouhizei-general
period: {from: 2026-01-01, to: 2026-12-31}
source:
  overlay: jp-tax-filing@2026.10.1
  recipe: jp-tax-filing.shouhizei-general
  bindings: 5
  params: {from: 2026-01-01, to: 2026-12-31, scope_confirmed: true}
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

Published function packages are selected explicitly by `overlay:` or `overlays:`
in `book.yaml`.
A book may add its own layer on top:

```text
config/overlays/
├── overlay.yaml        # id: book / extends: jp-tax-classification@2026.10.1
├── fields.yaml         # optional field types and choices
├── functions.yaml      # optional shared expressions
├── rules/*.yaml        # extra checks (an id matching a published rule overrides it)
├── recipes/*.yaml      # extra computations
├── derive/*.yaml       # extra derived-value proposals
└── tests/*.yaml        # golden cases — `iris overlay test` runs them
```

With multiple published pins, the layer's `extends` is a list containing all
of them. Local expressions inherit the regional primary package's CEL helpers;
other published packages keep their helpers private. An override of an existing
rule, derivation or recipe keeps that item's package ID for `overlay_settings`.
New book-local items use the reserved `book` settings key, independent of the
published pins and the local manifest's ID:

```yaml
overlay_settings:
  book:
    rules:
      local.memo:
        params: {memo: invoice}  # a new rule declared in config/overlays/rules/
```

Use the declared item ID for rules/derivations and the short recipe name for
new local recipe defaults. Published field definitions cannot be replaced by
the book layer. When adding a required rule input, sync its book-local definition
first, then its settings. Use the local reviewed upgrade to check the complete
candidate selection, settings and matching `extends` before changing pins.
It retains the original local definition and parents. Cloud stores these bounded
sources without compiling or evaluating them. An interrupted trusted parent/pin
mismatch blocks local execution; inspect the retained sources and make a new
explicit upgrade review before continuing.

Rules and recipes are written in [CEL](https://cel.dev) expressions over the
book's records — a language with no file or network access and a bounded cost,
which is what makes it safe for your AI to write them. `iris validate` applies
your trusted layer next to the explicitly selected published packages; cloud
keeps native integrity and access guards without executing the layer. Only the
book's Owner can change these files. The first time
a machine meets a version of this layer it shows the files and asks once
(`iris overlay trust` records the answer); until then only the published
overlay applies. `iris overlay list` and published MCP recipe tools remain
available; the CLI and MCP `describe_overlay.issues` report
`overlay.book-layer-untrusted`. Book-local settings are checked when the layer
is trusted. A recipe from your layer records `book:<hash>` as its source,
so a reviewer can see a schedule came from a book-specific recipe. The published
overlays are open source (Apache-2.0) in the public
[`irisbooks/overlays`](https://github.com/irisbooks/overlays) repository. A layer
that proves useful beyond one book can be proposed there as a pull request.

Trust is machine-local and does not travel with a clone. A retained historical
definition can be reviewed under `config/overlay-packages/local/HASH/` and trusted
explicitly with `iris overlay trust --source book:HASH [path]`. This checks its
exact content and original Book-contained parents without changing selection.
Trusting today's layer does not grant trust to another historical hash; missing
or changed retained sources remain unavailable for replay.

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

Before reusing a parse cache, compare its `source_sha` with `iris hash` of the
current source. If it changed, reconcile changed rows and existing journal
links before importing further entries; preserve completed row state.

## What syncs and what doesn't

With cloud sync, `iris sync` mirrors the **syncable** files to the cloud:

- **Synced:** `journals/`, `assets/`, `filings/`, `notes/` (including parse
  caches), `AGENTS.md` (shared agent contract), `raw/` (verbatim bytes), `config/book.yaml`,
  `config/chart-of-accounts.yaml`, `config/rules.yaml`,
  `config/balance-assertions.yaml`, `config/overlays/`, `config/overlay-packages/`.
- **Not synced:** `.iris/` (runtime state), `README.md` / `CLAUDE.md` (local entry files), and `compiled/` (regeneratable).

See also: [Core concepts](concepts.md) ·
[CLI command reference](cli-reference.md).

### Independent annual books and acquisition openings

`iris yearend` writes complete opening inventory in the next book's
`config/book.yaml`. Each book can be valued independently, without a link to
an earlier book. Select earlier books only to include their own historical periods.

```yaml
opening_inventory:
  - account: Assets:Fund
    unit: FUND
    method: fifo
    quantity: 100
    carrying_value_minor: 1200000
    acquisition_cost_minor: 1000000
    lots:
      - id: original-purchase
        date: 2025-11-01
        quantity: 100
        cost_minor: 1000000
```

Quantities are integers at the unit's scale; money is integer book-currency
minor units. Carrying value and acquisition cost are separate. Carrying value
also disambiguates a native-currency cash residual from a unit holding in the
same account. FIFO/specific openings retain original lots and their dates;
moving-average openings use a quantity/cost pool without lots. A null acquisition
cost means unknown. The opening journal still states the monetary/quantity
balance and must reconcile with these fields within this book.
Do not infer acquisition cost from a revalued opening amount.

Explicit lot IDs are preserved. When a purchase omits its lot ID, analytics derives
one from the fiscal year, journal path and original line index within this book’s
inventory. Changing the book’s cloud ID does not change that lot ID.
