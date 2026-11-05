# Records, history and year-end

This page covers how a book's records stay checkable after the fact —
correction history, search and traceability — how returns are prepared from
the book, and how a year is closed and handed over.

## History, search and traceability

Four features keep a book's records checkable after the fact — by you, your
accountant, or an auditor:

| Feature | What it does | Where |
| --- | --- | --- |
| **Correction/deletion history** | The server records every change to every file, deletions included — who changed it, when, and what it was before | `iris api history`; the web app **Activity** timeline and per-journal **History** panel (cloud) |
| **Search** | Find journals by date, amount, and counterparty, in any combination — and by status, account, or tag | `iris search`; the filters on the web app **Journals** page |
| **Ledger ↔ journal** | Every ledger row names the journal file it came from | `iris report ledger`; the web app **Accounts** ledger |
| **Journal ↔ source document** | Every journal cites its receipts, invoices, and statements, and you can walk that link both ways | `iris references <path>`; the **Cited by** panel in the web app's Raw documents browser |

The ledger link comes from the design rather than from a separate feature.
The journal files are the only source: the general ledger, trial balance, and
statements are computed from them on demand. Nothing is copied into a second
book, so the two can never drift apart.

Search and both kinds of traceability work fully offline. The correction
history is kept by the server, so it exists only for a book synced to the
cloud. A **local-only book has no server-side correction history**, and local
git history doesn't stand in for one: it lives on your own machine and can be
rewritten, so it is not an independent record.

Deleting a book ends its server record too: after a 30-day window, all of the
book's server data — including the correction history — is permanently
destroyed. As with paper books, keeping your books for the retention period
your tax law sets is your duty. Before deleting a book, keep your own copy of
the book folder and of its record from `iris api history --all --json`
(see [Audit handoff](#audit-handoff)).

> **Seals** (closing a year) lock the period — writes into a sealed year are
> refused for journals and accounting dependencies until reopening; changes
> to that scope made while reopened are flagged
> in that history. See [Year-end close](#year-end-close).

> **Not certified.** IrisBooks holds no third-party certification and does not
> claim that a book kept in it meets any jurisdiction's electronic-bookkeeping
> standard. Whether your books qualify, and any notice to your tax authority,
> is for you and your accountant to determine.

## Returns and regional rules

The engine handles the universal, stable parts: double-entry math, the fields
recorded on each line, totals and data exports. Regional rules — tax
classifications, depreciation methods, the figures a return needs — come only
from the [overlays](https://irisbooks.io/docs/en/overlays/) your book selects. Each region has a guide there:
which packages to select, and what they leave to you.

A figures recipe records its result under `filings/` with its provenance, and
`iris validate` re-runs it, so a correction posted after you filed shows up as
an error until the recipe is re-run. The forms themselves change yearly and
vary by place, so your AI prepares them from the engine's figures, the
recorded filings and the current official form, and keeps them in the book
under `compiled/<region>/<form>/`. IrisBooks sums; your AI files.

## Year-end close

A book covers one fiscal year. Closing it has an accounting half and a
compliance half, run in the book of the year you're closing:

```bash
iris yearend                                      # start the FY2026 book, with its opening balances
# …closing adjustments and the return happen here, in the FY2025 book…
iris yearend                                      # after late corrections: refresh FY2026's opening balances
iris seal --dry-run 2025                          # see exactly what will be sealed (cloud)
iris seal 2025                                    # seal it (cloud)
```

- **Next year's book (`iris yearend`).** Creates the FY2026 book beside this
  one as a copy — your settings, chart of accounts, guides and notes, and the
  fixed assets you still hold — with an opening-balance entry computed from
  this year's closing balances, so the new year starts reconciled and
  self-contained. Entries you already recorded in 2026 move across. For a
  cloud book, the new book's cloud copy is created in the same step (the same
  people keep access, and your inbound email address moves to it) and both
  books are synced. You can run it as soon as the new year starts: closing
  adjustments and the return still happen in the old book, and each re-run
  refreshes the new book's opening balances. See
  [iris yearend](cli-reference.md#iris-yearend).
- **Seal.** Marks the fiscal year as closed — by whom and when — and **locks**
  its dated journals and `config/`, `assets/`, `filings/`, `compiled/`. The
  server rejects changes to that scope until reopening. `raw/` and `notes/`
  remain writable. Its entries display as `closed`.
- **Nothing is removed.** Sealing and reopening never delete a file: the
  year's files stay in your working tree and on the server, with every
  earlier version.

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

Need to amend a sealed year? In its book, reopen it, edit, re-sync, and
re-seal:

```bash
iris reopen 2025      # unlock the seal; the year's files are already in the working tree
# …make corrections…
iris sync             # push; the server flags these as post-seal edits
iris yearend          # refresh the FY2026 book's opening balances (while 2026 is still open)
iris seal 2025        # close the year again (supersedes the old seal)
```

If the *next* year is already sealed too, `iris yearend` leaves its opening
entry frozen as filed and tells you so — book the difference as a
current-period correction (a prior-period adjustment) in the new book, or
reopen that year as well.

The seal / reopen half also lives in the web app: the
book's **Year-end** screen lists the book's fiscal year with its close state
and runs the same preview → close → reopen flow — see
[Using the web app](web-app.md#year-end). Only starting the next year's book
(`iris yearend`) is CLI-only, since it creates a folder on your computer.

### Audit handoff

What an auditor, an accountant or a tax authority asks for is already in the
book:

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
- **Access.** Or invite your accountant into the book, where the history is
  visible entry by entry — see
  [Collaboration and roles](web-app.md#collaboration-and-roles).

See also: [Core concepts](concepts.md) ·
[CLI command reference](cli-reference.md) · [Troubleshooting](troubleshooting.md).
