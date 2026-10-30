# IrisBooks documentation mirror

> **Generated — do not edit here.** This subtree is mirrored from the private
> IrisBooks monorepo by `publish-docs.sh`; any change made directly in this
> repository is overwritten on the next publish.

| File | What it is | Canonical live URL |
|---|---|---|
| [`llm.md`](llm.md) | The English manual in one file for AI assistants, including their agent-only guidance | <https://irisbooks.io/llms-full.txt> |
| [`llms-key-facts.md`](llms-key-facts.md) | The overview + key-facts block spliced into the `llms.txt` index | <https://irisbooks.io/llms.txt> |
| [`en/`](en/) · [`ja/`](ja/) | The user manual (English / Japanese) | <https://irisbooks.io/docs/> |

The region overlays a book pins by `overlay:` (YAML + CEL rules, recipes,
derivations) are open source in <https://github.com/irisbooks/overlays>.

Docs are mirrored before each release is published, so a release tag pins the
documentation that shipped with that binary:
`https://raw.githubusercontent.com/irisbooks/iris/<tag>/docs/llm.md`.
