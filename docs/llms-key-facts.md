> IrisBooks is local-first, double-entry bookkeeping built for Japan. A book
> is a folder of plain Markdown + YAML files on the user's own machine; the
> `iris` CLI (driven by the user's own AI assistant) and the web app are two
> lenses over the same folder.

Key facts for agents:

- Reports (trial balance, P&L, balance sheet) are computed from `posted`
  journal entries only — `draft` entries are drafts and never appear in
  reports.
- Sync is explicit (`iris sync`); nothing uploads in the background. The
  local workflow is fully offline; an IrisBooks account adds sync, the web
  app, collaboration, period seals, and the server-side correction/deletion
  history (訂正・削除の履歴) required for 優良電子帳簿 区分①.
- Working inside a book folder? Read `LLM-GUIDE.md` at the book root first —
  it is the binding working contract for AI assistants.
- Run `iris validate` after every write. Never invent account paths — add
  accounts to `config/chart-of-accounts.yaml` first. When uncertain, propose
  `status: draft` and file a note in `notes/open-questions.md`.
