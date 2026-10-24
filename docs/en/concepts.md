# Core concepts

A short tour of the ideas that make IrisBooks make sense. Once these click,
both the CLI and the web app feel obvious.

## Files are your books

A **book** is a folder on disk, and its files are the primary accounting
records. You can read them, edit them, diff them, back them up, and hand them
to your accountant with any tool you already use.
The CLI works on those files; the web app works on their synced cloud copy.

One book covers one fiscal year. You can keep separate business and personal
books and combine selected books in cross-book reports. At year-end the next
year's book starts as a copy of this one — see [One book per year](#one-book-per-year).

```text
your-book/
├── config/
│   ├── book.yaml                 # identity, region, fiscal year, currency
│   ├── chart-of-accounts.yaml    # your accounts
│   ├── rules.yaml                # optional categorization hints
│   └── overlays/                 # optional: your book's own region rules
├── raw/                          # source documents (CSVs, PDFs, receipts)
├── journals/YYYY-MM/             # one Markdown file per entry
├── assets/YYYY/                  # fixed assets (for depreciation)
├── filings/                      # recorded return figures
├── notes/                        # working notes, todos, decisions, parse caches
└── compiled/                     # AI-generated reports (regeneratable)
```

The full layout is in the [Book file-format reference](book-format-reference.md).

## Journals — your transactions

Every transaction is one **journal** entry, stored as a Markdown file with a
YAML header at `journals/YYYY-MM/YYYY-MM-DD-<payee>-NN.md` — the folder is
the date's year and month, the first seven characters of the date. It's
double-entry: the debits and the credits must balance.

```markdown
---
date: 2026-05-04
payee: EXAMPLE.COM
status: draft
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

The text below the `---` is free-form: write *why* the transaction happened.
The filename is the entry's permanent identity — it stays put even as the
entry's status changes.

## Accounts — the chart of accounts

Your accounts live in `config/chart-of-accounts.yaml`, each with a
hierarchical path (`資産:普通預金`, `費用:消耗品費`) and a type (asset /
liability / equity / income / expense). Journals reference accounts by path.
The "normal side" of an account (whether debits increase it) is derived from
its type — you don't declare it.

You can give accounts **aliases** so journals can reference them in another
language or a shorter name. Don't invent account paths inside a journal — add
the account to the chart first (or ask your AI to propose it in
`notes/open-questions.md`).

## Status — the lifecycle of an entry

Every journal carries a `status`:

| Status | Meaning |
| --- | --- |
| `draft` | A draft. Being entered or still uncertain. Not on the books yet. |
| `posted` | On the books. **Only posted entries appear in reports.** |

This is the single most important rule to remember: **`iris balance`, the
P&L, and the balance sheet include only `posted` entries.** A `draft` entry
will not show up in your trial balance until someone promotes it. Promote with
[`iris post`](cli-reference.md#iris-post) or by editing the field.

(You'll also see a `closed` status — that's any entry whose date falls in a
sealed fiscal year. It's derived, never stored in the file: the web app,
`iris search`, and the remote connector all display it, and reopening the
year makes the stored status visible again. The web app additionally shows an
`incomplete` marker for drafts that aren't ready.)

## Reports are computed, never stored

IrisBooks never stores a "balance sheet file". Reports are derived from your
posted journals every time you ask:

- **Trial balance** (試算表) — `iris balance` or `iris report tb`
- **Profit & loss** (損益計算書) — `iris report pl`
- **Balance sheet** (貸借対照表) — `iris report bs`
- **General ledger** (元帳) for one account — `iris report ledger --account …`

Because they're computed, they're always consistent with the underlying
entries. The web app renders the same reports graphically and can export each
to CSV.

## Raw documents and cross-references

Anything under `raw/` — bank CSVs, receipt photos, PDF invoices — is the
*evidence* behind your entries. A journal points at its source via an
`attachments` entry, and you can walk that link in both directions:

- From a journal, see which documents it cites.
- From a document, see which journals cite it (`iris references <path>`, or the
  "Cited by" panel in the web app's Raw documents browser).

With it, you, your 税理士 or an auditor can go from any entry to its evidence
and back. For the book's other record-keeping features (correction history,
search), see [Japan tax & compliance](japan-tax-and-compliance.md).

## Region rules — the overlay

The `iris` engine knows double-entry bookkeeping, not any one country's tax
law. Reusable accounting functions live in **Overlays**: versioned rules and
computations (**recipes**) written in YAML and CEL. Each function is selected
independently. Japanese tax classification, tax amount proposals, filing aids,
small-asset deduction checks and declining-balance calculations are separate
Overlays. The public repository holds their sources, guides and examples.

Your book pins published versions in `config/book.yaml` — a Japanese book, for
example:

```yaml
region: JP
overlays:
  - journal-balance@2026.10.1
  - inventory-disposal@2026.10.1
  - jp-tax-classification@2026.10.1
  - jp-tax-amount@2026.10.1
  - jp-tax-filing@2026.10.1
  - jp-small-asset-deduction@2026.10.1
  - jp-declining-balance@2026.10.1
```

This is the new Japanese business preset's candidate selection; signed publication
is pending. Each selected function needs an exact verified copy inside the Book.
You and your AI can change the selection, create Book-specific rules and
contribute improvements to the community.

- **Rules** check your entries through local `iris validate`. The cloud stores
  definitions and results without executing Overlay policy.
- **Recipes** compute region figures — a 定率法 schedule, the 消費税 return —
  and record the result together with its source (the overlay version and the
  inputs), on the asset file or under `filings/`. `iris validate` re-runs the
  recipe, so a figure that no longer follows from its inputs is caught.
- **The pin never moves on its own.** A new version can change what is checked
  or computed, so moving to it takes an explicit `iris overlay upgrade`, when
  you decide. Figures recorded under an older version keep being checked
  against that version.

An omitted or empty selection enables no optional functions. Universal checks
(balanced entries, known accounts, dates and amounts) remain active. Region never
enables an Overlay automatically; upgrades change already selected versions.

The published overlays are open source (Apache-2.0) at
[github.com/irisbooks/overlays](https://github.com/irisbooks/overlays), so you
or your accountant can read the exact rule behind any figure; the tag names
there are the pins. A book can also add rules of its own in `config/overlays/` — see
the [Book file-format reference](book-format-reference.md).

## Sync — the three ways to work

The same book can live in three arrangements. You don't choose a "mode"; you
just use more or fewer of the features:

- **Offline.** Files only, no server, no account. You validate and report
  locally. Maximum privacy, zero network.
- **Files + Cloud.** Your local files plus a cloud mirror (sign in with
  `iris api login`). You edit locally and run `iris sync` to push and pull.
  The web app, multi-device access, collaboration, and timestamped history
  all live on the cloud side.
- **Cloud-only access.** You can view and review the cloud copy without a
  local folder. For bookkeeping work, accountants should also use files plus
  their own AI, with a separate work folder/session for each client.

Sync is **explicit**: nothing uploads until you (or your AI) run `iris sync`,
or `iris post`. Web-app changes are written directly to the cloud.
There is no background watcher silently
shipping your files. An owner and accountant can each sync their own copy of
the same book, then use web for viewing and review.

## One book per year

A book covers one fiscal year, recorded as `fiscal_year` in
`config/book.yaml`. When the year ends,
[`iris yearend`](cli-reference.md#iris-yearend) starts the next year's book
as a **copy**: a new folder beside this one with your settings, chart of
accounts, rules, guides and notes, the fixed assets you still hold, and an
opening-balances entry (期首残高) computed from this year's closing
balances. Entries you already recorded in the new year move across. If the
book is in the cloud, the new book gets its cloud copy in the same step,
with the same people's access and your inbound email address.

Nothing links the two books afterwards. The old one stays as it was: finish
its filing there, then seal it. The new one is where daily work goes. Each
year can change its own chart of accounts and settings without touching the
other, your AI only sees the year it's working in, and a year you no longer
need to keep can be deleted on its own.

## Seals — closing a year, visibly

At year-end you **seal** a fiscal year: the server records who closed it and
when. The lock covers journals dated in that year and the book's `config/`,
`assets/`, `filings/`, and `compiled/` files. `iris post` refuses sealed-year
journals; the server rejects writes in this scope from sync, the web app,
and the remote connector. Entries display as `closed` everywhere.
`raw/` evidence and `notes/` remain writable. Local files can still be edited,
but changes in the locked scope cannot be pushed until you reopen the year.

To amend a sealed year, use [`iris reopen`](cli-reference.md#iris-reopen).
Changes in the locked scope made after reopening are permanently flagged as
**post-seal edits** in the server's audit trail. Changes to `raw/` and `notes/`
have ordinary history, without that flag. When you're done, re-seal; the new
seal supersedes the old one in the audit chain. Sealing never removes files.
See [Year-end close](japan-tax-and-compliance.md#year-end-close).

## The durable history (correction/deletion record)

With cloud sync, the server keeps an append-only log of every change to every
file — who changed it, when, and what it was before. In Japanese this is the
**訂正・削除の履歴** ("record of corrections and deletions"). View it with
`iris api history` or in the web app's **Activity** timeline and per-journal
**History** panel, and export the
book's — its fiscal year's — record as a file with
`iris api history --all --json`.

Local git history is not a substitute: it lives on your own machine and can be
rewritten, so it is not an independent record. That is why the durable history
lives on the server.

## The two lenses, side by side

| | CLI + your AI | Web app |
| --- | --- | --- |
| Main use | Owners and accountants working with AI on files | Viewing, review and cloud administration |
| Edits | Your AI writes files; you review | Forms in the browser |
| Works offline | Yes | No (needs the server) |
| Reports | `iris report …` (text/JSON) | Rendered + CSV export |

They are not either/or — most owners use both: the CLI + AI to enter
data fast, the web app to review, report, and collaborate.

Next: [Bookkeeping with the CLI and your own LLM](cli-and-llm.md) or
[Using the web app](web-app.md).
