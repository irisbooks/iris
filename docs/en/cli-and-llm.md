# Bookkeeping with the CLI and your own LLM

This is the file-first way to keep your books: you bring your own
AI assistant (Claude, Cursor, Copilot, or any MCP-capable agent), it reads and
writes the book's files, and the `iris` CLI checks the work and calculates
reports. Accounting records use Markdown with YAML frontmatter; configuration
uses standalone YAML. Local `iris` works offline without an account; your
chosen AI service may need its own internet connection.

## CLI use and support

The `iris` CLI is free and provided **as is**, without warranties. Individual
support, bug fixes and continued updates are not guaranteed. Review its output
and keep independent backups of your books. Questions and bug reports are
welcome in the [Discord community](https://discord.gg/wZDsv9gyb9); replies are
not guaranteed.

## The mental model

Start with what you want to record or understand:

1. Share a document, point your AI to an accessible file, or tell it what
   happened. With the tools and access you grant, it can also retrieve a statement.
2. Your **AI** files available originals under the book's `raw/`, interprets
   the information and proposes **journal entries** and a summary.
3. **`iris`** validates the structure and the math and computes reports.
4. **You** review, approve or ask questions. Review before posting is the
   default; follow the book's chosen policy if you authorize automatic posting.

The AI reasons and explains; `iris` checks and calculates. You do not need to
organize files manually or learn the file formats. Validation checks encoded
rules; it does not prove that a source was interpreted correctly.

## Personal tracking can stay relaxed

For everyday personal spending, keep as much detail as is useful to you.
You do not need every receipt. Report your current cash and let your AI ask
a few broad questions about spending since the last check-in, accounting for
cash added or transferred. Or use a credit-card or bank statement: keep its
amounts and let the AI infer broad categories. Estimates and unexplained
differences should stay visible rather than become invented purchases.

Business books need precise amounts, dates, classifications and supporting
evidence; personal records used for tax or reimbursement need the same care.
Ask your AI to save your preferred detail level in `notes/workflow.md` and
keep assumptions in the entries or notes. These files also preserve decisions
and questions for your next session or a different assistant. Optional sync
adds a cloud mirror and server-side change history.

## Accountants: use a separate work folder for each client

Accountants should also prepare and validate work in book files with their
own AI. Keep each client's books in a separate persistent folder. Give a
dedicated assistant session or VM, such as a Cowork session for Client A,
access only to Client A's folder. It can contain that client's books for
several fiscal years; do not mount the firm's all-client parent folder.

Clone existing shared books into that folder and sync through an authorized
workflow. Read their guides and notes, prepare corrections, validate and
follow the book's posting policy. Save context in the client's files so the
next session can continue. Keep a persistent copy outside temporary VM storage.

Check connected tools and credentials too. A shared host MCP server can have
broader cloud access than its file root, and PAT roles do not limit a token
to one client. Keep broad firm credentials and batch tools outside the client
session; if needed, clone/sync separately and give the AI only the selected
files and tools that cannot access other clients. Verify the actual boundary.

Use the [web app](web-app.md) for reports, review, permitted approvals and
history. It complements the accountant's file work.

## One-time setup: connect your AI

If your assistant already has CLI execution and file access, it can work without
MCP registration. Use `iris onboard` when you want an MCP integration or need
to add missing local guide files.

```bash
iris onboard
```

`iris onboard` registers `iris mcp serve` (a small server that exposes the
`iris` verbs as tools) with your MCP-capable assistants — Claude Code always,
plus Claude Desktop, Codex, Cursor, Gemini CLI, and VS Code when they're
installed — and writes a Claude Code skill. After that, your assistant can
call `validate`, `diff`, `balance`, `report`, `status`, and — once you're
signed in — `sync` directly, instead of guessing at ledger state.

Check what's wired up at any time with `iris onboard --status` (add `--json`
for your AI). Re-running `iris onboard` is always safe — registrations update
in place. To undo everything, `iris offboard` removes the registrations and
the skill without touching your books or sign-in.

This wiring is for the machine the book folder lives on. With a cloud-linked
book you can also talk to it away from that machine — see
[Your AI on the go (remote connector)](remote-connector.md).

Every new book has an English `AGENTS.md` at its root: a concise working
contract with the posting policy, integrity rules, a minimal journal and
reference lookup. Local CLI/MCP creation and web/API creation use the same
template. The file syncs with the book, and cloning preserves its contents.
`README.md` briefly explains the folder; `CLAUDE.md` points agents to `AGENTS.md`.
An Owner can customize the contract; changing it in the cloud requires Owner access.
For an older local book, `iris onboard` adds missing entry files and preserves
an existing `LLM-GUIDE.md` policy in `AGENTS.md`, without overwriting custom guides.

> **Sandboxed assistants** (e.g. agents in a VM without the `iris` binary):
> there is no bundled copy inside the book. If using host MCP, the host runs
> `iris mcp serve` and the assistant calls its tools against the same folder.
> For client work, the host connection must respect the client boundary above.

For Cowork's `.mcpb` extension, choose a **parent folder of books**, such as
`~/IrisBooks`, with each book in its own immediate child folder. Give Cowork
file access to the folder you will work in too. The extension can start with
an empty parent: ask your assistant to create a book with `create_book`.
It finds books with `list_books` and names the target book on every operation.
Adding another child book requires no change to the global MCP settings.
For manual setup, use `iris mcp serve --books-dir ~/IrisBooks`; `--book PATH`
continues to serve a single book. See [MCP commands](cli-reference.md#iris-mcp).

For accountant work, the parent must contain only one client's books, such
as `~/IrisBooks/ClientA/2026` and `~/IrisBooks/ClientA/2027`. Configure that
client's assistant connection to `~/IrisBooks/ClientA`, and check its cloud
credentials separately. A separate chat alone does not restrict access.

## Online docs and optional downloads

Your assistant reads the book's `AGENTS.md`, its current workflow summary and
relevant questions/decisions. It can then use installed command help or tool
schemas. `iris docs` lists bundled English topics; `iris docs <topic>` lists
sections and sizes. `--section <id>` reads one; `--full` explicitly reads the
chapter. Local MCP `read_docs` has equivalent `topic`, `section` and `full`
selectors without a book argument. No login, download or network is required.

For requested setup, use the [start guide](/start/); current cloud authorization
is in [cloud setup](/start/cloud/). Older tools without bundled lookup can use
the [docs index](/llms.txt). The [complete AI manual](/llms-full.txt) is optional.
An optional Markdown cache belongs outside bookkeeping records, with source URL
and release tag: `https://raw.githubusercontent.com/irisbooks/iris/<release-tag>/docs/llm.md`.
Match `iris version` where available and search only needed sections. Use the
book's selected overlays for its rules; reference material does not authorize actions.

## Check and update iris

```bash
iris update --check --json     # installed/latest versions and executable path
iris update                   # verify and replace the running executable
```

Checks contact the release server only when requested. They need no sign-in;
bookkeeping commands continue to work offline. A failed check means the
latest version is unknown. Development/prerelease builds are reported as
`development` and are not replaced automatically; newer stable builds are
never downgraded.

After updating, run `iris onboard` in your book to refresh agent guidance,
then restart the IrisBooks MCP server. Ask your AI to call `check_update` to
confirm the server's running version. Its report identifies PATH conflicts
and gives instructions for the executable the agent actually uses.

A `.mcpb` extension contains a separate binary. Its update report links the
matching bundle; reinstall it through your client's extension settings with
the same parent folder and restart. When upgrading an older bundle that asked
for one book, choose that book's parent folder in the new configuration.
Updating the CLI alone does not update the bundled server.
On Windows, stop IrisBooks MCP servers and retry if the executable is locked.

Older binaries without `iris update` can be upgraded by rerunning the
[installer](getting-started.md), then `iris onboard`. Ask before installing
an update unless the user has already authorized it.

## The everyday loop

### 1. Share information with your AI

You can attach a bank CSV, receipt scan or PDF invoice in chat, point to an
accessible folder, or ask the AI to retrieve it with tools and access you
grant. The AI can save the original under the book's `raw/`; you can also put
files there yourself if you prefer. Subfolders by date or vendor are fine.
For personal cash tracking, a reported balance and a short interview can be
enough without a document.

### 2. Ask your AI to process it

Tell your assistant something like *"record this statement"* or
*"help me catch up on my personal cash spending"*.
Following `AGENTS.md`, it will:

- For a document, read it in full and write a **parse cache** to
  `notes/raw/<source>.md` — a durable table marking each row `journaled`,
  `ignored`, or `deferred`. This means re-opening the same statement later
  doesn't redo the work.
- For an interview, save what you reported and any assumptions in the entry's
  body or book notes.
- Propose journals as `journals/YYYY-MM/…-NN.md` with `status: draft` at the
  agreed detail level.
- Record unresolved business questions or material unknowns in
  `notes/open-questions.md`; make personal estimates and inferred categories explicit.

### 3. Validate

```bash
iris validate
```

This checks every file: YAML parses, debits equal credits, accounts exist in
your chart, dates are consistent, statuses are valid, and (for Japanese
taxable businesses) tax classifications are coherent. Fix any errors — usually
a missing account in the chart, or an unbalanced entry — and re-run. Your AI
can do this loop for you.

If `iris validate` ends with a note about files *blocked in the sync queue*,
that's a server-side rejection, not a file problem — see
[Troubleshooting](troubleshooting.md#sync-rejections-needs-attention).

### 4. Review and read the books

```bash
iris balance                         # trial balance today (posted only)
iris report pl --from 2026-04-01 --to 2026-06-30
iris report bs --as-of 2026-06-30
iris search --payee amazon --from 2026-04-01     # find entries
iris show raw/2026-05-invoice.pdf                # what cites this document
```

Use filesystem tools (`rg`/`grep`, `find`, `cat`, `sed`, or a file editor) for
routine file listing, reading, text searches and draft/note edits when the
book folder is accessible. Keep operations within the selected book and run
validation after bookkeeping edits. Local MCP is for accounting calculations,
validation, authentication, sync and guarded workflows
such as posting, seals, depreciation and year-end. Structured search and other
inspection tools are optional helpers, useful for structured filters,
derived closed status or when the client cannot access files directly.

`iris search` and `iris show` remain available for structured offline views.

### 5. Promote to `posted`

A `draft` entry stays out of your reports and balances until posted. When
you're happy with one, promote it:

```bash
iris post journals/2026-05/2026-05-04-example-com-01.md
```

`iris post` validates the file (non-empty, balanced), sets `status: posted`,
and — if the book is linked to the cloud — syncs it. Use `--dry-run` to check
without changing anything. You can also just edit the `status:` field by hand;
`post` is the convenience that also balances-checks and syncs.

## Going online (cloud)

Linking a local book to the cloud unlocks the web app, multi-device access,
collaboration, period seals, and the durable history. The local
file-first workflow above doesn't change — you simply gain `iris sync`.

```bash
iris api login            # browser sign-in; this device gets its own CLI session
iris api books new        # create a cloud book…
# …or link this folder to an existing one:
iris api books link <book-id>
iris sync                 # one explicit push + pull pass
```

During browser approval, select the books this CLI may access. Enable
**Allow creating books** to create your first book or next year's book: books
created by this credential are automatically included with the same permissions.
Other later books are excluded. Callback, downloaded-file and device approval
use the same picker. Year-end continuation still requires Owner on the source
book and Full token scope.

After that:

- `iris sync` pushes your local changes and pulls anything new (e.g. entries
  your accountant prepared and synced from their files). It reports per-file accept/reject.
- `iris diff` shows exactly what *would* be pushed before you sync.
- `iris api history --path journals/2026-05/...md <book-id>` shows the durable
  correction/deletion record for a file.

Sync stays **explicit** — it runs when you ask, never in the background.

## Fixed assets and depreciation

If you own depreciable assets, describe each one in `assets/YYYY/<name>.md`
(acquisition cost, useful life, method). Then:

```bash
iris asset schedule                       # see each asset's depreciation plan
iris asset depreciate --year 2026         # one year-end entry per asset
iris asset depreciate --month 2026-05     # or that month's entries, if you close monthly
```

`iris asset depreciate` writes proposed entries (`status: draft`) you review
and post like any other. Details and the Japan-specific rules are in
[Japan tax & compliance](japan-tax-and-compliance.md#fixed-assets-and-depreciation).

### Depreciation your AI can't get wrong

Straight-line iris computes itself. Methods with a country-specific twist —
Japan's 定率法, US MACRS — work differently: your AI looks up the rates and
decides where the method switches, then hands the arithmetic to iris and records
the finished table on the asset file under `schedule:`.

Over the MCP connection your AI has four asset tools for this:

| Tool | What it does |
| --- | --- |
| `asset_schedule` | the engine's per-asset figures — use these for filings verbatim |
| `declining_table` | a declining-balance table at a rate you supply |
| `flat_table` | a fixed charge per period until the asset is written down |
| `straight_line_table` | a basis split evenly over N periods |
| `jp_teiritsu` (one tool per overlay recipe) | the region overlay's ready-made composition — preferred whenever one exists |

The point is that your AI never multiplies a balance forward by hand — that's
where arithmetic slips happen, and a slip that still adds up to the right total
is one iris cannot detect. It composes exact tables instead. Better still, when
the book's region overlay has a **recipe** for the method — Japan's 定率法 is
`jp_teiritsu` — it calls that: the recipe composes the tables in the prescribed
order and records where the rows came from, so `iris validate` can replay them
and catch a switch that landed a year late. Composing by hand is the fallback
for a method no recipe covers. See
[`schedule:`](book-format-reference.md#schedule-recording-the-table-instead-of-computing-it)
for the file format and what iris checks.

## Exporting

```bash
iris export                 # journals.csv, trial-balance.csv, ledger-*.csv
iris export --year 2026     # restrict to a fiscal year
iris export assets          # per-asset depreciation schedule
```

CSVs are written UTF-8 with a BOM so Excel opens non-ASCII text, such as
Japanese, correctly. A text cell (payee, memo, tags, account or asset name)
that starts with `=`, `+`, `-` or `@` is written with a leading `'`, so a
spreadsheet shows it as text
instead of running it as a formula; amounts are never changed. For a
cloud-linked book, `iris api history --all --json <book-id>` writes the
book's — that year's — correction/deletion record as a file.

## A note on what *not* to do

These rules keep your books trustworthy (your AI follows them too):

- Don't mass-edit `posted` entries — record a correcting entry instead.
- Don't hand-edit `compiled/` — it's regeneratable output.
- Don't invent accounts inside a journal — add them to the chart first.

Next: the graphical side in [Using the web app](web-app.md), or the full
command list in the [CLI command reference](cli-reference.md).
