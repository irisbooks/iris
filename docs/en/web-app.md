# Using the web app

The web app is the viewing and review surface for owners and accountants:
read reports, review entries, approve where permitted, inspect history and
manage cloud access. For bookkeeping work, accountants should also use
[book files with their own AI](cli-and-llm.md), in a separate workspace for
each client. The web app works against the cloud copy of your book, so it
requires sign-in and an online connection.

## Signing in

Accounts start with email + password. From the sign-in screen you can:

- **Log in** by entering your email and choosing **Continue**. Passkey sign-in
  starts automatically when available. If no passkey is available, enter your
  password.
  If the passkey prompt is cancelled or fails, retry it or choose
  **Use password instead**.
  If it keeps failing, include the displayed **Support reference** when contacting support.
  When authenticator protection is enabled, password login also requires
  its six-digit code.
- **Sign up** (when open) — submit your email and password, then confirm with
  the verification code emailed to you.
- **Reset a password** via "Forgot password" — request a code, then set a new
  password.

These screens have a language switch in the top-right corner (labeled
"日本語" / "English") in case your browser's language was guessed wrong.
The `.io` service currently sends verification codes, reset codes and invitations
using Cognito's default English emails. The app itself supports both languages.

If your accountant invited you to a book, sign up (or log in) with the exact
email they invited, and the book is already there.

There's also a **CLI authorization** page: when you run `iris api login`, the
browser opens here to authorize the command-line tool. Confirm it's your email
and the expected tool, then approve.

For `iris api login --device`, open the printed IrisBooks URL on your own
phone. Sign in, enter the request number, then review your account, permissions
and warning before approving. Approve only a request you intentionally started;
the displayed device name is not verified. Your password, authenticator code
and passkey stay with you; the VM receives its own CLI session after approval.

### Passkeys and authenticator backup

In your avatar menu → Settings → Account security, first set up an
authenticator app. Scan the QR or copy the setup key, then verify a code.
Keep a backup of the authenticator. You can then add a passkey on your own
device, and add another passkey as a spare. Passkey login uses your device's
biometric or PIN verification; it does not require an additional authenticator
code. You can replace the authenticator or remove a passkey in the same card.

Sign in again if asked before changing protection. After a change, existing
browser, CLI, API-token and connector access is revoked; sign in or reconnect
where needed. If finishing the change fails, use the completion retry button.
Existing users choose when to enroll. Password reset does not remove
authenticator protection, and self-service recovery after losing all factors
is not available. Keep a working backup before relying on passkeys.

## When no books appear

The first-run screen explains how to set up a local book with your AI assistant
and the `iris` CLI, then sync it to this account. **Copy message for your AI**
includes this service's setup-guide URL and your signed-in email.
Paste it into your assistant on your computer. **Read the setup guide** opens
the manual if you prefer to follow the steps yourself.

If you already have a local book, open its folder with your assistant and ask
it to connect and sync that book. After sync finishes, choose **Refresh book
list**; a book found there opens in Overview. If you expected a shared book,
check that you signed in with the invited email address. The account menu
remains available for language changes and logging out. The **Settings** gear
and language icon beside it are visible directly in the top bar, including on
phones. You can set up passkeys and an authenticator before syncing a book.

The recommended creation workflow is through your AI and local files.
**Add new book** remains available for explicitly creating a cloud book.

## Layout

The sidebar stays available on both global and book pages:

- **Across books** contains **Dashboard** and **Net Worth**, for portfolio
  reports.
- **My Books** lists each book with its fiscal year. Open a book to enter
  its Overview; when switching from another book, the current section is
  preserved and book-specific filters and resource selections are cleared.
  The arrow expands its sections without changing the current page. One
  book expands at a time, with Overview, Journals, Activity, four report
  links, and management pages for Files, Accounts, Notes, Year-end and
  Book settings.
- **Closed books** groups closed and archived books. A direct link to one
  opens its group and sections automatically.
- **Manage books** opens the full **My Books** directory; **Add new book**
  starts book creation. Both are available with one book as well.

The top bar names the current global page: **Dashboard**, **Net Worth**,
**Manage books**, **Settings**, or **Add new book**. Inside a book, it shows
the book's name and fiscal year; the year links to its **Year-end** screen.
The top bar stays visible as you scroll, with the sidebar or mobile drawer
directly below it.
On a phone, use the top-left menu button for the same navigation.

The top-right **Settings** gear opens account settings, and the **language**
icon switches between English and Japanese. Its tooltip names the language
you will switch to ("日本語" / "English"). Both icons stay visible on global,
book and first-run pages.

Your **avatar** (top right) opens the account menu from anywhere: your
**Settings** (see below), a language switch, and log out. The language
item is always labeled in the *other* language ("日本語" / "English"),
so if the interface ever ends up in a language you can't read, the way
back stays readable. Everything else — including the color theme —
lives in Settings.

Each view has its own URL: `/app/` for Dashboard, `/app/networth` for Net
Worth, `/app/books` for the directory, and `/app/b/<book-id>/...` for book
pages. You can bookmark them or open independent browser tabs. The address
decides which book is shown; a previously visited book does not override
it. Existing report filters and file selections remain in their URLs.

## Dashboard

The portfolio home screen shows net worth, consolidated P&L, top movers
and pending drafts for one or more books. Book-specific P&L flow charts and
balance-sheet composition live in that book's **Overview**. Opening a book
in the sidebar does not change the books included in portfolio reports;
use each report's inclusion controls for that.

Cross-book reports show their generation time. After syncing journals or recording
prices, choose **Run aggregation** on the page you are viewing. Dashboard refreshes
its P&L inputs and Net Worth generation together; the Net Worth page refreshes
its own analytics file. Remote Net Worth reads
that same Net Worth generation. Date and cash filters query the downloaded file
locally. Changed book selections or reporting currency create a separate scope.
Only synced data enters cloud generations. Net Worth keeps showing its last successful
report while the next one is queued, running or waiting for an automatic retry.
Repeated requests reuse that job. After success or failure, wait 60 seconds before
starting another generation; the page shows the remaining wait. Failed refreshes
retain the last completed figures and show a warning. The next daily generation
is available after midnight UTC, once any current job and cooldown finish.

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
- **Approve a draft** — read the original source on its detail page, then use
  **Approve reviewed source**. Bulk approval first displays each selected source.
  Approval binds those exact versions; changed sources must be reviewed again.

Create, edit, delete and restore records through local files and permitted CLI/API
operations. Web records are read-only except for the reviewed `draft → posted`
transition. Posting preserves unknown fields, quantities, lots, comments and body.

Named-view Books label amounts **View preview**, including shared-root entries.
The detail page identifies the default preview; CSV exports retain the unapproved
scope. Approval marks the shared source as posted and does not accept its financial
variations. Use **Book settings → Accounting view acceptance** to review and accept separately prepared calculations. Report selectors choose an accepted view; CSV and ledger drilldowns retain its identity. Stale or unaccepted calculations remain unavailable.

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
who deleted them and when — deletions are recorded, not erased. Download a historical
version for inspection; restore through permitted local/CLI operations.

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
operation. Each row can expand to show a content **diff** and download a prior
version when available. Web does not replace the current record. Post-seal changes
are badged. This is
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

Run `iris validate` locally before syncing and closing. Overlay checks and recipe
replay run on local clients using Book-contained definitions; the cloud checks
native accounting, access, posting, seals and revision consistency. A successful
cloud preview or close does not certify Overlay validation or recipe replay.
If `config/balance-assertions.yaml` is configured, the preview also compares its
observations with the accepted synced ledger and evidence versions. Review recorded,
observed and difference values; missing/changed evidence remains unresolved even
when balances match. Correct the underlying records locally, sync and preview again.
The server refuses close until those native observations pass. A stale/missing
source-data error requires a server projection rebuild; repeated close attempts
cannot repair it. Matching hashes establish source identity, not correct transcription
or bank authenticity.
Named-view close requires every declared view accepted against the current complete inputs with no draft source events. The preview lists the pinned generations. Close locks referenced evidence and calculations; unrelated incoming raw files remain writable.

Closing never removes anything: the year's files stay in the book.

A book covers one fiscal year. The next year starts as a book of its own —
created from the CLI with [`iris yearend`](cli-reference.md#iris-yearend) —
and appears in **My Books** beside this one, with the same people's access.

The same flow works from the CLI (`iris api seal`, `iris reopen`) — see
[Japan tax & compliance](japan-tax-and-compliance.md). Members who aren't
the owner see the same year list read-only.

## Settings — your settings and book settings

Settings are split by what they affect. Open them with the top-right
**Settings** gear or **avatar menu → Settings**.

**Your settings** (avatar menu → Settings — available everywhere, even
outside any book) hold what belongs to you, not to a book:

- **Change password** — enter your current password and confirm a new one.
  After saving, browser/CLI sessions, API tokens and connected apps are
  revoked. Sign in with the new password and reconnect your tools.
- **Sign-in email** — verify the new address with its email code. Until
  verification finishes, your current address still works for login and
  recovery. Use **I already have a verification code** after a page reload.
- **Close account** — permanent. Export needed data and delete cloud books
  you created or hold Owner access to first. Sign out and sign in again,
  then close within five minutes by typing your email and confirming.
  Personal settings/prices and shared-book access are removed; your sign-in
  identity is deleted. Local files and others' shared books remain. Book
  histories, deleted-book retention and security records follow the privacy
  policy. If cleanup is incomplete, contact support privately with the
  reference shown. A closed account cannot be reopened.
- **Language** — switch the interface between English and 日本語.
- **Appearance** — light, dark, or follow the system.
- **Books** — every book you're a member of, with your role; each row opens
  that book's own settings page.
- **Account security** — sign out every device and revoke all API tokens,
  CLI sessions, connected apps, and pending sign-in approvals. Confirm the
  action, then sign in again and reconnect your tools. Use this if a device
  or credential may have been lost.
- **Personal Access Tokens** — create tokens for the CLI and integrations.
- **Connect your AI** — the remote connector URL and setup steps. See
  [Your AI on the go](remote-connector.md).
- **Connected apps** — the AI apps connected through the remote connector,
  with a **Disconnect** button to revoke one's access.

**Book settings** (sidebar → Settings, inside the book — or one click from
the Books list above) hold what belongs to that book:

- The book's **ID and fiscal year**.
- **Posting approval** (book owners only) — when on, CLI/AI writes to posted
  entries and local posting are refused (`APPROVAL_REQUIRED`). Review and approve
  exact draft sources in Web. The current Web supports approval only; correcting
  or demoting posted content while this gate is enabled remains unavailable.
  Only the owner can change this setting, from this page.

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
accountant (or the accountant invites the owner). Each can work with AI on
their own synced files, sharing the same cloud book. Web supports viewing,
review and permitted approvals alongside that file work.

### Personal Access Tokens (PATs)

A PAT is a long-lived credential for scripts and the CLI, scoped by role
(**viewer / bookkeeper / full**). Create one in your settings (avatar menu →
Settings), copy it **once** (it
won't be shown again), and use it as `IRIS_API_TOKEN`. A token expires after
90 days unused — each use renews it, up to one year from creation. Tokens show
their last-used time and expiry, and you can revoke any token immediately — here in
Settings, or from the CLI with `iris api token list` / `iris api token revoke`
(Full-access PATs can revoke tokens too; creating one stays web-only).
Select the books the token may access. Your role on each book remains the
upper bound; listings and reports include only permitted books. **Allow creating
books** also gives this token the same action permissions on books it creates,
including the next year's book. Unrelated books created elsewhere are excluded.
Year-end continuation requires Full scope and Owner on the source book. A
restricted Full token can list/revoke itself; other tokens remain manageable in
the web app. Older unrestricted credentials retain their existing access;
revoke and recreate them to narrow it.

## Net Worth

**Net Worth** adds up assets minus liabilities across your included books.
The headline shows that net amount. The chart separately shows **asset valuation**
as a line and **acquisition cost of remaining holdings** as a teal shaded area,
with their difference above it. When cash is included, an ochre area stacks
cash/book-value assets above holdings cost, and the combined total is labelled
**Acquisition cost + cash/book-value assets**. The legend, tooltips and dated table
show the two components separately. Buying holdings with existing cash changes
the split without changing the combined cost. Acquisition cost is not cumulative
deposits or realized profit. The checkbox applies to the chart and totals together.
Liabilities affect the Net Worth headline; they are not acquisition cost.
Accounts marked `owner: true` and their descendants are excluded.

The **Settings** tab chooses included books. Each annual book contributes only
within its own fiscal year. `iris yearend` carries complete opening lots and
costs into the next book, which works independently. Include earlier books for
their historical periods; missing years remain blank. The year boundary adds
no purchase or deposit.

Cloud generation reads current accepted DSQL projections in one consistent
snapshot when the worker starts, then saves frozen inputs for retries. Journal
edits during capture cannot mix old and new projections. Sync and run aggregation
to include later changes.

Prices are the observations you record, never future prices. Missing prices use
book value and show a coverage warning. Missing acquisition basis or disposal
policy leaves cost blank; book-value revaluations do not become acquisition cost.
The chart samples weekly and includes the selected endpoint. Expand the date/value
table for exact displayed observations, or download the DuckDB file for your own
SQL and pivot analysis. Acquisition cost uses the ordinary posted ledger or a named Book’s accepted default native generation. Additional fields → Accepted financial view shows its identity; regenerating refuses stale acceptance.

Expand **Additional fields** to inspect saved journal-line, asset or book-setting
values in this report. Choose a record type, then use **Find fields** to list
observed paths and record counts in 100-path pages. Optional path search is a
literal, case-sensitive substring. Select a path such as `/tax/category` to
inspect it. **Records** shows each original source and its value/type;
an optional exact JSON filter distinguishes `100` from `"100"`. Results page
through 100 records at a time. Long values preview the first 4,096 characters;
download the report for the full values.

**Group by value** shows typed groups, record counts and sums. Integer sums are
exact; fractional sums marked `≈` are approximate. A value or sum outside the
supported numeric range shows **Out of range**, retaining the original value.
Strings, arrays and missing values are excluded from sums.
The first 100 groups are shown. Large integers retain every digit, while a
missing field stays distinct from an explicit `null`. These fields use the
displayed report's included books and generation time. Sync and run aggregation
to include later changes; older report files may also need regeneration.

**Read field references** opens declarations and guidance from the current synced
Book. For grouped results, explicitly select an included Book for reference help.
These references may be newer than the frozen report. Book settings also offers
the package overview: stored selection/settings, declared fields/tasks, exact
guide sections and task examples. It shows the Book revision and read time.
Unavailable metadata remains explicit. Cloud does not evaluate package
compatibility, applicability, requiredness conditions, validation or calculations;
use local context for those checks and unsynced changes.

No market data is fetched for you. Record prices, including FX, with `iris price
add`; refresh after syncing them. Acquisition FX uses the acquisition date when
available. These figures are a best-effort portfolio view.

## For accountants — the daily shape

Prepare and validate work with your own AI in a separate work folder and
restricted assistant environment for each client. See the
[file workflow](cli-and-llm.md) for folder, tool and credential boundaries.
Use the web app to organize your review across clients:

- **My Books** is your client directory — each book (one per client per
  fiscal year) with its year, draft count, last activity, and a **Year-end**
  column showing that year's close state: closed, reopened, **ready to
  close**, or "N drafts" still blocking it. At year-end this column is your
  worklist — each badge links straight into that book's Year-end screen.
- Switch into a client book to review and approve entries, check the
  **Activity** log for what staff did, and run reports.
- Run authorized **PAT** + `iris api …` batch scripts separately from
  individual clients' AI sessions.
- At year-end, close each client's fiscal year from **Year-end** (or the
  CLI) — see
  [Japan tax & compliance](japan-tax-and-compliance.md).

Cloud permissions are granted per book; a client may have several fiscal-year
books. Keep that client's files together in their own workspace. The dashboard's
**Consolidated P&L** includes all books you can access by default, including
client books; use its book picker to choose the totals you want to see.
**Net Worth** defaults to owned books only; invited books require opt-in in
its Settings tab.

Next: [Japan tax & compliance](japan-tax-and-compliance.md).
