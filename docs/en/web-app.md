# Using the web app

The web app is the graphical interface to IrisBooks, available on any paid
plan. It's the primary surface for accountants and a comfortable second lens
for owners who'd rather click than type. It works against the cloud copy of
your book, so it needs you to be signed in and online.

## Signing in

Accounts are email + password. From the sign-in screen you can:

- **Log in** with your email and password.
- **Sign up** (when open) — submit your email and password, then confirm with
  the verification code emailed to you.
- **Reset a password** via "Forgot password" — request a code, then set a new
  password.

If your accountant invited you to a book, sign up (or log in) with the exact
email they invited, and the book is already there.

There's also a **CLI authorization** page: when you run `iris api login`, the
browser opens here to authorize the command-line tool. Confirm it's your email
and the expected tool, then approve.

## Layout

The left sidebar has two zones:

- **Across all books** — Dashboard, My Books (shown when you have 2+), Net
  Worth. These don't depend on which book is active.
- **Current book** — a book switcher, then Journals, Activity, Reports
  (General Ledger / Trial Balance / P&L / Balance Sheet), and a Manage group
  (Accounts, Raw documents, Notes, Settings).

Switch the active book from the switcher at the top of the "Current book"
zone; each book gets its own accent color so you always know where you are.

## Dashboard

The home screen. With one book it shows that book's headline numbers —
revenue, expenses, net income, a P&L flow chart and balance-sheet treemap, and
a banner if any entries are still incomplete. With two or more books it adds a
cross-book view: a net-worth tile, an action queue (what needs attention
across books), a consolidated P&L, and your top movers.

## Journals

**Journals** is your transaction list. From here you:

- **Filter and search** — by date range, counterparty/payee, free text,
  status (posted / draft / closed / …), and amount
  (equals / greater / less).
- **Export** the filtered list to CSV.
- **Open an entry** to see its full detail: date, counterparty, status, tags,
  attached source documents (click through to the document), the line-item
  table with debits/credits and totals, and the narrative body.
- **Create a new entry** with the **New journal** button — fill in date,
  payee, lines, tags, and attachments, then save.
- **Edit or delete** an existing entry inline. Deleting is soft: the entry
  moves to the **Deleted** view, where it can be restored.
- **Post draft entries** — the detail page has a one-click **Post** button
  for draft entries (it activates once debits and credits
  balance). To post several at once — say, a batch of drafts captured
  through the [remote connector](remote-connector.md) — tick their
  checkboxes in the list and use **Post selected**.

### History and the "after seal" warning

Every journal detail page has a **History** panel: the full audit trail of
that file — each put / delete / move, who did it, when, the source, and the
reason. If an entry was changed *while its fiscal year was reopened after a
seal*, a clear **"after seal"** badge appears. This is the per-entry view of
the durable correction/deletion record.

An entry whose date falls in a **sealed** fiscal year displays as `closed`
(in the list, the Closed filter, and the detail page) and cannot be edited,
deleted, or posted — the year has to be reopened first (`iris reopen`).

The **Deleted** view (from the Journals list) lists soft-deleted entries with
who deleted them and when — deletions are recorded, not erased. Each row has
a **Restore** action that brings the entry back into the Journals list.

## Reports

Four reports, each with date/as-of filters, a "hide zero-balance rows" toggle,
and CSV export:

- **General Ledger** — pick an account and see its full ledger for the period,
  with an optional opening balance.
- **Trial Balance** — balances as of a date; warns if debits ≠ credits.
- **P&L** — revenue and expenses with subtotals and net income for a period.
- **Balance Sheet** — assets, liabilities, and equity as of a date.

Reports show only **posted** entries. A "freshness" note tells you when the
underlying figures were last computed, and an "incompletes" banner warns when
draft entries exist that aren't counted yet.

## Accounts

The **Accounts** page shows your chart of accounts grouped by type (asset /
liability / equity / income / expense). Click any account to open its ledger
for the current fiscal year (or a custom range), with opening balance when a
date filter is applied.

## Raw documents

The **Raw documents** browser is a two-pane view of everything under `raw/`.
Select a file and it renders inline — images, PDFs, parsed CSV tables, or text.
The **Cited by** panel shows which journals reference the document, so you can
jump from a receipt straight to the entry that booked it. This reverse
drill-down is part of Japan's 帳簿間相互関連性 (cross-reference) requirement.

## Notes

The **Notes** browser is a read-only Markdown viewer for everything under
`notes/` — your working notes, decisions, todos, and the AI's parse caches. A
parse cache can link back to its source document in the Raw browser.

## Activity

The **Activity** timeline is the book-wide audit log: every file operation
(put / delete / move) across the whole book, filterable by actor, path, and
operation. Each row can expand to show a content **diff**, and — if a prior
version exists — a **Recover** button. Post-seal changes are badged. This is
the book-level view of the durable history.

## Settings — language, collaboration, and tokens

The **Settings** page holds:

- **Language** — switch the interface between English and 日本語.
- **Active book** info — its ID and fiscal year.
- **Posting approval** (book owners only) — when on, posting an entry — and
  editing, deleting, or demoting an already-posted entry — can only be done
  here in the web app. Your AI assistant and the CLI keep preparing and
  editing drafts, but their attempts to touch posted entries are refused
  (`APPROVAL_REQUIRED`). Turn it on when you want every entry to pass
  through your own hands before it counts. Only the owner can change it,
  and only from this page — deliberately not from the CLI or a token, so
  an AI assistant can never lift its own gate.
- **Inbound email** — the book's receiving address, the allowed-senders
  list, and quarantined mail with an "Allow sender" shortcut. See
  [Receipts by email](email-inbox.md).
- **Grants** (book owners only) — manage who can access the book and at what
  role; invite new members by email. See below.
- **Personal Access Tokens** — create tokens for the CLI and integrations.
- **Connect your AI** — the remote connector URL and setup steps. See
  [Your AI on the go](remote-connector.md).
- **Connected apps** — the AI apps connected through the remote connector,
  with a **Disconnect** button to revoke one's access.
- **Danger zone** (book owners only) — delete the book from the cloud. See
  below.

### Deleting a book

A book's **owner** can delete its cloud copy from Settings → **Danger zone**.
Deletion is deliberately a web-only ceremony: it requires your browser
session and typing the book's exact name — no CLI command, token, or AI
assistant can do it, whatever its access level.

What deletion means:

- The book disappears **immediately for every member** — from the web app,
  the CLI, and connected AI apps.
- For **30 days** the server keeps the data invisible in case of a mistake
  (contact support to restore within the window). After that, everything on
  the server — journals, files, and the correction/deletion history — is
  **permanently destroyed**. If the book has sealed fiscal years, the dialog
  warns you: deleting destroys those closed-period records and their audit
  trail, so export anything you must keep first.
- **Local copies are never touched.** A clone on your computer keeps all its
  files; `iris sync` there reports that the book was deleted and explains
  how to keep working locally or connect to a new cloud book.
- Email sent to the book's receiving address is dropped, and pending upload
  links stop working.

### Collaboration and roles

A book owner grants others access by **role**:

| Role | Can do |
| --- | --- |
| **Owner** | Everything, including managing members and roles. |
| **Bookkeeper** | Create and edit entries. |
| **Reviewer** | Read-only review. |

Invite someone by email from the Grants section; change or revoke a role
anytime. (Owners can also manage grants from the CLI — see
[`iris api grants`](cli-reference.md#iris-api-grants).)

This is how an **owner and an accountant** share a book: the owner invites the
accountant (or vice versa, on the accountant's plan), and both work against the
same cloud book — the owner often via CLI + AI, the accountant via the web app.

### Personal Access Tokens (PATs)

A PAT is a long-lived credential for scripts and the CLI, scoped by role
(**viewer / bookkeeper / full**). Create one in Settings, copy it **once** (it
won't be shown again), and use it as `IRIS_API_TOKEN`. A token expires after
90 days unused — each use renews it, up to one year from creation. Tokens show
their last-used time and expiry, and you can revoke any token immediately — here in
Settings, or from the CLI with `iris api token list` / `iris api token revoke`
(Full-access PATs can revoke tokens too; creating one stays web-only).
Accountants use PATs to run `iris api …` across many client books from scripts.

## Net Worth

**Net Worth** (a paid feature) values your holdings across books — cash, plus
non-currency units like foreign currency, crypto, or metals — and shows a
total, the change versus last month, a trend line, the biggest movers, and a
composition breakdown. The **Settings** tab there lets you choose which books
count toward the consolidated total. It's a best-effort "how am I doing"
number, not an audited figure; units without a recorded price are listed so you
know what's missing.

## For accountants — the daily shape

If you manage many client books:

- **My Books** is your client directory — each book with its draft count,
  fiscal-year status, and last activity, so you can see at a glance which
  clients need attention today.
- Switch into a client book to review and approve entries, check the
  **Activity** log for what staff did, and run reports.
- Use **PATs** + `iris api …` to script repetitive work across books.
- At year-end, seal each client's fiscal year and produce an auditor bundle —
  see [Japan tax & compliance](japan-tax-and-compliance.md).

Client books stay fully separate — there's no cross-client aggregation, which
is the right default for confidentiality.

Next: [Japan tax & compliance](japan-tax-and-compliance.md).
