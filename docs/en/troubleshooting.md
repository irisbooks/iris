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
- **Tax classification** (JP taxable books) — a `tax` block with an unknown
  category, or a rate that doesn't match its category (e.g. a `taxable_sale`
  with no rate, or an `export_sale` with a non-zero rate).

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

The `iris` binary isn't on this machine's `PATH` yet. Install it
(`curl -fsSL https://irisbooks.jp/install.sh | sh` on macOS/Linux,
`irm https://irisbooks.jp/install.ps1 | iex` on Windows PowerShell), then check
with `iris version`. If you're working in a sandboxed AI environment, there is
**no** copy bundled inside the book — the host runs `iris mcp serve` and your
assistant calls the verbs over MCP instead.

## Sync rejections (needs-attention)

`iris validate` checks *file* state, but the server runs additional rules when
you push (chart-projection orphans, a journal referencing a `raw/` file that
isn't uploaded, schema/immutability violations). When the server rejects a
push, `iris validate` may end with a note like *"N file(s) blocked in the sync
queue"* — the files are fine, the *push* was rejected.

To clear it:

```bash
iris attention list      # read the field-level reason
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
iris attention retry            # re-push everything in the queue
iris attention retry --path <relpath>   # just one file
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
- **forbidden** — your access was revoked (your credential is valid but you
  no longer hold a grant). Ask the book's owner to re-invite you. If access
  was intentionally revoked, that's expected.
- **auth_expired** — your session is gone. Re-authenticate
  (`iris api login`) and run `iris sync` again.

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
iris api seal --period 2025 <book-id>   # close the year again
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

## Still stuck?

- Re-read [Core concepts](concepts.md) — most confusion is about `status`
  (drafts vs posted) or what sync does.
- Check the in-book `notes/open-questions.md` — your AI files ambiguous items
  there.
- For Japan tax specifics, see
  [Japan tax & compliance](japan-tax-and-compliance.md); your AI verifies
  volatile values (rates, tables, form layouts) against the NTA's current
  pages.
