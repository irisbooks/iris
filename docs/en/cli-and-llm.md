# Bookkeeping with the CLI and your own LLM

This is the free-plan, file-first way to keep your books: you bring your own
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

This wiring is for the machine the book folder lives on. On a paid plan you
can also talk to your books away from that machine — see
[Your AI on the go (remote connector)](remote-connector.md).

Every book also ships an `LLM-GUIDE.md` at its root: a complete working
contract your AI reads before touching anything. You don't need to read it,
but it's why the AI knows the conventions (filenames, double-entry rules,
where to flag uncertainty).

> **Sandboxed assistants** (e.g. agents in a VM without the `iris` binary):
> there is no bundled copy inside the book. The model is "one host `iris`,
> reached over MCP" — the host runs `iris mcp serve` and the assistant calls
> the verbs as MCP tools against the same folder.

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
  `journals/<fy>/<mm>/…-NN.md` with `status: draft`.
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
iris post journals/2026/05/2026-05-04-example-com-01.md
```

`iris post` validates the file (non-empty, balanced), sets `status: posted`,
and — if the book is linked to the cloud — syncs it. Use `--dry-run` to check
without changing anything. You can also just edit the `status:` field by hand;
`post` is the convenience that also balances-checks and syncs.

## Going online (paid plans)

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
- `iris api history --path journals/2026/05/...md <book-id>` shows the durable
  correction/deletion record for a file.

Sync stays **explicit** — it runs when you ask, never in the background.

## Fixed assets and depreciation

If you own depreciable assets, describe each one in `assets/YYYY/<name>.md`
(acquisition cost, useful life, method). Then:

```bash
iris asset schedule                       # see each asset's depreciation plan
iris asset depreciate --month 2026-05     # generate that month's depreciation entries
```

`iris asset depreciate` writes proposed entries (`status: draft`) you review
and post like any other. Details and the Japan-specific rules are in
[Japan tax & compliance](japan-tax-and-compliance.md#fixed-assets-and-depreciation).

## Exporting

```bash
iris export                 # journals.csv, trial-balance.csv, ledger-*.csv
iris export --year 2026     # restrict to a fiscal year
iris export assets          # per-asset depreciation schedule
```

CSVs are written UTF-8 with a BOM so Excel opens Japanese correctly. On a paid
plan, `iris api export audit <book-id>` produces an auditor-facing bundle.

## A note on what *not* to do

These rules keep your books trustworthy (your AI follows them too):

- Don't mass-edit `posted` entries — record a correcting entry instead.
- Don't hand-edit `compiled/` — it's regeneratable output.
- Don't invent accounts inside a journal — add them to the chart first.

Next: the graphical side in [Using the web app](web-app.md), or the full
command list in the [CLI command reference](cli-reference.md).
