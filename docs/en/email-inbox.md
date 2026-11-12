# Receipts by email

Every cloud book has a private receiving address. Email a receipt or invoice
to it, or forward one from your own mailbox, and the message text and its
attachments are saved into your book's `raw/` automatically. It gets supplier
invoices, online-purchase receipts, and bank notifications into the book
without a scanner or the CLI. Automatic forwarding rules, such as one in a
corporate mailbox, are often quarantined; read the note under
[Reviewing quarantined mail](#reviewing-quarantined-mail) before you set one
up.

## Your book's receiving address

The address is generated when the book is created. It follows your business
from year to year: when [`iris yearend`](cli-reference.md#iris-yearend) starts
next year's book, the address moves to the new book (and the old book gets a
fresh one), so vendors keep one address. Show it with:

```bash
iris api inbox show <book-id>
```

It looks like `k7f3x9q2m4p8w1r5@in.irisbooks.io` — random on purpose, so it
can't be guessed and spammed. Don't publish it; give it only to the
suppliers and services whose mail you want in the book.

## What gets accepted

A message is only ingested when **all** of these hold:

1. **The sender is on the book's allowlist** (see below).
2. **The sending server checks out** — the three checks that a sender is
   genuine (SPF, DKIM, and DMARC) must all pass, so a message with a forged
   "From:" never enters your book.
3. **The virus scan is clean** — every message is scanned (GuardDuty malware
   protection) before it is saved to your book.

A message that fails any of these goes to the quarantine list. Nothing is
dropped without a record.

## What lands in the book

Each accepted message becomes one folder under `raw/email/`, named by month
and message id:

```
raw/email/2026-07/a1b2c3d4e5f6g7h8/
├── email.md          # from, to, date, subject + the message text
├── receipt.pdf       # attachments, decoded and ready to reference
└── invoice-0042.pdf
```

`email.md` starts with the sender, date, subject and list of attachments, so
your AI can read the context and write a journal that cites an attachment as
its source document (the journal's `attachments` entry has a `path` that
points at the file; see [Core concepts](concepts.md)). The files are saved to
the cloud first and reach your folder on your next `iris sync`.

An attachment over 10MB is not saved, and `email.md` says so. The original
message is kept on the server as the audit copy.

## Managing the sender allowlist

The allowlist starts with your own login email, so forwarding from your own
mailbox works out of the box. Add senders as exact addresses or whole
domains:

```bash
iris api inbox allow billing@stripe.com <book-id>   # exact sender
iris api inbox allow '*@amazon.co.jp' <book-id>     # any sender at a domain
iris api inbox disallow '*@amazon.co.jp' <book-id>  # remove again
```

Only the book's owner and bookkeepers can add or remove senders. Full flag
listings are in the [CLI command reference](cli-reference.md). You can also
see the address and manage the allowlist in the [web app](web-app.md), under
the book's **Settings → Inbound email**.

## Reviewing quarantined mail

Rejected messages are listed with the reason — in the web app under the
book's **Settings → Inbound email** (where a quarantined sender can be
allowed with one click), or from the CLI:

```bash
iris api inbox quarantine <book-id>
```

| Reason | Meaning |
| --- | --- |
| `sender_not_allowlisted` | The sender is not on the allowlist. Add it and have the message sent again. |
| `auth_fail` | SPF/DKIM/DMARC verification failed — possibly spoofed, or mangled by an auto-forwarding rule. |
| `malware` | The virus scan found a threat. The message was not saved to your book. |
| `scan_failed` | The scan could not complete (e.g. password-protected archive). Remove the password and send it again. |
| `ingest_failed` | The message met all three conditions, but saving it to the book failed. Send it again. |

Take care with **automatic** forwarding rules. A rule that re-sends mail as
the original sender, as corporate mailboxes often do, usually fails the
sending-server checks, so those messages are quarantined as `auth_fail` even
when the sender is on the allowlist. Forwarding a message by hand from your
own mail client works, because the mail is then checked as coming from you.
