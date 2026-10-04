# Bookkeeping with the CLI and your own LLM

This is the file-first way to keep your books: you bring your own
AI assistant (Claude, Cursor, Copilot, or any MCP-capable agent), it reads and
writes the Markdown/YAML files, and the `iris` CLI checks the work and answers
questions about the books. Everything here works offline.

## The mental model

You don't type ledger entries into a form. Instead:

1. You drop **source documents** into `raw/`.
2. Your **AI** reads them and proposes **journal entries** as files.
3. **`iris`** validates the structure and the math and computes reports.
4. **You** review and approve (promote entries to `posted`).

The AI does the tedious transcription; `iris` is the deterministic referee;
you stay in control of what becomes final.

## One-time setup: connect your AI

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

Every book also ships an `LLM-GUIDE.md` at its root: a complete working
contract your AI reads before touching anything. You don't need to read it,
but it's why the AI knows the conventions (filenames, double-entry rules,
where to flag uncertainty).

> **Sandboxed assistants** (e.g. agents in a VM without the `iris` binary):
> there is no bundled copy inside the book. The model is "one host `iris`,
> reached over MCP" — the host runs `iris mcp serve` and the assistant calls
> the verbs as MCP tools against the same folder.

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
the same book folder and restart. Updating the CLI alone does not update it.
On Windows, stop IrisBooks MCP servers and retry if the executable is locked.

Older binaries without `iris update` can be upgraded by rerunning the
[installer](getting-started.md), then `iris onboard`. Ask before installing
an update unless the user has already authorized it.

## The everyday loop

### 1. Drop a document into `raw/`

Put bank CSVs, receipt scans, or PDF invoices anywhere under `raw/`. Subfolders
by date or vendor are fine — the AI figures out what each file is from its
contents, not its location.

### 2. Ask your AI to process it

Tell your assistant something like *"process the new bank statement in raw/"*.
Following `LLM-GUIDE.md`, it will:

- Read the file in full and write a **parse cache** to
  `notes/raw/<source>.md` — a durable table marking each row `journaled`,
  `ignored`, or `deferred`. This means re-opening the same statement later
  doesn't redo the work.
- Propose one journal per real transaction as
  `journals/YYYY-MM/…-NN.md` with `status: draft`.
- File anything ambiguous in `notes/open-questions.md` instead of guessing.

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

`iris search` and `iris show` are deterministic, offline views over your
files — use them (and let your AI use them) instead of eyeballing folders.

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

After that:

- `iris sync` pushes your local changes and pulls anything new (e.g. entries
  your accountant added in the web app). It reports per-file accept/reject.
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
[`schedule:`](book-format-reference.md#schedule--recording-the-table-instead-of-computing-it)
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
