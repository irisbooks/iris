# Your AI on the go (remote connector)

Your books live on your computer — but with cloud sync the cloud keeps a
synced copy, and the **remote connector** lets an AI app reach that copy when
you're away from your machine: ask for figures from your phone, or capture an
expense as a draft the moment it happens.

The connector speaks MCP (Model Context Protocol), the same standard your
local setup uses. It works with **Claude** (mobile, web, desktop, and Claude
Code) and **ChatGPT**.

Other MCP-capable apps aren't supported yet. An AI app has to identify itself
in the way the current MCP specification asks for, and IrisBooks only accepts
apps whose identity it recognises — so if your app can't complete the
sign-in, that is usually why, rather than anything wrong with your account.

## Set it up

1. In your AI app, add a custom connector with this URL:

   ```text
   https://irisbooks.jp/mcp
   ```

   (In Claude: Settings → Connectors → Add custom connector.)
2. Your browser opens the IrisBooks sign-in and asks what to allow:
   - **Bookkeeper** (default) — the AI can read your books and create
     *draft* entries.
   - **Viewer** — read-only: reports and browsing, no drafting.
3. Approve, and the connector is live in that AI app — including on your
   phone if the app syncs connectors across devices.

Your per-book roles still apply on top: even a Bookkeeper connection can't
draft into a book where you are only a Reviewer.

## What you can do from anywhere

- **Ask for figures** — trial balance, P&L, balance sheet, monthly cashflow.
  Numbers come from the cloud copy and include posted entries only; the AI is
  told when they were last synced from your machine and will say so.
- **Browse and search entries** — by date, payee, amount, status.
- **Check the fiscal years** — which years exist, which are closed or
  reopened, and how many drafts still block a year's close. (Closing and
  reopening themselves stay in the web app's Year-end screen and the CLI.)
- **Capture expenses as drafts** — "I just paid ¥3,400 for a taxi" becomes a
  `draft`-status draft with proper accounts and balanced lines. It appears
  in your local book folder at your next `iris sync`, ready for review.
- **Send in the receipt** — the AI can mint a **one-time upload link** (works
  once, expires in 15 minutes, images/PDF up to 10 MB). The file is scanned,
  lands in `raw/uploads/`, and attaches itself to the draft. The upload page
  waits for that to finish and shows **"the document is in your book"** —
  that message, not the upload itself, is your receipt's proof of arrival
  (it usually takes under a minute). If scanning is slow the page says so
  honestly; you can close it and reopen the same link later to check, and if
  the file is rejected (for example by the malware scan) the page tells you
  instead of pretending it worked. If the document is already in your email,
  the AI hands you the book's [receiving address](email-inbox.md) instead.

## What it deliberately can't do

The connector **drafts, it never posts**. It cannot:

- post or approve entries,
- edit or delete anything that's `posted` or `closed`,
- draft into a sealed fiscal year — a sealed year refuses all writes until
  the owner reopens it (its entries show as `closed` when browsing),
- seal or reopen a fiscal year.

Review stays where it belongs — at your computer or in the web app, with the
full validate → post loop. Every remote-drafted entry is labeled in the audit
history, so you (and your accountant) can always see which entries arrived
from a phone.

## At the computer or on the go?

| You are… | Use | Why |
| --- | --- | --- |
| At your computer | the [local setup](cli-and-llm.md) | sees unsynced edits; full loop: author → validate → post → sync |
| Away from it | the remote connector | cloud copy; figures, drafts, and receipts from anywhere |

You don't have to choose — set up both. An AI app that can see both (e.g.
Claude Desktop) knows to prefer the local one when it's available.

## Disconnecting

Two ways; either works:

- **In your AI app** — remove the connector in the app's settings; the app
  tells IrisBooks to revoke its access.
- **In the web app** — your Settings (avatar menu) → Connected apps lists every AI app you have
  connected, with its access level and when it was last used. **Disconnect**
  revokes its access server-side — useful when you no longer have the device
  or app at hand.

Revocation takes effect within a few minutes. A collaborator's underlying
book role is separate — owners can change or revoke it any time in the
book's Settings → Grants.
