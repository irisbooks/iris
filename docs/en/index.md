# IrisBooks User Manual

IrisBooks is local-first, double-entry bookkeeping built for Japan. Your
books are a **folder of plain Markdown and YAML files** on your own machine —
not rows in someone else's database. You work with them through two lenses:

- the **`iris` command-line tool** driven by your own AI assistant (Claude,
  Cursor, Copilot, …), and
- the **web app**, a first-party interface for browsing, editing, reporting,
  and collaborating.

Both read and write the same folder. Nothing is locked in a proprietary
format — zip the folder and hand it to your accountant, sync it between
machines, or keep it entirely offline.

> **New here?** Read [Getting started](getting-started.md) first, then
> [Core concepts](concepts.md). Everything else is reference you can return to.

## Who this manual is for

- **Business owners** — freelancers, sole proprietors (個人事業主), and SMBs
  who keep their own books and file 青色申告 / 確定申告. Start with the CLI +
  your own AI ([Bookkeeping with the CLI and your own LLM](cli-and-llm.md)),
  add the web app if you're on a paid plan.
- **Accountants / 税理士** — firms managing many client books. The
  [web app](web-app.md) is your primary surface; the CLI and access tokens
  let you script across clients.

## Table of contents

1. [Getting started](getting-started.md) — install, create your first book,
   record your first entry.
2. [Core concepts](concepts.md) — books, journals, accounts, status,
   reports, sync, seals, plans.
3. [Bookkeeping with the CLI and your own LLM](cli-and-llm.md) — the
   file-first workflow (free plan).
4. [Using the web app](web-app.md) — journals, reports, raw documents,
   activity, settings, collaboration (paid plans).
5. [Receipts by email](email-inbox.md) — your book's receiving address,
   the sender allowlist, and the quarantine.
6. [Your AI on the go (remote connector)](remote-connector.md) — figures,
   drafts, and receipts from your phone (paid plans).
7. [Japan tax & compliance](japan-tax-and-compliance.md) — 優良電子帳簿,
   consumption tax (消費税), fixed assets & depreciation, year-end close.
8. [CLI command reference](cli-reference.md) — every command and flag.
9. [Book file-format reference](book-format-reference.md) — the on-disk
   structure of a book.
10. [Troubleshooting](troubleshooting.md) — validation errors, sync
    rejections, conflicts.

## A 60-second picture

```text
your-book/
├── config/        # book settings + your chart of accounts
├── raw/           # drop bank CSVs, receipts, invoices here
├── journals/      # double-entry entries, one Markdown file each
├── notes/         # working notes shared with your AI and accountant
└── compiled/      # AI-generated reports (regeneratable)
```

You (or your AI) drop a bank statement into `raw/`, the AI proposes journal
entries, you review them, `iris validate` checks the math, and `iris balance`
shows your trial balance. On a paid plan, `iris sync` mirrors everything to
the cloud where the web app, your accountant, and timestamped history live.
