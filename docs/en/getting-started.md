# Getting started

Whether the books are for a household or a business, you begin with book
files and your own AI. The **`iris` CLI** runs on your computer and needs no
account or network. If you use the cloud, the **web app** adds viewing, review
and cloud administration. This page walks through both.

Accountants: copy the book a client shared with you to your own computer
(`iris clone`) and work there; you don't create the book again for each
client. Keep a separate assistant work folder and session for each client. See
[Accountants: use a separate work folder for each client](cli-and-llm.md#accountants-use-a-separate-work-folder-for-each-client).

## Try the sample books

You can look around before you create anything. [The demo](https://irisbooks.io/demo/)
opens made-up books for a shop and its owner's household, in English and
Japanese, in the screens `iris view` shows on your computer, with `iris` itself
running in your browser. It needs no account. You can fix a draft, post it and
watch the reports change. Nothing leaves your browser, and your changes last
until you reload the page. The dates move so that this year's books run to today.

To try the same books with your own AI, choose **Try it on your computer** in
the demo and download the zip, which includes your changes. Its README covers installing `iris` and opening
a book in Claude Code or Codex. With `iris` installed,
`iris view --books-dir <unzipped folder>` opens them on your computer in the
demo's screens, with nothing uploaded. On your computer the household's fund
and coin are valued at cost until you record prices with `iris price add`, so
the net worth you see there differs from the demo's.

## Do I need an account?

Not for bookkeeping itself. The files on your computer and the CLI are
complete on their own, and `iris view` shows them on screen. An IrisBooks
account adds cloud sync, the web app, collaboration, and a correction and
deletion history kept on the server (see
[Core concepts → Sync](concepts.md#sync-the-three-ways-to-work)).

To start without an account, Path A is all you need. To use the cloud as
well, the usual order is to create the book with Path A and then go on to
Path B.

## Path A — Create a book on your computer (CLI)

### 1. Check for `iris`

Run `iris --version`. If it prints a version, `iris` is already installed: use
it, and run `iris update` when you want the latest release. Otherwise install
it as below.

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

The installer downloads the binary for your platform, checks that it matches
the published one, and puts it on your `PATH`. If it doesn't match, nothing
is installed. On a first install on a desktop, it also adds **IrisBooks** to
your apps, so you can open your books without a terminal (see
[the launcher](iris-view.md#the-launcher)); set `IRIS_NO_LAUNCHER=1` to skip
that. Updates never add it. Confirm the installed version with:

```bash
iris --version
```

If `iris` still isn't found, open a new terminal or use the absolute executable
path printed by the installer. Check `PATH` before installing another copy.

> **How the check works.** The installer carries the SHA-256 checksums for the
> current release. Those checksums come from the signed release and are served
> by irisbooks.io, separately from the download host, so a tampered download
> is refused even without `minisign`. To install another version with
> `IRIS_VERSION`, install `minisign` first: the installer then verifies that
> release's signed checksum file, and refuses without it. After installation,
> `iris update` verifies signatures with its built-in verifier and needs no
> external `minisign`.

### 2. Create your first book

Run the guided wizard in an empty folder:

```bash
iris init
```

It asks the questions below in turn, then creates the book folder.

| Question | Default and notes |
| --- | --- |
| Book name | — |
| Region | Required; there is no default |
| Currency | The region's currency |
| Fiscal-year start month | January |
| The fiscal year the book covers | A book is one year. Pick last year's if you're catching up on its filing |
| Should your AI assistant **post entries automatically** after validating? | Say no to review and post them yourself. You can change this later in the "Posting policy" section of `AGENTS.md` |

You can also skip the questions and pass everything as flags:

```bash
iris init --name "Acme Design" --region JP --language en \
  --fiscal-start-month 4 .
```

Add `--sample` to seed ~40 demo entries you can explore and then delete. See
[`iris init`](cli-reference.md#iris-init) for every flag.

You can also make a book without the terminal. Open **IrisBooks** from your
apps and choose **Create a book**. The page asks the same questions on one
form. See [Create a book](iris-view.md#create-a-book).

### 3. Make the book your own

First open `config/chart-of-accounts.yaml` and adjust the accounts to match
your business or household.

Then record your **opening balances** (the cash, bank balances, receivables,
payables and loans you hold when the year starts) as your first journal
entry. Date it the first day of the book's fiscal year and tag it
`opening-balance`. The asset-movements report leaves out entries with this
tag, since a carried balance is not money coming in. The opening entry that
`iris yearend` writes into next year's book gets the same tag automatically.
If you're migrating from another system, the amounts should match that
system's trial balance at the cutover date. `notes/todos.md` lists this task
too.

If you already hold investments or anything else counted in units (fund
units, shares, coins) bought in earlier years, there are two more things to
do:

1. Give each holding its quantity and unit in that opening entry.
2. List what is left of its purchases as lots (original date, quantity and
   cost) under `opening_inventory` in `config/book.yaml`.

The book then keeps the holding's acquisition cost apart from its book value.
Later sales use up the oldest lots first by default, and `iris yearend`
carries the lots still held into the next year's book. The earlier purchases
themselves can't be entries in this book: they fall outside its fiscal year.
See
[acquisition openings](book-format-reference.md#independent-annual-books-and-acquisition-openings).

### 4. Connect your AI assistant

If your assistant can already run commands and read and write this folder, no
further setup is needed. It reads `AGENTS.md`, the working guide at the root
of the book, before it starts. If you use the Claude or ChatGPT desktop app,
the book's **Overview** in `iris view` can start a session in the book's
folder for you. See
[Work on a book with your AI](iris-view.md#work-on-a-book-with-your-ai).

MCP is a way for an AI app to call `iris` directly as a tool. To connect over
MCP, or to add guide files the book is missing, run:

```bash
iris onboard
```

This registers the `iris` MCP server (`iris mcp serve`) with your MCP-capable
apps (Claude Code, Claude Desktop, Codex, Cursor, Gemini CLI, VS Code) and
writes a Claude Code skill that tells your assistant how to work in the book.
See [One-time setup: connect your AI](cli-and-llm.md#one-time-setup-connect-your-ai).

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

Your AI can file the documents; you do not need to move files into `raw/`
yourself. Personal spending can start from a balance and a short interview,
with every estimate marked as an estimate. Business records need exact
amounts and supporting documents. `iris` itself needs no account or network;
your AI service may need a connection.

Each step is described in [The everyday loop](cli-and-llm.md#the-everyday-loop).
What saved documents, drafts and posted entries are each good for is in
[The mental model](cli-and-llm.md#the-mental-model).

### 6. See your books on screen

```bash
iris view
```

This opens the book in a window of its own: reports, journals and documents,
read from your files. Post the drafts your AI prepared, fix one, or start an
entry yourself. It needs no account. To open your books without a terminal,
open **IrisBooks** from your apps and choose the book's folder. If it isn't
there, add it with `iris view --add-launcher`. See
[Your books on this computer](iris-view.md).

## Path B — Use the web app (cloud)

The web app shows your books in the browser and adds cloud sync, access from
several devices, collaboration, and the correction and deletion history kept
on the server. It needs an IrisBooks account.

### 1. Sign in

Cloud accounts are invitation-only. Request an invitation through the
[Discord community](https://discord.gg/wZDsv9gyb9), then sign in to the
[web app](https://irisbooks.io/app/) with the invited email address.
If your accountant invited you to a book, accept the invitation on your
Dashboard to open it.

### 2. Create a book

If you have no books yet, the app opens the **New book** wizard. Fill in the
following and the book is created in the cloud:

- A name for the book.
- Its region. There is no default. Choosing one fills in the region's
  currency, which you can change.
- The fiscal year the book covers.
- The month its fiscal year starts. It is January unless you pick another.

The new book already contains its `config/book.yaml`, a starter chart of
accounts and `AGENTS.md`, so `iris clone <book-id>` gives you a working folder
on your computer right away.

Region and the fiscal-year start can't be changed once the first journal is
posted. The review step shows the dates your first fiscal year covers, so
check them there.

If you already have a book on your computer, from Path A for example, don't
create a new one here. Choose **Already have an IrisBooks book on your
computer?** in the wizard and link that book to the cloud in step 3 below.
After linking and syncing, use **Refresh book list** to open it.

### 3. Link an existing local book (optional)

If you have a book on your computer from Path A, you can tie it to a cloud
book (link it) so the two sync. Run these inside the book folder:

```bash
iris api login                 # sign in
iris api books new             # create the cloud book and link this folder to it
iris sync                      # send the files on your computer to the cloud
```

`iris api books new` creates the cloud book from the folder's own settings
(name, fiscal year, region, …) and links the folder to it. That's why
`iris sync` works straight afterwards.

If you already created the book in the web app, don't run `new`. Run
`iris api books link <book-id>` with the id the app showed you instead;
running `new` would give you a second book.

`iris api login` signs in through a browser, so the computer running the CLI
needs one. Where there is none, such as a server or an assistant's VM, run
`iris api login --device`, approve on your own phone, then run
`iris api login --device-complete`. Either way, check which account you are
signed in to with `iris api whoami` before creating, linking or syncing a
book. See [login modes and account profiles](cli-reference.md#iris-api-login).

Now the same book is reachable from both the CLI and the web app. See
[Core concepts → Sync](concepts.md#sync-the-three-ways-to-work) for
what syncing does and doesn't change.

### 4. Work in the app

Pick a book under **My Books** in the left sidebar and the sidebar lists that
book's screens: Overview, Journals, Activity, the reports, Files, Accounts,
Notes, Year-end and Book settings. Totals across several books are on the
**Dashboard** and **Net Worth**. The gear icon (top right) opens your own
settings. Full walk-through in [Using the web app](web-app.md#layout).

## Next steps

- Understand the moving parts → [Core concepts](concepts.md)
- Do the file-first workflow → [Bookkeeping with the CLI and your own LLM](cli-and-llm.md)
- Review and post on screen → [Your books on this computer](iris-view.md)
- Learn the web app's screens → [Using the web app](web-app.md)
- Close the year and prepare returns → [Records, history and year-end](records-and-year-end.md)
- Your region's tax rules → [Overlays](https://irisbooks.io/docs/en/overlays/)
