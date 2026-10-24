# Your AI on the go (remote connector)

The remote connector lets an AI app read the cloud copy of your synced books
when you are away from your computer. Ask for figures, inspect journals and
look up stored references from your phone or browser.

Bookkeeping in the first release is **read-only**. Optional raw document uploads
are the exception: saving evidence does not execute accounting overlays. Creating or changing records requires the
book's accounting rules to run locally. Use the local CLI or local MCP setup
for those changes; sync afterward to make them visible remotely.

The connector speaks MCP and supports **Claude** (mobile, web, desktop and
Claude Code) and **ChatGPT**. It recognises supported apps through their Client
ID Metadata Documents. Other MCP apps cannot complete the current sign-in flow.

After choosing a book, your assistant calls `read_book_guide` for its synced
`AGENTS.md`. Book policy cannot expand the connector's read-only permissions.

## Set it up

1. Add a custom connector in your AI app with this URL:

   ```text
   https://irisbooks.io/mcp
   ```

   In Claude: Settings → Connectors → Add custom connector.
2. Sign in through the browser and approve **Viewer — read-only** access.
   Optionally allow **raw document uploads**. There is no drafting permission to choose. If the app runs on this computer,
   approve the localhost warning only when you just started the connection.
3. Ask the assistant to list your books and select one. The user's current
   book grants still apply; a connector cannot read an inaccessible book.

Existing Bookkeeper connections are narrowed to reads and raw uploads. New
connections default to Viewer; the optional `evidence:upload` permission allows
raw document links. Refreshed tokens retain the approved combination. Connector
tokens remain Viewer-only on the general REST API. This does not change your separate local CLI
credentials or collaborator roles.

## What you can do from anywhere

- **Read reports** — `get_report` provides trial balance, P&L, balance sheet,
  account ledger and grouped totals. Ordinary books use posted entries;
  named views require a current accepted financial ledger. Responses include
  the sync watermark `figures_as_of` when available.
- **Inspect asset movements** — `get_report(report="cashflow")` is the legacy
  name for monthly gross asset increases/decreases, including receivables and
  fixed assets. Transfers can count on both sides. It is not a cash-flow statement.
- **Browse journals and accounts** — `list_accounts`, `search_journals` and
  `get_journal`. Search filters combine with AND. Amount bounds are nonnegative
  integer minor units; follow `nextCursor` using the same filters. `journal_path`
  from search selects a journal. Sealed-year entries appear as `closed`.
- **Read Net Worth, holdings and prices** — `get_networth`, `get_holdings` and
  `list_prices` read synced cloud data. Price listing accepts `unit`, `currency`,
  `year`, `limit` and `cursor`; follow `nextCursor` until empty. Prices are scoped
  to the authenticated user. Net Worth's omitted `as_of` uses the generation's
  reporting date; holdings default to today.
- **Read package references** — `get_book_context` returns stored selections,
  task/field metadata, settings, guide sections and declared examples. It checks
  access and Book revision, but does not execute CEL, validate records or run recipes.
- **Check the fiscal year** — `fiscal_years` reports open/closed/reopened state,
  entry counts and drafts that block closing.
- **Capture raw evidence** — with upload permission and Owner/Bookkeeper access,
  `create_upload_link(book_id=...)` creates a one-time image/PDF link (15 minutes,
  up to 10 MB). Scanned files land under `raw/uploads/`. It accepts no
  `journal_path` and never edits or attaches to a journal. Wait for the upload
  page to confirm delivery, then link the evidence through the local workflow.
- **Look up an existing receiving address** — `get_inbox_address` reads address
  metadata only. It does not send email or create upload links.

Select cloud books with `book_id` from `list_books`. Report arguments depend on
`report`: `as_of` for trial balance/balance sheet; `from`/`to` for P&L;
`account` plus `from`/`to` or `as_of` for ledger; `by` plus `from`/`to` or
`year` for sum; `year` for asset movements. Inapplicable fields, invalid types,
unknown arguments and reversed ranges return errors rather than being ignored.

Net Worth shares **one automatic input generation per user per UTC day** with
web cross-book reports. Changing dates, book selection or currency does not
refresh captured inputs. Responses show `snapshot.generatedAt` and
`snapshot.nextRefreshAt`. To capture synced changes sooner, choose **Run
aggregation** on the web Dashboard or Net Worth. Remote MCP reads that updated
snapshot and cannot invoke the manual aggregation action itself.

## What it deliberately can't do

The connector cannot create, edit or delete journals, record prices, apply
completions, run recipes, post or approve entries, or seal/reopen a year. Former
draft tools are removed. Raw evidence upload remains available with explicit
permission; it does not create or change accounting records.
Use the local CLI or local MCP server for bookkeeping changes so the selected
accounting rules and validation run before sync.

## At the computer or on the go?

| You are… | Use | What it provides |
| --- | --- | --- |
| At your computer | the [local setup](cli-and-llm.md) | live files and the author → validate → post → sync workflow |
| Away from it | the remote connector | cloud reports, journals and stored references, plus optional raw evidence upload |

You can configure both. An assistant that sees both is instructed to prefer the
local server when available, since it includes unsynced edits.

## Disconnecting

Remove the connector in your AI app, or use IrisBooks Settings → Connected apps
→ **Disconnect**. Successful revocation applies to the next request; an already
admitted request may finish. Your underlying collaborator role is managed
separately in the book's Settings → Grants.
