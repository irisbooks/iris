> IrisBooks is local-first, double-entry bookkeeping. A book is a folder of
> plain Markdown + YAML files on the user's own machine; the `iris` CLI
> (driven by the user's own AI assistant) and the web app are two lenses over
> the same folder. Each country's tax rules come as a region overlay the book
> pins; Japan is the first region with one.

Key facts for agents:

- Reports (trial balance, P&L, balance sheet) are computed from `posted`
  journal entries only — `draft` entries are drafts and never appear in
  reports.
- Sync is explicit (`iris sync`); nothing uploads in the background. The
  local workflow is fully offline; an IrisBooks account adds sync, the web
  app, collaboration, period seals, and the server-side correction/deletion
  history (for a Japanese book, the 訂正・削除の履歴 that 優良電子帳簿 区分①
  requires).
- Working inside a book folder? Read `LLM-GUIDE.md` at the book root first —
  it is the binding working contract for AI assistants.
- Run `iris validate` after every write. Never invent account paths — add
  accounts to `config/chart-of-accounts.yaml` first. When uncertain, propose
  `status: draft` and file a note in `notes/open-questions.md`.
- Region rules are data, not engine code. What is specific to a country —
  how a line's tax is classified, depreciation methods and their limits, a
  tax return's figures — comes from the region overlay for the book's
  `region`, pinned in `config/book.yaml` (`overlay: jp@…` for Japan). The
  overlays are open source, one per region, at
  https://github.com/irisbooks/overlays. Run a recipe (`iris overlay recipe`,
  or the matching MCP tool) rather than computing those figures yourself;
  change the pin only with `iris overlay upgrade`, and only when the user
  asks. A region without an overlay yet gets the universal checks only —
  don't invent its rules.
