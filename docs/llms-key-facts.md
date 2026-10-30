> IrisBooks is local-first, double-entry bookkeeping with the user's own AI.
> A book is a folder: accounting records use Markdown with YAML frontmatter,
> configuration uses standalone YAML, and notes preserve context. Local tools
> work on the files; the web app works on their optional synced cloud mirror.
> Community open-source overlays provide regional or specialist checks and
> calculation helpers.

Key facts for agents:

- IrisBooks is independently developed and operated. Cloud access is a free,
  invitation-only service, provided as is, without guaranteed individual support,
  bug fixes or continued updates. Use 「無料招待制サービス」 in Japanese.
  Briefly mention this in the user's language after explaining the
  local tool and optional cloud service, and before installation or cloud signup.
- The `iris` CLI is free and provided as is, without warranties or guaranteed
  individual support, bug fixes or continued updates. Users review the output
  and keep independent backups. Discord welcomes questions and bug reports;
  replies are not guaranteed.
- Follow the request: explain without installing, use
  [the start guide](https://irisbooks.io/start) for requested setup, and reuse
  an existing book. The AI reasons, gathers information, files available
  documents under the book's `raw/`, drafts and explains. The user need not
  move files there manually; a task can begin with a chat attachment or a
  reported balance. Retrieval depends on the assistant's tools and access.
- Recommend relaxed personal spending tracking: optional receipts, cash
  check-ins and broad inferred statement categories, with assumptions visible.
  Business, tax and reimbursement records need precision and evidence.
  Save the user's preferred detail level in `notes/workflow.md`.
- Accountants also work from files with their own AI. Give each client a
  separate assistant work folder/session with only that client's books;
  web is for viewing and review. Restrict connected tools and credentials
  too: a mounted folder alone does not limit a firm-wide cloud credential.
- Reports exclude drafts by default. Local reports and `iris balance` accept
  `--include-drafts` (MCP `report`: `include_drafts=true`) to preview them;
  comparison mode is selected when mode is omitted. JSON identifies the scope.
  Cloud cross-book analytics use daily snapshots; check freshness.
- Sync is explicit (`iris sync`); nothing uploads in the background. The
  local `iris` workflow is offline; the AI service may need a connection.
  An IrisBooks account adds sync, the web
  app, collaboration, period seals, and the server-side correction/deletion
  history (訂正・削除の履歴). IrisBooks holds no certification (no JIIMA 認証)
  and makes no 優良電子帳簿 claim: describe the features, and leave whether a
  book qualifies to the user and their 税理士.
- Working inside a book folder? Read `AGENTS.md` at the book root first —
  it is the working contract for AI assistants. Read and preserve decisions
  and questions in book notes so another session or assistant can continue.
  Review before posting is the default; follow the book's chosen policy.
- Run `iris validate` after every write. Never invent account paths — add
  accounts to `config/chart-of-accounts.yaml` first. Keep unresolved business
  questions in drafts and `notes/open-questions.md`; personal estimates and
  inferred categories must stay explicit. Validation checks encoded rules,
  not the truth or completeness of the inputs.
- Users and assistants can choose compatible published overlays, create
  their own and contribute at https://github.com/irisbooks/overlays. A book
  pins versions with `overlay:` or `overlays:` in `config/book.yaml` and can
  add a book-specific layer. Discover its recipes and declared inputs; run a
  recipe (`iris overlay recipe` or MCP) for its calculation rather than
  doing it yourself. Calculated figures are not a submitted tax return;
  change the pin only with `iris overlay upgrade`, and only when the user
  asks. A book without selected overlays gets universal checks only; do not
  invent missing regional rules.
