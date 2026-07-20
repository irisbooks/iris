# Getting started

There are two ways into IrisBooks. Most owners begin with the **CLI** (works
fully offline, free). If you're on a paid plan or you're an accountant, you'll
also use the **web app**. This page walks both.

## Path A — Create a book on your machine (CLI)

### 1. Install `iris`

`iris` is a single binary. On macOS or Linux:

```bash
curl -fsSL https://irisbooks.jp/install.sh | sh
```

On Windows (PowerShell):

```powershell
irm https://irisbooks.jp/install.ps1 | iex
```

The installer downloads the binary for your platform, verifies its signature,
and puts it on your `PATH`. Confirm with:

```bash
iris version
```

If `iris` isn't found, open a new terminal (the `PATH` change takes effect in
new shells) or run the install command above again.

### 2. Create your first book

Run the guided wizard in an empty directory:

```bash
iris init
```

It asks for a book name, region, language, entity kind (individual / company /
…), fiscal-year start, and whether your AI assistant should **post entries
automatically** after validating (say no to review and post them yourself —
you can change this later by editing the "Posting policy" section of
`LLM-GUIDE.md`). Then it scaffolds the folder. You can also skip the prompts:

```bash
iris init --name "Acme Design" --region JP --language en \
  --entity-kind individual --fiscal-start-month 4
```

Add `--sample` to seed ~40 demo entries you can explore and then delete. See
[`iris init`](cli-reference.md#iris-init) for every flag.

### 3. Make the book your own

Open `config/chart-of-accounts.yaml` and adjust the accounts to match your
business. Then record your **opening balances** — cash, bank, receivables,
payables, loans — as your first journal entries, tagged `opening-balance`
(reports treat the latest entry with that tag as the starting point for
balances; year-end carry-forwards get the same tag automatically). If you're
migrating from another system, these should reconcile to that system's trial
balance at the cutover date. (`notes/todos.md` has a task reminding you of
this.)

### 4. Connect your AI assistant

The fastest way to actually do bookkeeping is to let your AI assistant read
and write the files. Wire it up once:

```bash
iris onboard
```

This registers `iris mcp serve` with your MCP-capable clients (Claude Code,
Claude Desktop, Codex, Cursor, Gemini CLI, VS Code) and writes a Claude Code
skill so your assistant knows how to work in the book. See
[Bookkeeping with the CLI and your own LLM](cli-and-llm.md) for the full
workflow. Your AI reads `LLM-GUIDE.md` at the book root before working.

### 5. The everyday loop

```bash
# 1. Drop a bank CSV / receipt / invoice anywhere under raw/
# 2. Ask your AI to process it into journal entries (status: draft)
# 3. Check the structure and the math
iris validate
# 4. See where you stand
iris balance
iris report pl --from 2026-04-01 --to 2026-06-30
```

That's the whole free-plan loop: files in `raw/`, entries in `journals/`,
`iris validate` to check, `iris report` to read. No account, no network.

## Path B — Use the web app (paid plans)

The web app gives you a graphical interface, cloud sync, multi-device access,
collaboration, and the durable server history. It's part of any paid plan.

### 1. Sign in

Go to the IrisBooks web app and sign in (or sign up). Accounts are
email + password. If your accountant invited you, sign up with the invited
email address and the book will already be waiting.

### 2. Create a book

If you have no books yet, the app drops you into the **New book** wizard. Give
the book a name, region, and fiscal year, and it's created in the cloud —
already seeded with its `config/book.yaml` and a starter chart of accounts,
so `iris clone <book-id>` gives you a working local folder right away.

### 3. Link an existing local book (optional)

Already have a book on disk from Path A? Connect the two so they sync:

```bash
iris api login                 # one-time browser sign-in (this device gets its own session)
iris api books new             # or: iris api books link <book-id>
iris sync                      # push your local files up
```

Now the same book is reachable from both the CLI and the web app. See
[Core concepts → Sync and plans](concepts.md#sync-the-three-ways-to-work) for
what syncing does and doesn't change.

### 4. Work in the app

The left sidebar splits into **Across all books** (Dashboard, My Books, Net
Worth) and **Current book** (Journals, Activity, Reports, Accounts, Raw
documents, Notes, Settings). Full walk-through in
[Using the web app](web-app.md).

## Which plan do I need?

You can do real, complete bookkeeping for free. Paid plans add sync, the web
app, collaboration, and the durable correction/deletion history that Japan's
(optional) 優良電子帳簿 status requires.

| | Free | Personal | Pro | Pro (Accountant) |
| --- | :---: | :---: | :---: | :---: |
| Local book + AI | ✓ | ✓ | ✓ | ✓ |
| Sync + web + period seals | | ✓ | ✓ | ✓ |
| Books you own | 1 | 2 | unlimited | 2 |
| Be invited to others' books | | up to 2 | up to 2 | up to 500 |
| Invite others to your book | | 1 | unlimited | unlimited |

More detail in [Core concepts → Plans](concepts.md#plans-what-each-tier-adds).

## Next steps

- Understand the moving parts → [Core concepts](concepts.md)
- Do the file-first workflow → [Bookkeeping with the CLI and your own LLM](cli-and-llm.md)
- Learn the GUI → [Using the web app](web-app.md)
- File taxes in Japan → [Japan tax & compliance](japan-tax-and-compliance.md)
