# Getting started

There are two ways into IrisBooks. Most owners begin with the **CLI** (works
fully offline, no account). If you use the cloud, or you're an accountant,
you'll also use the **web app**. This page walks both.

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
…), fiscal-year start, the fiscal year the book covers (a book is one year —
pick last year's if you're catching up on its filing), and whether your AI assistant should **post entries
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
payables, loans — as your first journal entry, dated the first day of the
book's fiscal year and tagged `opening-balance` (the opening entry
`iris yearend` writes into next year's book gets the same tag
automatically; the cash-flow view leaves it out, since a carried balance is
not money coming in). If you're
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

That's the whole offline loop: files in `raw/`, entries in `journals/`,
`iris validate` to check, `iris report` to read. No account, no network.

## Path B — Use the web app (cloud)

The web app gives you a graphical interface, cloud sync, multi-device access,
collaboration, and the durable server history. It needs an IrisBooks account.

### 1. Sign in

Go to the IrisBooks web app and sign in (or sign up). Accounts are
email + password. If your accountant invited you, sign up with the invited
email address and the book will already be waiting.

### 2. Create a book

If you have no books yet, the app drops you into the **New book** wizard. Give
the book a name and region, say whether an individual or a company keeps it,
and pick the month its fiscal year starts (a Japanese company defaults to
April, everyone else to January). It's created in the cloud — already seeded
with its `config/book.yaml` and a starter chart of accounts, so
`iris clone <book-id>` gives you a working local folder right away.

Region, individual-or-company and the fiscal-year start can't be changed once
the first journal is posted. The review step shows the dates your first fiscal
year covers, so check them there.

### 3. Link an existing local book (optional)

Already have a book on disk from Path A? Connect the two so they sync:

```bash
iris api login                 # one-time browser sign-in (this device gets its own session)
iris api books new             # or: iris api books link <book-id>
iris sync                      # push your local files up
```

Run inside your book folder, `iris api books new` creates the cloud book from
that folder's own settings (name, fiscal year, region, …) and links it for
you — that's why `iris sync` works on the next line. If you
already created the book in the web app, use `iris api books link` with the id
the app showed you instead; running `new` again would give you a second book.

Now the same book is reachable from both the CLI and the web app. See
[Core concepts → Sync](concepts.md#sync-the-three-ways-to-work) for
what syncing does and doesn't change.

### 4. Work in the app

The top bar holds the **Dashboard** tab and the book plate — pick a book
there to enter it. Inside a book, the left sidebar lists the book's
screens: Journals, Activity, the reports, and a Manage group (Accounts,
Raw documents, Notes, Year-end, Settings). Your avatar (top right) opens
your account settings. Full walk-through in
[Using the web app](web-app.md).

## Do I need an account?

Not for bookkeeping itself — the local files and CLI are complete on their
own. An IrisBooks account adds sync, the web app, collaboration, and the
durable correction/deletion history that Japan's (optional) 優良電子帳簿
status requires. See
[Core concepts → Sync](concepts.md#sync-the-three-ways-to-work).

## Next steps

- Understand the moving parts → [Core concepts](concepts.md)
- Do the file-first workflow → [Bookkeeping with the CLI and your own LLM](cli-and-llm.md)
- Learn the GUI → [Using the web app](web-app.md)
- File taxes in Japan → [Japan tax & compliance](japan-tax-and-compliance.md)
