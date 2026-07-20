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
| **帳簿間の相互関連性の確保** | Books cross-reference their source documents | `iris show`, and the **Cited by** panel in the web app's Raw documents browser |
| **検索機能の確保** | Search by date, amount, and counterparty (combinable) | `iris search`, and the filters on the web app **Journals** page |

Two of the three — **search** and **cross-references** — work for free and
offline (`iris search`, `iris show`). The third — the **correction/deletion
history** — has to be trustworthy to an auditor, which only the server-side
record provides. That's why it's a paid capability: local git history is *not*
auditor-trustable.

> **Scope of the 優良 claim.** All three capabilities must hold *together*,
> so 優良電子帳簿 applies only to a book kept on a paid plan with cloud sync.
> A **free, local-only book is not covered**: search and cross-references
> still work, but there is no auditor-trustable correction/deletion history.
> The claim also holds only **while the book stays on the service**. If you
> **delete a book** (after a 30-day window, all server data is permanently
> destroyed — including the correction history and sealed archives) or you
> **end your subscription**, the durable history is gone and the book no
> longer qualifies. As with paper books, the legal duty to preserve your
> books — including that history — for the statutory retention period
> (7 years, up to 10 in some corporate cases) is yours. Before deleting a
> book or cancelling, export what you must keep:
> `iris api export audit` (see [Audit handoff](#audit-handoff)).

> **Seals** (closing a year) lock the period — writes into a sealed year are
> refused until it is reopened, and every edit made while reopened is flagged
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
Your AI takes these buckets and applies the current year's form math — the
division of labor stays: **IrisBooks sums, your AI files.** Note the 課税期間
is the calendar year for individuals, your fiscal year for a 法人 (`--year`).

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
- **Methods**: `straight_line` (定額法), `declining_balance` (定率法, with a
  `declining_rate`), or `expensed` (immediate write-off).

Then run depreciation:

```bash
iris asset schedule                    # each asset's depreciation plan
iris asset depreciate --year 2026      # annual: one FY-total entry per asset at year end
iris asset depreciate --month 2026-05  # monthly: that month's entries
iris export assets                     # per-asset schedule as CSV
```

Most sole proprietors and small companies book depreciation once a year as a
決算整理 entry — that's `--year`, which writes one FY-total proposal per asset
dated the fiscal year's last day (mid-year acquisitions are prorated by month,
月割, automatically). Use `--month` instead if you close your books monthly.
Pick one cadence per fiscal year — the command refuses to mix the two, since
that would double-count. Either way, `iris asset depreciate` writes proposed
entries you review and post like any other journal.

> **Known limitation.** `declining_balance` does not yet implement the JP
> two-phase switch to 改定償却率 when book value falls below the 保証額. For
> assets that reach that point, your AI computes the switch and records a
> correcting entry. This is documented so it isn't a surprise at filing time.

For the filings themselves — 固定資産台帳, the fixed-asset tax return
(償却資産税, per municipality), 別表16 — your AI works from the asset files
plus the engine's fiscal-year figures (`iris export assets --year` /
`iris asset schedule --year`) and this year's official form spec (the NTA's
or your municipality's published layout), and writes the result under
`compiled/jp/<form>/<year>/` in the book. Forms change yearly, so the AI
fetches the current spec rather than following a frozen instruction sheet.

## Year-end close

Closing a fiscal year has an accounting half and a compliance half:

```bash
iris yearend 2025                                 # write FY2026's 期首残高 (opening balances)
iris sync                                         # push the entry
iris api seal --period 2025 --preview <book-id>   # see exactly what will be sealed (paid)
iris api seal --period 2025 <book-id>             # seal it (paid)
iris api archive download --year 2025 <book-id>   # download the sealed archive zip
```

- **Carry forward (`iris yearend`).** Writes the next year's 期首残高
  (opening balance) entry from the closing balances, so the new year starts
  reconciled and self-contained. Works offline and on the free tier — it's an
  ordinary journal in your book. See
  [iris yearend](cli-reference.md#iris-yearend).
- **Seal.** Marks the fiscal year as closed — by whom and when — and **locks**
  it: every write into the sealed year is refused, on every surface (the CLI,
  sync, the web app, the remote connector). Its entries display as `closed`.
- **Archive.** A snapshot of the sealed year (zip + queryable SQLite) is built
  server-side for download and audit handoff. Your working tree is untouched
  — the year's files stay exactly where they are.

Need to amend a sealed year? Reopen it, edit, re-sync, and re-seal:

```bash
iris reopen 2025      # unlock the seal; the year's files are already in the working tree
# …make corrections…
iris sync             # push; the server flags these as post-seal edits
iris yearend 2025     # refresh next year's opening balances (while 2026 is still open)
iris api seal --period 2025 <book-id>   # close the year again (supersedes the old seal)
```

If the *next* year is already sealed too, `iris yearend` leaves its opening
entry frozen as filed and tells you so — book the difference as a
current-period correction (前期損益修正), or reopen that year as well.

### Audit handoff

To give an auditor or 税理士 a self-contained package:

```bash
iris api export audit <book-id>
```

This bundles a per-fiscal-year snapshot (queryable SQLite), Excel-friendly CSV
views, and the event log — the complete correction/deletion timeline, including
any post-close edits.

## Quick compliance checklist

- [ ] `config/book.yaml` has the right `region: JP`, `entity_kind`, and
      `fiscal_start_month`.
- [ ] If 課税事業者: `consumption_tax` is set and lines are classified; `iris
      validate` is clean.
- [ ] Fixed assets are described in `assets/` with correct `useful_life_months`.
- [ ] (Optional) If you want 優良電子帳簿 treatment: you're on a paid plan
      (for the correction/deletion history) and have filed the advance
      notification (届出) with your tax office. Keep the book on the service
      for the retention period — deleting the book or unsubscribing ends
      優良 eligibility (run `iris api export audit` first if you must).
- [ ] At year-end: seal, download the archive, and (for handoff)
      `iris api export audit`.

See also: [Core concepts](concepts.md) ·
[CLI command reference](cli-reference.md) · [Troubleshooting](troubleshooting.md).
