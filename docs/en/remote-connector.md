# Your AI on the go (remote connector)

The remote connector lets an AI app read the cloud copy of your synced books
when you are away from your computer. Ask for figures, inspect journals and
look up stored references from your phone or browser.

For bookkeeping the connector is **read-only**. Creating or changing a record
means checking it against the book's accounting rules, and those run only on
your computer. Make changes with the local CLI or local MCP setup, then sync,
and the connector sees them. There is one exception, and it is optional: you
can allow the connector to upload source documents such as a photo of a
receipt. An upload saves a file and touches no record.

The connector speaks MCP and supports **Claude** (mobile, web, desktop and
Claude Code) and **ChatGPT**. It recognises supported apps through their Client
ID Metadata Documents, so other MCP apps cannot sign in at present.

After you choose a book, your assistant first calls `read_book_guide` to read
the book's synced `AGENTS.md`, its working guide. Whatever the guide says, it
cannot widen the connector's read-only access.

## Set it up

1. Add a custom connector in your AI app with this URL:

   ```text
   https://irisbooks.io/mcp
   ```

   In Claude: Settings → Connectors → Add custom connector.
2. Sign in through the browser and approve **Viewer — read-only** access.
   To upload source documents, also allow **raw document uploads**. There is
   no permission for writing drafts. If the AI app runs on the same computer
   as your browser, the page shows a warning about localhost. Approve it only
   if you started the connection yourself a moment ago.
3. Ask the assistant to list your books and select one. The connector can
   read only the books you currently have access to.

What a connection is allowed to do:

- A new connection gets Viewer access. If you also allowed uploads, it gets
  the `evidence:upload` permission, which lets it issue upload links for
  source documents.
- A connection approved earlier with Bookkeeper access is now limited to
  reading and uploading as well.
- Renewing a connection keeps the combination you approved.
- On the general REST API, a connector's token has Viewer access only.

Your local CLI sign-in and your role in each book are managed separately.
Nothing you change on the connector affects them.

## What you can do from anywhere

- **Read reports** — `get_report` provides trial balance, P&L, balance sheet,
  account ledger and grouped totals. For an ordinary book the figures come from
  posted entries. For a book with named views they come from the calculation
  currently accepted for that view. Responses include
  the sync watermark `figures_as_of` when available.
- **Read the cash flow statement** — `get_report(report="cash-flow-statement")`
  gives the movements of the accounts the chart marks as cash, by operating,
  investing and financing activity, with opening and closing cash.
- **Inspect asset movements** — `get_report(report="cashflow")` is the legacy
  name for monthly gross asset increases/decreases, including receivables and
  fixed assets. Transfers can count on both sides. It is not a cash-flow statement.
- **Browse journals and accounts** — `list_accounts`, `search_journals` and
  `get_journal`. Search filters combine with AND. Amounts, including the bounds,
  are decimal strings in the book currency, as journal files write them
  (`"98.00"`); follow `nextCursor` using the same filters. `journal_path`
  from search selects a journal. Sealed-year entries appear as `closed`.
- **Read Net Worth, holdings and prices** — `get_networth`, `get_holdings` and
  `list_prices` read synced cloud data. Price listing accepts `unit`, `currency`,
  `year`, `limit` and `cursor`; follow `nextCursor` until empty. Prices belong
  to the signed-in user, not to a book. When `as_of` is omitted, Net Worth uses
  the reporting date of its aggregation, and holdings use today.
- **Read package references** — `get_book_context` returns stored selections,
  task/field metadata, settings, guide sections and declared examples. It checks
  access and Book revision, but does not execute CEL, validate records or run recipes.
- **Check the fiscal year** — `fiscal_years` reports open/closed/reopened state,
  entry counts and drafts that block closing.
- **Capture raw evidence** — with upload permission and Owner/Bookkeeper access,
  `create_upload_link(book_id=...)` creates a one-time image/PDF link (15 minutes,
  up to 10 MB). Scanned files land under `raw/uploads/`. It accepts no
  `journal_path` and never edits or attaches to a journal. Wait until the upload
  page confirms that the file arrived. Linking it to a journal is done later,
  in the local workflow.
- **Look up an existing receiving address** — `get_inbox_address` reads address
  metadata only. It does not send email or create upload links.

Select a cloud book with a `book_id` from `list_books`. The arguments
`get_report` takes depend on the report:

| Report | Arguments |
| --- | --- |
| Trial balance | `as_of`; add `from` for the period form |
| Balance sheet | `as_of`; `compare: prior-year` to add last year's figures |
| P&L | `from`, `to`; `compare: prior-year` to add last year's figures |
| Monthly trend (`trend`) | `from`, `to` |
| Cash flow statement (`cash-flow-statement`) | `from`, `to` |
| Ledger | `account`, with `from`/`to` or `as_of` |
| Grouped totals | `by`, with `from`/`to` or `year` |
| Asset movements (`cashflow`) | `year` |

An argument the report does not use, a value of the wrong type, an unknown
argument or a reversed date range returns an error; none is silently ignored.

Net Worth uses the same aggregation as the web's cross-book reports. It runs
automatically **once per user per UTC day**. Changing the dates, the book
selection or the currency does not refresh the data that run captured.
`snapshot.generatedAt` is when it ran and `snapshot.nextRefreshAt` is when the
next automatic run is due. To pick up synced changes sooner, choose **Run
aggregation** on the web Dashboard or Net Worth. The connector reads the
updated result but cannot start that run itself.

## What it deliberately can't do

The connector cannot:

- create, edit or delete journals;
- record prices;
- apply completions or run recipes;
- post or approve entries;
- seal or reopen a year.

Earlier versions could write drafts; the connector no longer can. Uploading
source documents is available only when you allowed it, and an upload never
creates or changes an accounting record. Make bookkeeping changes with the
local CLI or local MCP server, so that the book's accounting rules and
validation run before the change is synced.

## At the computer or on the go?

| You are… | Use | What it provides |
| --- | --- | --- |
| At your computer | the [local setup](cli-and-llm.md) | live files and the author → validate → post → sync workflow |
| Away from it | the remote connector | cloud reports, journals and stored references, plus optional raw evidence upload |

You can set up both. An assistant that can use both is told to prefer the
local one, because it also sees edits you have not synced yet.

## Disconnecting

Remove the connector in your AI app, or use IrisBooks Settings → Connected apps
→ **Disconnect**. From then on the next request is refused; a request that
was already accepted may still finish. Disconnecting does not change your
role in the book, which is managed in the book's Settings → Grants.
