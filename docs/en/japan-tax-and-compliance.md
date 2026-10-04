# Japan tax & compliance

IrisBooks is built for Japanese bookkeeping. This page covers the things a
Japanese owner or 税理士 needs: qualifying for 優良電子帳簿, classifying
consumption tax (消費税), depreciating fixed assets, and closing the year.

> **How IrisBooks splits the work.** The engine handles the universal,
> stable parts — double-entry math, per-line classification, totals, data
> exports. The year's *forms* — which change yearly and vary by municipality —
> are filled by your AI against the data IrisBooks produces, then reconciled
> back. So you'll see "IrisBooks gives you the numbers; your AI fills the
> form, IrisBooks checks it reconciles." That's deliberate.

## 優良電子帳簿 — the three requirements

First, the context. The full 65万円 青色申告 special deduction requires meeting
the 55万円 conditions plus *either* of two routes: filing electronically via
**e-Tax**, or keeping your books as **優良電子帳簿** under 電子帳簿保存法. So
優良 status is optional — one of two routes, not a requirement. Its own
distinct benefit is a 5% reduction of 過少申告加算税, and claiming it requires
notifying your tax office in advance (届出).

優良電子帳簿 takes three capabilities, and IrisBooks maps directly onto them:

| Requirement | What it means | In IrisBooks |
| --- | --- | --- |
| **訂正・削除の履歴の確保** | A record of every correction and deletion | The durable server history: `iris api history`, the web app **Activity** timeline + per-journal **History** panel |
| **帳簿間の相互関連性の確保** | Entries in one book trace to the matching entries in related books (e.g. journal ↔ general ledger) | Inherent in the design: the ledger and reports are derived live from the journals, and every ledger row carries the journal file it came from (`iris report ledger`, the web app **Accounts** ledger) |
| **検索機能の確保** | Search by date, amount, and counterparty (combinable) | `iris search`, and the filters on the web app **Journals** page |

The second requirement deserves a word, because IrisBooks meets it by
architecture rather than by a feature. In traditional bookkeeping, entries
are transcribed (転記) from the journal into the general ledger, so the two
books must carry a shared reference — typically a journal number — for an
auditor to match them up. IrisBooks has no transcription step: the journal
files are the single source, and the general ledger, trial balance, and
statements are derived from them on demand. Every ledger row cites the
journal file it came from, so the relationship between books is preserved
natively — nothing is copied, so nothing can drift apart.

Two of the three — **search** and **book-to-book traceability** — work fully
offline (`iris search`, `iris report ledger`). The third — the
**correction/deletion history** — has to be trustworthy to an auditor, which
only the server-side record provides. That's why it lives on the cloud side:
local git history is *not* auditor-trustable.

Separately from the three requirements, every journal also cites its **source
documents** — `iris show <path>` and the **Cited by** panel in the web app's
Raw documents browser walk that link in both directions. That journal ↔
evidence trail is what 電子帳簿保存法 asks of scanned paper documents
(スキャナ保存, for 重要書類), and it is plain audit hygiene besides: an
auditor can go from any entry to its receipt and back.

> **Scope of the 優良 claim.** All three capabilities must hold *together*,
> so 優良電子帳簿 applies only to a book kept on cloud sync.
> A **local-only book is not covered**: search and book-to-book traceability
> still work, but there is no auditor-trustable correction/deletion history.
> The claim also holds only **while the book stays on the service**. If you
> **delete a book** (after a 30-day window, all server data is permanently
> destroyed — including the correction history), the
> durable history is gone and the book no longer qualifies. As with paper
> books, the legal duty to preserve your books — including that history —
> for the statutory retention period (7 years, up to 10 in some corporate
> cases) is yours. Before deleting a book, keep your own copy of the book
> folder and of its record from `iris api history --all --json`
> (see [Audit handoff](#audit-handoff)).

> **Seals** (closing a year) lock the period — writes into a sealed year are
> refused for journals and accounting dependencies until reopening; changes
> to that scope made while reopened are flagged
> in that history. See [Year-end close](#year-end-close).

## Consumption tax (消費税)

Whether you manage consumption tax at all depends on your status, declared
once in `config/book.yaml`:

```yaml
consumption_tax:
  status: taxable          # taxable (課税事業者) | exempt (免税事業者)
  accounting: tax_included # tax_included (税込) | tax_excluded (税抜)
  method: general          # general (本則) | simplified (簡易課税)
  business_class: 5        # 1..6, only for simplified
```

- A **免税事業者** (no `consumption_tax` block, or `status: exempt`) records
  tax-inclusive amounts as ordinary 売上 / 経費 with no tax detail and files no
  consumption-tax return. You can skip the rest of this section.
- A **課税事業者** classifies each relevant journal **line** with a `tax`
  block, all year long. At year-end the totals by category and rate drive the
  消費税申告書 — which your AI fills against the figures IrisBooks sums.

### Classifying a line

Add a `tax` block to the lines that carry consumption tax:

```yaml
lines:
  - account: 収益:売上
    credit: 100000
    tax:
      category: taxable_sale   # 課税売上
      rate: "10"               # standard 10%
  - account: 費用:消耗品費
    debit: 5000
    tax:
      category: taxable_purchase
      rate: "10"
      invoice: true            # you hold a qualifying invoice (適格請求書)
```

**Categories** (`category`):

| Token | 税区分 | Carries a rate? |
| --- | --- | --- |
| `taxable_sale` | 課税売上 | yes (positive) |
| `taxable_purchase` | 課税仕入 | yes (positive) |
| `exempt_sale` | 非課税売上 | no |
| `exempt_purchase` | 非課税仕入 | no |
| `export_sale` | 免税売上(輸出) | `0` (or omit) |
| `out_of_scope` | 不課税 / 対象外 | no |
| `securities_sale` | 有価証券譲渡 | no |

**Rate tokens** (`rate`): `"10"` (standard), `"8r"` (軽減税率 8%), `"8o"`
(旧/経過措置 8%, distinct from `8r`), `"5"`, `"3"` (legacy), `"0"` (export).

**Invoice flag** (`invoice`): on a purchase line, whether you hold a qualifying
invoice under the 適格請求書等保存方式 (invoice system, Oct 2023 onward).

**Simplified method** (`method: simplified`): each 課税売上 line needs a
事業区分 (`business_class`, 第1〜6種). It defaults to the book-level
`business_class` but can be overridden per line.

`iris validate` checks these for coherence — that a category is known, that a
rate matches its category (e.g. `taxable_sale` needs a positive rate, an
`export_sale` is 0%), and that a simplified-method sale has a valid business
class. The detailed classification rules (区分判定, 簡易課税 事業区分, invoice
経過措置) are tax law, not product behavior — your AI checks the NTA's current
pages when classifying, and the AI-facing manual (served at `/llms-full.txt`)
summarizes them with the authoritative citations. IrisBooks doesn't ship a
frozen copy of rules that change; iris validates, it doesn't legislate.

### The year-end figures

The sums the return needs come from the engine, not from anyone re-adding
lines by hand:

```bash
iris report sum --by tax.category,tax.rate --from 2026-01-01 --to 2026-12-31
```

groups every posted line by its classification and totals it exactly (add
`tax.invoice` for the invoice-method split, `tax.business_class` under 簡易課税).
Note the 課税期間 is the calendar year for individuals, your fiscal year for a
法人 (`--year`).

The Japan overlay goes one step further with two **recipes** that combine the
sums the way the 申告書 needs them: `jp.shouhizei-general` (本則課税 — sales and
purchases by rate, the invoice / non-invoice split at the 経過措置 percentage
you pass, the 課税売上割合, net tax and the payable amount rounded down to
¥100) and `jp.shouhizei-simplified` (簡易課税 — sales tax by 事業区分 and the
deemed purchase tax at the みなし仕入率 you pass). `iris overlay recipe
jp.shouhizei-general --set from=2026-01-01 --set to=2026-12-31 --set
non_invoice_pct=80 --write filings/jp.shouhizei-general.md` records the
figures under `filings/` with provenance, and `iris validate` re-runs the
recipe against the journals from then on — a posted correction after filing
shows up as an error until the recipe is re-run. Your AI fills the form from
the recorded figures. The division of labor stays: **IrisBooks sums, your AI
files.**

On a **税抜経理** book (`accounting: tax_excluded`), `iris validate` also
proposes, as a hint, the consumption tax inside each classified line that has
no `tax.amount` yet; `iris validate --fix` records it, and your AI books that
amount on 仮払消費税 / 仮受消費税 — the arithmetic is iris's, the entry is the
AI's.

## Fixed assets and depreciation

Describe each depreciable asset as a file under `assets/YYYY/<name>.md`:

```yaml
---
name: "MacBook Pro 16"
acquisition_date: 2026-04-15
acquisition_cost: 480000
salvage_value: 1
useful_life_months: 48        # 耐用年数 4 years × 12
method: straight_line         # straight_line | declining_balance | expensed
asset_account: "資産:工具器具備品"
depreciation_expense_account: "費用:減価償却費"
accumulated_depreciation_account: "資産:減価償却累計額"
---
```

- **`useful_life_months`** comes from the 耐用年数省令 tables — your AI looks
  up the right life on the NTA's current pages (耐用年数省令 別表第一・第二;
  for 定率法, the 償却率 in 別表第十) and records the resolved number on the
  file, so the book carries its own justification and its git history answers
  "which table revision was this?".
- **Methods**: `straight_line` (定額法), `declining_balance` (定率法), or
  `expensed` (immediate write-off). 定額法 and 即時償却 iris computes for you.
  For 定率法 your AI records the table on the file (see below), because the
  switch to 改定償却率 is a Japanese rule and iris deliberately ships no
  jurisdiction's rules.
- **Immediate write-offs** (`expensed` — the 少額減価償却資産 special,
  `toku_rei: shoutoku_300k`): book the purchase to the asset account like
  any other asset; `iris asset depreciate` writes the whole cost off in the
  acquisition year. That is what puts the item into the year's depreciation
  figures (`period_dep`), where the 青色申告決算書's depreciation table and
  別表16(7) list it.

### 定率法 — recording the table

Japanese 定率法 depreciates at the 償却率 until the annual charge would fall
below the 償却保証額 (取得価額 × 保証率), then switches to a fixed
改定取得価額 × 改定償却率 for the rest of the useful life. The switch, the
rounding and the order of the two halves are built into the Japan overlay's
`jp.teiritsu` recipe; your AI supplies the inputs and iris does the rest:

1. Look up 償却率 / 保証率 / 改定償却率 for the asset's useful life in 別表第十
   on the NTA site (the 200% table for acquisitions from 2012-04, the 250%
   table for 2007-04〜2012-03 — an asset keeps the table it was acquired under).
2. Run the recipe with those rates, the cost, the life in years and the first
   fiscal year-end month — `iris overlay recipe jp.teiritsu --set cost=1000000
   --set life=8 --set rate=0.250 --set guarantee=0.07909 --set revised=0.334
   --set start=2027-03 --write assets/2026/lathe.md`, or the `jp_teiritsu` tool
   over MCP. It writes the table under `schedule:` and its provenance under
   `schedule_source:`.

The result looks like this on an 8-year ¥1,000,000 asset (償却率 0.250,
保証率 0.07909, 改定償却率 0.334), with a March fiscal year end:

```yaml
method: declining_balance
useful_life_months: 96
schedule:
  - period: 2027-03
    amount: 250000     # 償却率 years
  - period: 2028-03
    amount: 187500
  - period: 2029-03
    amount: 140625
  - period: 2030-03
    amount: 105468
  - period: 2031-03
    amount: 79101      # still above the 償却保証額 79,090
  - period: 2032-03
    amount: 79260      # switched: 改定取得価額 237,306 × 0.334
  - period: 2033-03
    amount: 79260
  - period: 2034-03
    amount: 78785      # ends on the 備忘価額 1 円
schedule_source:       # written by the recipe: the inputs, for replay and for your 税理士
  overlay: jp@2026.09.1
  recipe: jp.teiritsu
  bindings: 1
  params: {cost: 1000000, life: 8, rate: 0.250, guarantee: 0.07909, revised: 0.334, start: 2027-03, salvage: 1}
```

iris checks the rows add up to 取得価額 − 備忘価額 and are otherwise
well-formed, and — because the inputs are on the file — **replays the recipe**
on every `iris validate` and refuses the file if the rows differ. A switch that
landed in the wrong year is caught, not just a wrong total. The rates stay
visible for your 税理士 to check against 別表第十.

Then run depreciation:

```bash
iris asset schedule --year 2026        # each asset's depreciation plan
iris asset depreciate --year 2026      # annual: one FY-total entry per asset at year end
iris asset depreciate --month 2026-05  # monthly: that month's entries
iris export assets --year 2026         # per-asset schedule as CSV
```

Most sole proprietors and small companies book depreciation once a year as a
決算整理 entry — that's `--year`, which writes one FY-total proposal per asset
dated the fiscal year's last day (mid-year acquisitions are prorated by month,
月割, automatically). Use `--month` instead if you close your books monthly.
Pick one cadence per fiscal year — the command refuses to mix the two, since
that would double-count. Either way, `iris asset depreciate` writes proposed
entries you review and post like any other journal.

For the filings themselves — 固定資産台帳, the fixed-asset tax return
(償却資産税, per municipality), 別表16 — your AI works from the asset files
plus the engine's fiscal-year figures (`iris export assets --year` /
`iris asset schedule --year`) and this year's official form spec (the NTA's
or your municipality's published layout), and writes the result under
`compiled/jp/<form>/` in the book. Forms change yearly, so the AI
fetches the current spec rather than following a frozen instruction sheet.

## Year-end close

A book covers one fiscal year. Closing it has an accounting half and a
compliance half, run in the book of the year you're closing:

```bash
iris yearend                                      # start the FY2026 book, with its 期首残高 (opening balances)
# …決算整理 and the return happen here, in the FY2025 book…
iris yearend                                      # after late corrections: refresh FY2026's opening balances
iris api seal --period 2025 --preview <book-id>   # see exactly what will be sealed (cloud)
iris api seal --period 2025 <book-id>             # seal it (cloud)
```

- **Next year's book (`iris yearend`).** Creates the FY2026 book beside this
  one as a copy — your settings, chart of accounts, guides and notes, and the
  fixed assets you still hold — with a 期首残高 (opening balance) entry
  computed from this year's closing balances, so the new year starts
  reconciled and self-contained. Entries you already recorded in 2026 move
  across. For a cloud book, the new book's cloud copy is created in the same
  step (the same people keep access, and your inbound email address moves to
  it) and both books are synced. You can run it as soon as the new year
  starts: 決算整理 and the return still happen in the old book, and each
  re-run refreshes the new book's opening balances. See
  [iris yearend](cli-reference.md#iris-yearend).
- **Seal.** Marks the fiscal year as closed — by whom and when — and **locks**
  its dated journals and `config/`, `assets/`, `filings/`, `compiled/`. The
  server rejects changes to that scope until reopening. `raw/` and `notes/`
  remain writable. Its entries display as `closed`.
- **Nothing is removed.** Sealing and reopening never delete a file: the
  year's files stay in your working tree and on the server, with every
  earlier version.

Before previewing or closing, recorded filings must replay successfully against
the cloud's current posted journals and recipe sources. A stale filing after a
correction, or an unavailable recipe source, can block even the preview before
it lists drafts. Re-run the filing recipe with the intended inputs, run
`iris validate`, sync the filing and its inputs, and preview again. If the
cloud still reports an unavailable replay projection after a successful sync,
seek support from the [Discord community](https://discord.gg/wZDsv9gyb9); repeated close attempts will not repair it.

Need to amend a sealed year? In its book, reopen it, edit, re-sync, and
re-seal:

```bash
iris reopen 2025      # unlock the seal; the year's files are already in the working tree
# …make corrections…
iris sync             # push; the server flags these as post-seal edits
iris yearend          # refresh the FY2026 book's opening balances (while 2026 is still open)
iris api seal --period 2025 <book-id>   # close the year again (supersedes the old seal)
```

If the *next* year is already sealed too, `iris yearend` leaves its opening
entry frozen as filed and tells you so — book the difference as a
current-period correction (前期損益修正) in the new book, or reopen that year
as well.

The seal / reopen half also lives in the web app: the
book's **Year-end** screen lists the book's fiscal year with its close state
and runs the same preview → close → reopen flow — see
[Using the web app](web-app.md#year-end). Only starting the next year's book
(`iris yearend`) is CLI-only, since it creates a folder on your computer.

### Audit handoff

What an auditor, a 税理士 or a tax office asks for is already in the book:

- **The books.** The book folder itself (plain markdown and YAML), or a
  fiscal year as CSVs with `iris export --year 2025` (from the cloud copy:
  `iris api export --year 2025 <book-id>`).
- **The correction/deletion record**, as a file:

  ```bash
  iris api history --all --json <book-id> > history-2025.json
  ```

  The book is the year, so it lists every change to that year's records —
  what changed, who changed it and when — including corrections made after
  the year was closed
  (marked `post_seal_period`). See
  [iris api history](cli-reference.md#iris-api-balance-holdings-history).
- **Access.** Or invite your 税理士 into the book, where the history is
  visible entry by entry — see
  [Collaboration and roles](web-app.md#collaboration-and-roles).

## Quick compliance checklist

- [ ] `config/book.yaml` has the right `region: JP`, `entity_kind`, and
      `fiscal_start_month`.
- [ ] If 課税事業者: `consumption_tax` is set and lines are classified; `iris
      validate` is clean.
- [ ] Fixed assets are described in `assets/` with correct `useful_life_months`.
- [ ] (Optional) If you want 優良電子帳簿 treatment: the book is on cloud
      sync (for the correction/deletion history) and you have filed the
      advance notification (届出) with your tax office. Keep the book on the
      service for the retention period — deleting the book ends 優良
      eligibility (keep a copy of the book and its
      `iris api history --all --json` first if you must).
- [ ] At year-end: `iris yearend` to start next year's book; once the return
      is filed, seal the year in the old book.

See also: [Core concepts](concepts.md) ·
[CLI command reference](cli-reference.md) · [Troubleshooting](troubleshooting.md).
