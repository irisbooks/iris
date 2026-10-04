# Using the web app

The web app is the graphical interface to IrisBooks, available to any
signed-in account. It's the primary surface for accountants and a comfortable second lens
for owners who'd rather click than type. It works against the cloud copy of
your book, so it needs you to be signed in and online.

## Signing in

Accounts are email + password. From the sign-in screen you can:

- **Log in** with your email and password.
- **Sign up** (when open) — submit your email and password, then confirm with
  the verification code emailed to you.
- **Reset a password** via "Forgot password" — request a code, then set a new
  password.

These screens have a language switch in the top-right corner (labeled
"日本語" / "English") in case your browser's language was guessed wrong.
The emails behind these flows (verification codes, reset codes, invitations)
arrive in the app's language — the switch here, your browser on first
visit, or whatever you chose later in Settings → Language.

If your accountant invited you to a book, sign up (or log in) with the exact
email they invited, and the book is already there.

There's also a **CLI authorization** page: when you run `iris api login`, the
browser opens here to authorize the command-line tool. Confirm it's your email
and the expected tool, then approve.

## Layout

The top bar carries your location:

- **Dashboard** — the one always-visible tab, for the screens that span
  your whole account.
- **The book plate** — the current book's name and fiscal year, side by
  side with the book's color dot. Click the name to switch books (each book
  is listed with its year — two years of one business share a name), open
  **My Books**, or create a new book. Inside a book, the year links to the
  book's **Year-end** screen.

Whichever of the two is your current place is gently recessed into the
bar — carved in, like a nameplate. Inside a book the plate is carved and
tinted with the book's color; on screens outside a book it sits flat and
dimmed (Dashboard is carved instead) — clicking the book's name takes you
back inside.

Inside a book, the left sidebar lists that book's screens: Journals and
Activity, a Reports group (General Ledger / Trial Balance / P&L / Balance
Sheet — all four always visible), and a Manage group (Accounts, Raw
documents, Notes, Year-end, Settings). Outside a book there is no sidebar —
the Dashboard and its related screens use the full width. On a phone, the
book plate sits on its own row under the top bar, with the menu button for
the book's screens at its right edge.

Your **avatar** (top right) opens the account menu from anywhere: your
**Settings** (see below), a language switch, and log out. The language
item is always labeled in the *other* language ("日本語" / "English"),
so if the interface ever ends up in a language you can't read, the way
back stays readable. Everything else — including the color theme —
lives in Settings.

Each book gets its own accent color — the plate and the sidebar rail wear
it — so you always know where you are. **Net Worth** opens from its card on
the Dashboard, and **My Books** from the book plate's menu; both have a
"‹ Dashboard" link to step back.

## Dashboard

The home screen. With one book it shows that book's headline numbers —
revenue, expenses, net income, a P&L flow chart and balance-sheet treemap, and
a banner if any entries are still incomplete. The net-worth tile also appears
with one book. With two or more books it adds an action queue (what needs
attention across books), a consolidated P&L, and your top movers.

If your books don't all use the same currency, set a base currency
(`iris api config set --base-currency JPY`). The consolidated P&L then shows
**Conversion rates** — one row per other currency, with the rate it used and
the date you recorded it. Each rate is editable: type a different one and the
total recalculates immediately. That edit changes the view only and is not
saved; to keep a rate, record it with `iris price add --unit USD --price 155`,
the same price store Net Worth values your holdings from.

A currency with no recorded rate shows an empty box, and books in that
currency are listed separately rather than folded into the total — a missing
rate stays visible instead of quietly changing the number.

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
deleted, or posted — the year has to be reopened first (from the
[**Year-end**](#year-end) screen, or `iris reopen`).

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

Reports open on the book's fiscal year (`fiscal_year` in `config/book.yaml`),
from its first day to today, clamped to the year's first or last day when
today is outside that year. The **Journals** list opens on the whole book year,
so entries dated later in the year remain visible. Change the dates to see
another period.

Reports show only **posted** entries. A "freshness" note tells you when the
underlying figures were last computed, and an "incompletes" banner warns when
draft entries exist that aren't counted yet.

## Accounts

The **Accounts** page shows your chart of accounts grouped by type (asset /
liability / equity / income / expense). Click any account to open its ledger
for the fiscal year you are working in, up to today (or a custom range), with
opening balance when a date filter is applied.

## Raw documents

The **Raw documents** browser is a two-pane view of everything under `raw/`.
Select a file and it renders inline — images, PDFs, parsed CSV tables, or text.
The **Cited by** panel shows which journals reference the document, so you can
jump from a receipt straight to the entry that booked it. This reverse
drill-down is the book's journal ↔ evidence audit trail: an auditor can walk
from any receipt to the entries that booked it, and back.

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

## Year-end

The **Year-end** screen shows the book's fiscal year — how many journal
entries it holds, its close state (**Open** / **Closed** / **Reopened**), and
who closed it, when. It's where a book **owner** runs
the period close:

- **Close a year.** A preview shows which files the close will lock and
  lists any remaining drafts. A year cannot close while
  drafts remain — post, delete, or redate them first (each listed draft
  links to its entry). Closing locks the year’s journals and accounting dependencies
  (`config/`, `assets/`, `filings/`, `compiled/`) until reopening; `raw/` and
  `notes/` remain writable.
- **Reopen a year.** Unlocks it for amendments. Every change to the locked scope made while
  reopened is permanently flagged "after seal" in the audit trail, and
  the screen counts the files amended. Close the year again when you're
  done — the **History** panel keeps every close and reopen on record.

Before previewing or closing, recorded filings must replay successfully against
the cloud's current posted journals and recipe sources. A stale filing after a
correction, or an unavailable recipe source, can block even the preview before
it lists drafts. Re-run the filing recipe with the intended inputs, run
`iris validate`, sync the filing and its inputs, and preview again. If the
cloud still reports an unavailable replay projection after a successful sync,
seek support from the [Discord community](https://discord.gg/wZDsv9gyb9); repeated close attempts will not repair it.

Closing never removes anything: the year's files stay in the book.

A book covers one fiscal year. The next year starts as a book of its own —
created from the CLI with [`iris yearend`](cli-reference.md#iris-yearend) —
and appears in **My Books** beside this one, with the same people's access.

The same flow works from the CLI (`iris api seal`, `iris reopen`) — see
[Japan tax & compliance](japan-tax-and-compliance.md). Members who aren't
the owner see the same year list read-only.

## Settings — your settings and book settings

Settings are split by what they affect, and everything is reachable from
one door: your **avatar menu (top right) → Settings**.

**Your settings** (avatar menu → Settings — available everywhere, even
outside any book) hold what belongs to you, not to a book:

- **Language** — switch the interface between English and 日本語.
- **Appearance** — light, dark, or follow the system.
- **Books** — every book you're a member of, with your role; each row opens
  that book's own settings page.
- **Personal Access Tokens** — create tokens for the CLI and integrations.
- **Connect your AI** — the remote connector URL and setup steps. See
  [Your AI on the go](remote-connector.md).
- **Connected apps** — the AI apps connected through the remote connector,
  with a **Disconnect** button to revoke one's access.

**Book settings** (sidebar → Settings, inside the book — or one click from
the Books list above) hold what belongs to that book:

- The book's **ID and fiscal year**.
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
- **Danger zone** (book owners only) — delete the book from the cloud. See
  below.

### Deleting a book

A book's **owner** can delete its cloud copy from the book's Settings →
**Danger zone**.
Deletion is deliberately a web-only ceremony: it requires your browser
session and typing the book's exact name — no CLI command, token, or AI
assistant can do it, whatever its access level.

What deletion means:

- The book disappears **immediately for every member** — from the web app,
  the CLI, and connected AI apps.
- For **30 days** the server keeps the data invisible in case of a mistake
  (seek support from the [Discord community](https://discord.gg/wZDsv9gyb9) to restore within the window). After that, everything on
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
accountant (or the accountant invites the owner), and both work against the
same cloud book — the owner often via CLI + AI, the accountant via the web app.

### Personal Access Tokens (PATs)

A PAT is a long-lived credential for scripts and the CLI, scoped by role
(**viewer / bookkeeper / full**). Create one in your settings (avatar menu →
Settings), copy it **once** (it
won't be shown again), and use it as `IRIS_API_TOKEN`. A token expires after
90 days unused — each use renews it, up to one year from creation. Tokens show
their last-used time and expiry, and you can revoke any token immediately — here in
Settings, or from the CLI with `iris api token list` / `iris api token revoke`
(Full-access PATs can revoke tokens too; creating one stays web-only).
Accountants use PATs to run `iris api …` across many client books from scripts.

## Net Worth

**Net Worth** adds up what your books own minus what they owe — cash,
receivables, fixed assets and loans at the value recorded in the books, and
foreign currency, crypto, shares or metals at the prices you recorded — and
shows a total, the change versus last month, a trend line, the biggest movers,
and a composition breakdown. Accounts marked `owner: true` in the chart (事業主貸,
事業主借) are left out: they are your own money, not the business's. The
**Settings** tab there lets you choose which books count toward the
consolidated total.

A book counts for the months of its own fiscal year, so the trend line runs
from one year's book into the next without counting anything twice. Once a
book's year has ended, it stops counting until next year's book exists — Net
Worth lists it as *year ended* until you run
[`iris yearend`](cli-reference.md#iris-yearend).

It's a best-effort "how am I doing" number, not an audited figure. A unit
without a recorded price counts at its book value and is listed so you know
what to price. IrisBooks fetches no prices on your behalf — exchange rates
included — so record them yourself with `iris price add`.

## For accountants — the daily shape

If you manage many client books:

- **My Books** is your client directory — each book (one per client per
  fiscal year) with its year, draft count, last activity, and a **Year-end**
  column showing that year's close state: closed, reopened, **ready to
  close**, or "N drafts" still blocking it. At year-end this column is your
  worklist — each badge links straight into that book's Year-end screen.
- Switch into a client book to review and approve entries, check the
  **Activity** log for what staff did, and run reports.
- Use **PATs** + `iris api …` to script repetitive work across books.
- At year-end, close each client's fiscal year from **Year-end** (or the
  CLI) — see
  [Japan tax & compliance](japan-tax-and-compliance.md).

Each client's files and permissions belong to a separate book. The dashboard's
**Consolidated P&L** includes all books you can access by default, including
client books; use its book picker to choose the totals you want to see.
**Net Worth** defaults to owned books only; invited books require opt-in in
its Settings tab.

Next: [Japan tax & compliance](japan-tax-and-compliance.md).
