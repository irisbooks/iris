# Getting started

Begin with book files and your own AI, whether you are an owner or an
accountant. Local **`iris` CLI** work needs no account or network. The optional
**web app** supports viewing, review and cloud administration. This page walks both.

Accountants should use a separate assistant work folder/session for each
client and clone existing shared books rather than create new identities.
See [the file workflow](cli-and-llm.md) for folder and tool access boundaries.

## Path A — Create a book on your machine (CLI)

### 1. Install `iris`

The CLI is free and provided **as is**. Individual support, bug fixes and
continued updates are not guaranteed. See [CLI use and support](cli-and-llm.md#cli-use-and-support).

`iris` is a single binary. On macOS or Linux:

```bash
curl -fsSL https://irisbooks.io/install.sh | sh
```

On Windows (PowerShell):

```powershell
irm https://irisbooks.io/install.ps1 | iex
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

It asks for a book name, region, language, fiscal-year start month (January
unless you pick another), the fiscal year the book covers (a book is one year —
pick last year's if you're catching up on its filing), and whether your AI assistant should **post entries
automatically** after validating (say no to review and post them yourself —
you can change this later by editing the "Posting policy" section of
`AGENTS.md`). Then it scaffolds the folder. You can also skip the prompts:

```bash
iris init --name "Acme Design" --region JP --language en \
  --fiscal-start-month 4 .
```

Add `--sample` to seed ~40 demo entries you can explore and then delete. See
[`iris init`](cli-reference.md#iris-init) for every flag.

### 3. Make the book your own

Open `config/chart-of-accounts.yaml` and adjust the accounts to match your
business. Then record your **opening balances** — cash, bank, receivables,
payables, loans — as your first journal entry, dated the first day of the
book's fiscal year and tagged `opening-balance` (the opening entry
`iris yearend` writes into next year's book gets the same tag
automatically; the asset-movements report leaves it out, since a carried balance is
not money coming in). If you're
migrating from another system, these should reconcile to that system's trial
balance at the cutover date. (`notes/todos.md` has a task reminding you of
this.)

### 4. Connect your AI assistant

If your assistant can already run the CLI and access this folder, no additional
integration is needed. Read `AGENTS.md` and start the requested work. To connect
an MCP client or refresh missing local guides, run:

```bash
iris onboard
```

This registers `iris mcp serve` with your MCP-capable clients (Claude Code,
Claude Desktop, Codex, Cursor, Gemini CLI, VS Code) and writes a Claude Code
skill so your assistant knows how to work in the book. See
[Bookkeeping with the CLI and your own LLM](cli-and-llm.md) for the full
workflow. Your AI reads `AGENTS.md` at the book root before working.

### 5. The everyday loop

```bash
# 1. Share a document, point to an accessible file, or report a personal cash balance
# 2. Your AI files available originals in raw/ and prepares entries (status: draft)
# 3. Check the structure and the math
iris validate
# 4. See where you stand
iris balance
iris report pl --from 2026-04-01 --to 2026-06-30
```

Your AI can handle document filing; you do not need to move files into `raw/`
yourself. Personal spending can start from a balance and a short interview,
with estimates recorded explicitly; business records need precision and
supporting evidence. See [the everyday workflow](cli-and-llm.md).
Local `iris` needs no account or network; your AI service may need a connection.

## Path B — Use the web app (cloud)

The web app gives you a graphical interface, cloud sync, multi-device access,
collaboration, and the durable server history. It needs an IrisBooks account.

### 1. Sign in

Cloud accounts are invitation-only. Request an invitation through the
[Discord community](https://discord.gg/wZDsv9gyb9), then sign in to the
[web app](https://irisbooks.io/app/) with the invited email address.
If your accountant shared a book, it will already be waiting.

### 2. Create a book

If you already have a local book, choose **Already have an IrisBooks book on your computer?** in
the wizard and follow the linking step below before creating a separate cloud
book. After linking and syncing, use **Refresh book list** in the wizard to open it.

If you have no books yet, the app drops you into the **New book** wizard. Give
the book a name and region, choose the fiscal year it covers, and pick the
month its fiscal year starts (January unless you pick another). It's created in the cloud — already seeded
with its `config/book.yaml`, a starter chart of accounts and `AGENTS.md`, so
`iris clone <book-id>` gives you a working local folder right away.

Region and the fiscal-year start can't be changed once the first journal is
posted. The review step shows the dates your first fiscal
year covers, so check them there.

### 3. Link an existing local book (optional)

Already have a book on disk from Path A? Connect the two so they sync:

```bash
IRISBOOKS_APP_BASE=https://irisbooks.io IRISBOOKS_API_BASE=https://irisbooks.io/api iris api login
iris api books new             # or: iris api books link <book-id>
iris sync                      # push your local files up
```

In PowerShell, set `$env:IRISBOOKS_APP_BASE = 'https://irisbooks.io'` and
`$env:IRISBOOKS_API_BASE = 'https://irisbooks.io/api'` before `iris api login`.
Successful login saves the service selection. Accounts and cloud books are
separate between regional services.

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
own. An IrisBooks account adds sync, the web app, collaboration, and a
durable correction/deletion history kept on the server. See
[Core concepts → Sync](concepts.md#sync-the-three-ways-to-work).

## Next steps

- Understand the moving parts → [Core concepts](concepts.md)
- Do the file-first workflow → [Bookkeeping with the CLI and your own LLM](cli-and-llm.md)
- Learn the GUI → [Using the web app](web-app.md)
- File taxes in Japan → [Japan tax & compliance](japan-tax-and-compliance.md)
