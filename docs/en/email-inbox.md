# Receipts by email

Every cloud book has a private receiving address. Email a receipt or invoice
to it — or set up a forwarding rule from your own mailbox — and the message
is decoded and filed into your book automatically. It's the fastest way to
get supplier invoices, online-purchase receipts, and bank notifications into
`raw/` without touching a scanner or the CLI.

## Your book's receiving address

The address is generated when the book is created and never changes. Show it
with:

```bash
iris api inbox show <book-id>
```

It looks like `k7f3x9q2m4p8w1r5@in.irisbooks.jp` — random on purpose, so it
can't be guessed and spammed. Treat it like a semi-secret: share it with the
suppliers and services whose mail you want in the book.

## What gets accepted

A message is only ingested when **all** of these hold:

1. **The sender is on the book's allowlist** (see below).
2. **The sending server checks out** — SPF, DKIM, and DMARC must all pass,
   so a spoofed "From:" can't inject files into your book.
3. **The virus scan is clean** — every message is scanned (GuardDuty malware
   protection) before it's allowed anywhere near your book.

Everything else lands in the quarantine list instead — nothing is silently
dropped.

## What lands in the book

Each accepted message becomes one folder under `raw/email/`, named by month
and message id:

```
raw/email/2026-07/a1b2c3d4e5f6g7h8/
├── email.md          # from, to, date, subject + the message text
├── receipt.pdf       # attachments, decoded and ready to reference
└── invoice-0042.pdf
```

`email.md` carries the envelope (sender, date, subject, attachment list) as
frontmatter, so your LLM can read the context and journal the attachments
with a `source_ref` pointing at the exact file (see
[Core concepts](concepts.md)). The files arrive locally on your next
`iris sync`, like any other server-side change.

Attachments over 10MB are skipped (noted in `email.md`); the original
message is retained server-side as the audit copy.

## Managing the sender allowlist

The allowlist starts with your own login email, so forwarding from your own
mailbox works out of the box. Add senders as exact addresses or whole
domains:

```bash
iris api inbox allow billing@stripe.com <book-id>   # exact sender
iris api inbox allow '*@amazon.co.jp' <book-id>     # any sender at a domain
iris api inbox disallow '*@amazon.co.jp' <book-id>  # remove again
```

Adding and removing require write access to the book (OWNER or BOOKKEEPER).
Full flag listings are in the [CLI command reference](cli-reference.md).
On a paid plan you can also manage the address and allowlist in the
[web app](web-app.md), under **Settings → Inbound email**.

## Reviewing quarantined mail

Rejected messages are listed with the reason — in the web app under
**Settings → Inbound email** (where a quarantined sender can be allowed
with one click), or from the CLI:

```bash
iris api inbox quarantine <book-id>
```

| Reason | Meaning |
| --- | --- |
| `sender_not_allowlisted` | Sender matched no allowlist pattern. Allowlist it and re-send. |
| `auth_fail` | SPF/DKIM/DMARC verification failed — possibly spoofed, or mangled by an auto-forwarding rule. |
| `malware` | The virus scan found a threat. The message never touched your book. |
| `scan_failed` | The scan could not complete (e.g. password-protected archive). |
| `ingest_failed` | The message passed the gate but writing to the book failed. |

One caveat: **automatic** forwarding rules (e.g. a rule in a corporate
mailbox that re-sends mail as the original sender) often break SPF, so those
messages quarantine as `auth_fail` even when the sender is allowlisted.
Forwarding manually from your own mail client works, because then the mail
is authenticated as coming from you.
