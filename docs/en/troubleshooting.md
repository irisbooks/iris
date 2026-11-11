# Troubleshooting

Common situations and how to clear them. When in doubt, run `iris validate` —
it's the fastest way to learn what's wrong.

## `iris validate` reports errors

`iris validate` checks every file and prints what's wrong. The usual causes:

- **Unbalanced entry** — debits don't equal credits. Fix the amounts so they
  sum to the same total.
- **Unknown account** — a journal references an account not in
  `config/chart-of-accounts.yaml`. Add the account to the chart (or use an
  alias). Don't invent account paths inside the journal.
- **Date mismatch** — the `date:` field doesn't match the `YYYY-MM-DD` prefix
  of the filename. Make them agree.
- **Bad status** — `status` must be `draft` or `posted`.
- **YAML won't parse** — usually indentation or a stray colon in the
  frontmatter. The error names the file.
- **Overlay rules** — a check from a package your book selected, such as a
  field with a value the package doesn't accept. The message names the rule;
  the package's docs under [Overlays](https://irisbooks.io/docs/en/overlays/) explain its fields.

Fix and re-run. Your AI assistant can do this loop for you.

## "I posted an entry but it's not in my reports"

Reports include **only `posted`** entries. If a transaction is missing from
`iris balance`, the P&L, or the balance sheet, its status is almost certainly
still `draft`. Promote it:

```bash
iris post journals/2026-05/2026-05-04-example-com-01.md
```

…or edit the `status:` field to `posted` and re-validate.

## "iris: command not found"

The shell cannot find `iris` on its current `PATH`. Check which machine or VM
the shell uses, open a new terminal after installation, or try the absolute
executable path reported by the installer. Run `iris version` on that copy.
Install only if the tool is actually missing; see [getting started](getting-started.md).
A sandboxed assistant may instead use a reachable host MCP server; verify
`check_update` there. A Book contains no bundled CLI executable.

## Sync rejections (needs-attention)

`iris validate` checks *file* state, but the server runs additional rules when
you push (chart-projection orphans, a journal referencing a `raw/` file that
isn't uploaded, schema/immutability violations). When the server rejects a
push, `iris validate` may end with a note like *"N file(s) blocked in the sync
queue"* — the files are fine, the *push* was rejected.

To clear it:

```bash
iris sync issues list      # read the field-level reason
```

Then fix the cause — usually:

- add the missing account to `config/chart-of-accounts.yaml`, or
- make sure the referenced `raw/...` document is actually present and synced.

Then **re-save the rejected journal**. Its content hash changes, the engine
drops the per-file suppression, and the push goes out automatically on the next
sync.

If your fix was in a *different* file (e.g. you fixed the chart days ago and
won't touch the journal again), nudge the engine instead:

```bash
iris sync issues retry            # re-push everything in the queue
iris sync issues retry --path <relpath>   # just one file
```

## Capacity limits (`CAPACITY_EXCEEDED`)

This is a capacity limit, not a transient failure. Repeating the same request
will not resolve it. Read the named operation and limit. For a report or
search, narrow the date range or filters when possible. Chart replacement
must fit within 1,500 accounts in one atomic update; keep accounts referenced
by journals. If the operation cannot be reduced safely, seek support from the [Discord community](https://discord.gg/wZDsv9gyb9).

## Sync conflicts

If you and someone else (or you on another device) changed the same file, a
push can conflict. The **server version takes the canonical path**, and your
version is saved beside it as a `<file>.conflicted` sidecar. `iris sync`
refuses to proceed while any sidecar exists, so nothing is lost.

```bash
iris conflicts list
```

Resolve each one. The usual way is to **merge by hand**: open the canonical
file, fold in whatever you need from the `.conflicted` sidecar, delete the
sidecar, and run `iris sync` again. To take one side wholesale instead:

```bash
iris conflicts resolve <path> --keep mine     # replace canonical with your version
iris conflicts resolve <path> --keep cloud    # discard your version
```

## `iris sync` exits with code 3

Exit code `3` means a **terminal disconnect**. The summary (and the
`disconnectReason` field of `iris sync --json`) says which kind:

- **deleted** — the owner deleted the book on the server (web app →
  the book's Settings → Danger zone). **Your local files are intact** — nothing was
  removed from your folder, and `iris status` shows
  `Remote: deleted on the server`. To keep working locally, edit
  `config/book.yaml` and set `book_id` back to your local id (`iris status`
  prints it). To reconnect to the cloud, create a new book
  (`iris api books new --no-link` — the folder still points at the deleted id,
  so plain `new` refuses) and link it (`iris api books link --force <id>`).
- **forbidden** — your access was revoked, or you left the book (your
  credential is valid but you no longer hold a grant). Ask the book's owner
  to re-invite you, then accept the invitation in the web app. If access was
  intentionally revoked, that's expected.
- **auth_expired** — your session is gone. Re-authenticate
  (`iris api login`) and run `iris sync` again.

## A cloud command reports a network error

When a request to the server fails, the message names the request, what went
wrong, and whether trying again can help:

```text
iris api login: device authorization request failed: POST https://irisbooks.io/api/cli-auth/device/start: no HTTP response within 45s (timeout; retryable): context deadline exceeded (Client.Timeout exceeded while awaiting headers)
```

The parentheses hold the kind of failure and whether a retry may succeed:

- **timeout**, **connect** — no answer arrived. This is usually a passing
  network problem: run the same command again. If it keeps failing, check your
  connection.
- **dns** — the server's name did not resolve. `not retryable` means the name
  does not exist: check the address in the message and your DNS settings.
- **tls** — the secure connection could not be verified. This usually happens
  on a network that inspects traffic; ask its administrator to allow the
  address in the message.
- **proxy** — your proxy failed or refused the address. `not retryable` means
  the proxy blocks it: add the address to the proxy's allowlist.
- **HTTP** followed by a status — the server answered. `retryable` statuses
  (408, 429, 500, 502, 503, 504) are temporary, so try again shortly. Any other
  status repeats until the request changes; read the text after it.

When no answer arrived, the message also says how far the request got and
when it failed, for example `while connecting, after 30.0s`. Stuck while
resolving the host name or connecting points to your network or a proxy;
waiting for the response points to the service, so try again shortly.

If `iris api login --device-complete` gets no answer, the pending login is
kept, so run the same command again. `iris sync --json` reports the same facts
in its `errorDetail` field.

## "I need to change a sealed year"

A sealed fiscal year is **locked**: `iris post` refuses journals dated in it
("FY \<n\> is sealed (closed period) — run `iris reopen <n>` to amend it, then
re-seal"). The server also rejects changes to those journals and to `config/`,
`assets/`, `filings/`, `compiled/` until reopening. `raw/` and `notes/` remain
writable. Local files remain editable, but locked changes cannot sync.
To amend the accounting records, reopen the year first:

```bash
iris reopen 2025      # unlocks the seal; the files are already in the working tree
# …make the correction…
iris sync
iris seal 2025        # close the year again
```

The server records the corrections as **post-seal edits** — visible in the
Activity log and badged in the web app. That's by design: the correction is
allowed and auditable, not hidden. Re-sealing supersedes the old seal in the
audit chain.

**Changing an entry's date is changing the year it belongs to.** If an entry
currently sits in a sealed year, re-dating it into an open year is refused
too — the rejection names the *sealed* year, not the new one. Moving an
amount out of a closed year changes that year's totals just as much as
editing it in place would. Reopen the sealed year first, then re-date.

## "The web app shows different numbers than my CLI"

Almost always a sync gap or a status difference:

- Run `iris diff` to see local changes you haven't pushed, then `iris sync`.
- Remember the web app, like the CLI, reports only `posted` entries — a draft
  you see locally won't appear until it's posted and synced.
- Reports in the web app show a "freshness" note for when the server last
  recomputed; give a recent push a moment to project.

## `iris view` doesn't open, or says it has closed

- **"This view has closed. Open IrisBooks again."** The page stops when no
  window has used it for a few minutes, for example after its windows closed or
  while the computer slept. Run `iris view` again or open IrisBooks from the
  launcher.
- **It opened in a browser tab, not a window of its own.** `iris` found neither
  Chrome nor Edge. A Chromium installed as a snap on Linux also gets a tab.
  Everything works the same, but extensions in that browser stay on.
- **The launcher does nothing.** It runs the `iris` that added it. If you moved
  `iris`, run `iris view --add-launcher` again. On a Mac the reason appears in
  an alert.
- **Your AI ran `iris view`, but no window appeared.** If your assistant works
  in a VM or container, the window opened there, not on your screen. Open
  IrisBooks from your launcher, or run `iris view` yourself.
- **The Dashboard asks for a reporting currency.** The folder's books use
  different currencies. Set one as described in
  [Prices and currencies](iris-view.md#prices-and-currencies).
- **A notice names a book it couldn't read.** Run `iris validate` in that book
  to see why. If it names two folders as copies of the same book, only the
  first is shown; keep one copy in the folder.
- **Posting or saving says a sync is running.** A sync, or a save from another
  window, is using the book at that moment. Try again.

## Still stuck?

- Re-read [Core concepts](concepts.md) — most confusion is about `status`
  (drafts vs posted) or what sync does.
- Check the in-book `notes/open-questions.md` — your AI files ambiguous items
  there.
- For your region's tax rules, see its guide under [Overlays](https://irisbooks.io/docs/en/overlays/);
  your AI verifies volatile values (rates, tables, form layouts) against the
  tax authority's current pages.
