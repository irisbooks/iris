# IrisBooks Docs

IrisBooks helps you keep books with your own AI assistant.

- Use the **`iris` command-line tool** with your AI to record and check entries.
- Use the **web app** to browse synced books, review entries, and read reports.

Your book is a folder of Markdown and YAML files. The CLI works without an
account; optional cloud sync adds web access and collaboration.

> **New here?** Read [Getting started](getting-started.md) first, then
> [Core concepts](concepts.md). Everything else is reference you can return to.

## Who this manual is for

- **Personal tracking** — understand everyday spending and balances without
  keeping every receipt. Start with a cash check-in or a statement and let
  your AI help at a level of detail you can maintain.
- **Business owners** — freelancers, sole proprietors (個人事業主), and SMBs
  who keep their own books and file 青色申告 / 確定申告. Start with the CLI +
  your own AI ([Bookkeeping with the CLI and your own LLM](cli-and-llm.md)),
  add the web app if you use the cloud.
- **Accountants / 税理士** — firms managing many client books. The
  [file workflow with your own AI](cli-and-llm.md) is for you too. Use a
  separate assistant work folder/session for each client; the
  [web app](web-app.md) supports viewing and review.

## Table of contents

1. [Getting started](getting-started.md) — install, create your first book,
   record your first entry.
2. [Core concepts](concepts.md) — books, journals, accounts, status,
   reports, sync, seals.
3. [Bookkeeping with the CLI and your own LLM](cli-and-llm.md) — the
   file-first workflow (fully offline).
4. [Using the web app](web-app.md) — journals, reports, raw documents,
   activity, settings, collaboration (cloud).
5. [Receipts by email](email-inbox.md) — your book's receiving address,
   the sender allowlist, and the quarantine.
6. [Your AI on the go (remote connector)](remote-connector.md) — figures,
   drafts, and receipts from your phone (cloud).
7. [Japan tax & compliance](japan-tax-and-compliance.md) — correction
   history and search, consumption tax (消費税), fixed assets & depreciation,
   year-end close.
8. [CLI command reference](cli-reference.md) — every command and flag.
9. [Book file-format reference](book-format-reference.md) — the on-disk
   structure of a book.
10. [Troubleshooting](troubleshooting.md) — validation errors, sync
    rejections, conflicts.

## A 60-second picture

```text
your-book/
├── config/        # book settings + your chart of accounts
├── raw/           # original documents, filed by you or your AI
├── journals/      # double-entry entries, one Markdown file each
├── notes/         # working notes shared with your AI and accountant
└── compiled/      # AI-generated reports (regeneratable)
```

Share a statement or tell your AI what happened. It files available originals
under `raw/`, reasons about entries and explains its proposal. `iris validate`
checks the work; after posting under your chosen policy, `iris balance` shows
the results. Notes preserve context for another session or assistant. Optional
`iris sync` mirrors book records to the cloud for the web app, collaboration
and server-side change history.
