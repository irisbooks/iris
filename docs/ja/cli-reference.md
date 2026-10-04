# CLI コマンドリファレンス

`iris` の全コマンドを目的別にまとめます。CLI には2つの作業面があります。

- **ファイルモードのコマンド**はローカルの帳簿フォルダに対して動きます。パス引数を
  省略すると、カレントディレクトリから上にたどって帳簿を探すため、帳簿ツリーの
  どこからでも実行できます。
- **クラウドコマンド**（`iris api …`）は IrisBooks サーバーと通信し、パスではなく
  **帳簿 ID** に対して動きます。サインイン（`iris api login`）するか
  `IRIS_API_TOKEN` を設定しておく必要があります。

各コマンドの最新かつ正式なフラグは `iris <command> -h` で確認できます。`iris -h`
で全体、`iris api -h` でクラウドのサブコマンドを一覧します。

JSON を出すコマンドには共通の約束があります。**金額は帳簿通貨のマイナー単位の
整数**（scale 0 なら ¥1,200 は `1200`、scale 2 なら $12.00 が `1200`）、日付は
`YYYY-MM-DD` の文字列、出力は2スペースインデントで整形されます。以下の出力形は
キーの骨組みで書いてあり、`?` は値が空のとき省略されるキーです。

## セットアップ

### iris update

```bash
iris update --check [--json]   # 最新の公開版と比較する（変更なし）
iris update [--json]           # 署名・チェックサム・バージョンを検証して更新する
```

使用中の実行ファイルを更新します。シンボリックリンクは実体の場所を使うため、
MCP の登録先は変わりません。JSON には `currentVersion`、`latestVersion`、`status`、
`updateAvailable`、`executablePath`、`pathExecutable`、`pathMismatch`、`installKind`、
`downloadURL`、`updateCommand`（コマンドと引数の配列）、`instructions`、`updated`、
`restartRequired`、失敗時の `error` が含まれます。確認に失敗した場合や開発版・
リリース候補では、`updateAvailable` は null です。`status` は `update_available`、
`up_to_date`、`newer_than_latest`、`development`、`check_failed`、`updated` のいずれかです。
終了コードは正常時が 0、失敗時が 1、引数の誤りが 2 です。更新不要の場合も 0 です。

帳簿の操作中に自動で通信することはありません。`IRIS_DL_BASE` でダウンロード元を
指定できます（既定は `https://irisbooks.jp/dl`）。署名は組み込みの公開鍵で必ず検証し、
`minisign` のインストールは不要です。検証に失敗した場合、古い実行ファイルは残ります。
開発版の置き換えや、古いバージョンへの更新は自動では行いません。

`.mcpb` の場合、確認結果に対応するバンドルの URL が表示されます。クライアントの
拡張設定から入れ直してください。CLI の更新後は帳簿のフォルダーで `iris onboard` を
再実行し、MCP を再起動します。`check_update` で AI が使うバージョンを確認してください。
Windows で使用中のファイルを置き換えられない場合は、MCP サーバーを停止して再実行します。
このコマンドがない古い版は、まずインストーラーで更新します。

### iris init

新しい帳簿を作ります。引数なしの `iris init` はガイド付きウィザード、フラグ指定で
質問を飛ばせます。

```bash
iris init [flags] [path]
```

| フラグ | 意味 |
| --- | --- |
| `--name` | 帳簿の表示名 |
| `--region` | 地域コード（JP, US。既定 JP） |
| `--language` | 言語（ISO 639-1） |
| `--entity-kind` | individual / company / partnership / trust |
| `--chart` | 勘定科目テンプレートの種類（地域に複数ある場合）— 日本: general / it / food（既定 general）。専用の勘定科目表が無い地域では、特定の国に依存しない最小構成の勘定科目表になります |
| `--currency` | 通貨（ISO 4217。地域既定） |
| `--fiscal-start-month` | 会計年度開始月 1〜12 |
| `--fiscal-year` | この帳簿が扱う会計年度（YYYY。既定は今日を含む年度）— 前年度の申告をこれから済ませる場合は前年度など |
| `--sample` | 試せるデモ仕訳を約40件追加 |
| `--posting` | LLM-GUIDE.md に書き込む記帳ポリシー: `approve`(既定 — あなたが確認して記帳)/ `auto`(検証を通った仕訳をアシスタントが自動記帳) |
| `--book-id` | 既存のサーバー帳簿に事前リンク（上級） |

### iris onboard

このマシンの AI アシスタントを帳簿につなぎます。`iris mcp serve` を MCP クライアント
に登録し、Claude Code スキルを書き込みます。Claude Code のプロジェクト設定
（`.mcp.json`）は常に書き込まれます。Claude Desktop・Codex CLI・Cursor・
Gemini CLI・VS Code は、マシン上で検出された場合（または各フラグで強制した
場合）に登録されます。

```bash
iris onboard [--book PATH] [--claude-desktop] [--codex] [--cursor] [--gemini] [--vscode] [--install-path] [--no-skill] [--dry-run]
iris onboard --status [--json]    # 読み取り専用レポート: どこに何が登録されているか
```

`--status` は各クライアントの登録状態を報告します（登録先のバイナリがまだ存在
するかも含む — 存在しない場合は `iris onboard` の再実行で直る古い状態です）。
`--json` で機械可読な出力になります。`iris onboard` の再実行は常に安全です。
登録はその場で更新され、重複しません。

### iris offboard

`iris onboard` の逆操作: すべてのクライアント設定から `irisbooks` の MCP 登録を
削除し（アンインストール済みクライアントの残骸も含む）、Claude Code スキルも
削除します。帳簿のデータやサインイン状態には触れません。冪等なので、クリーン
再インストール前の実行も安全です。

```bash
iris offboard [--book PATH] [--keep-skill] [--remove-path] [--dry-run]
```

| フラグ | 意味 |
| ---- | ------- |
| `--keep-skill` | Claude Code スキルを残す（他の帳簿がまだ使っている場合） |
| `--remove-path` | `onboard --install-path` で入れたバイナリも削除し、PATH 追加を戻す |
| `--dry-run` | 削除される内容の表示のみで、何も削除しない |

### iris uninstall

iris そのものをこのマシンから削除します: iris バイナリ、サインイン情報と
ローカル設定（`~/.config/irisbooks` — CLI セッションは先にサーバー側で失効
させます）、Claude Code スキル、マシン全体の MCP 登録（Claude Desktop・
Codex CLI）、`iris onboard --install-path` が追加した PATH 設定。実行前に、
このマシンで見つかった削除対象の正確な一覧を必ず表示し、確認を求めます。

帳簿には一切触れません — 帳簿はあなたが所有するただのファイルです。帳簿内の
エージェント設定（帳簿内の `.mcp.json`）もそのまま残ります。それも消したい
場合は、先に `iris offboard --book PATH` を実行してください。

```bash
iris uninstall [--yes] [--dry-run]
```

| フラグ | 意味 |
| ---- | ------- |
| `--yes` | 確認プロンプトを省略する |
| `--dry-run` | 削除計画の表示のみで、何も削除しない |

### iris clone

サーバー帳簿をディスクに取得します（`init` のライフサイクル上の対）。サインインが
必要です。Web アプリや、帳簿フォルダの外で実行した `iris api books new` で
作ったばかりの帳簿でもすぐに使えます。これらの帳簿には、最初から
`config/book.yaml` とひな形の勘定科目表が入っています（ローカル帳簿の中で作った
クラウド帳簿は空の状態で作られ、最初の `iris sync` でそのフォルダのファイルが
入ります）。AI アシスタント向けのローカルのガイド（`LLM-GUIDE.md`、
`CLAUDE.md`、`README.md`）が帳簿に無ければ、それも書き込みます。これらは同期
されないため、Web アプリで作った帳簿には最初は含まれていません。

```bash
iris clone <book-id> [dest] [--force]
```

## 確認・検証

### iris status

帳簿の識別情報、会計年度開始、アーカイブのフラグ、そして `draft` 下書きの
件数(下書きはレポートに含まれません)を表示します。

```bash
iris status [--json] [path]
```

**出力形**（`--json`）:

```text
{ name, bookId, region, language, currency, fiscalStartMonth,
  archived, archive?{ sourceBookId, fiscalYear },
  draftCount?, remoteDeleted? }
```

`archive` はアーカイブフォルダのときだけ、`draftCount` は下書きを数えられたとき
だけ、`remoteDeleted` はサーバー側で帳簿が消えていると報告されたときだけ現れます。

### iris validate

帳簿の構造とエントリを検証します。YAML、貸借一致、科目の存在、日付の整合、
ステータスの値、（日本の課税事業者は）税区分。

```bash
iris validate [--v] [--json] [--fix] [path]
```

`--v` は走査した全ファイルを表示、`--json` は問題と件数を出力しエラー時に 1 で終了。
`--fix` は地域オーバーレイが導いた値（ヒントとして報告されるもの。たとえば税抜経理の
帳簿で明細に含まれる消費税額）をファイルに記録してから、もう一度検証します。

**出力形**（`--json`）:

```text
{ book, bookOk, chartOk, journals, assets, notes,
  errors, warnings, hints, ok,
  issues[{ severity, file, code?, message }] }
```

`code` は安定したカタログキーです（`journal.date-required`、
`chart.alias-shadow-path`、`asset.ikkatsu-cost-range` など）。`message` は翻訳
されるので、分岐にはコードを使ってください。`ok` は `errors == 0` と同義で、
警告とヒントは `ok` にも終了コードにも影響しません。

### iris hash

単一ファイルの正規コンテンツハッシュを表示します（ローカルのバイト列とサーバーが
受理した内容を比較するときに便利）。

```bash
iris hash [--raw] <file>
```

### iris organize

帳簿のレイアウトを正規の形に整えます。既定はドライラン。

```bash
iris organize [--apply] [--fix month-folders,extensions,empty-raw,config-typos] [--json] [path]
```

`month-folders` は、`journals/YYYY-MM/` フォルダにあるのに日付がその月でない
仕訳を正しい月のフォルダへ移し、`notes/raw/` のパースキャッシュにある
`target:` のリンクを新しいパスに書き換えます。月より下のサブフォルダ（`auto/`
など）はそのまま残り、月フォルダの外にある仕訳は動かしません。

**出力形**（`--json`）— `--apply` がそのまま実行する計画そのものです。

```text
[ { family, code, path, new_path?, delete?, reason } ]
```

`family` は `--fix` のカテゴリ。移動なら `new_path`、削除なら `delete: true` が
付きます。

## レポート・検索

### iris balance

基準日時点の試算表（記帳済みのみ）。

```bash
iris balance [--as-of YYYY-MM-DD] [path]
```

出力は `iris report tb` と同じ試算表のドキュメントです（下記）。

### iris report

財務諸表。サブコマンド:

```bash
iris report tb [--as-of YYYY-MM-DD] [path]               # 試算表
iris report pl [--from D] [--to D] [path]                # 損益計算書
iris report bs [--as-of YYYY-MM-DD] [path]               # 貸借対照表
iris report ledger --account PATH [--as-of D] [path]     # 科目別元帳
iris report sum --by KEY[,KEY...] [--from D] [--to D] [--year YYYY] [path]
                                                         # 仕訳明細のグループ別集計
```

レポートの出力は **JSON** です（金額は最小単位の整数 — Web API と同じ形）。
テキスト表モードはありません: 日本語の勘定科目名では端末の列揃えが安定せず、
AI はもともと JSON を読み、人間向けの整形表示は Web アプリが担います。
互換性のため `--json` フラグは受け付けます（no-op）。

`report sum` は記帳済みの仕訳明細を指定キー — `account`、`unit`、`payee`、
`month`、または `tax.category` のようなドット記法のフィールド — でグループ化し、
グループごとの借方・貸方・純額と明細数を返します（例: 消費税の集計は
`--by tax.category,tax.rate --year 2026`）。キーを持たない明細は空キーの
グループとして明示されるため、未分類の明細が黙って消えることはありません。
`--year` は会計年度（開始年ベース）、`--from/--to` は任意の日付範囲（両端含む）です。

**日付の既定値**。省略した日付は、帳簿の会計年度（`fiscal_year`。帳簿は1年に
1冊）から補います。残高（`balance`・`tb`・`bs`・`ledger`）は今日時点、その年度が
終わっていれば年度末時点で出します。「今日」は帳簿の地域での日付で、日本の帳簿
なら日本時間です。`pl` と `sum` は、年度の初日から同じ日までを集計します。
前年度の帳簿を年が明けてから申告のために開くと、前年度を通年で表示します。
`--to` だけを指定すると、その日が属する会計年度の
初日から集計します。`--from` だけなら今日までです。今日より後の日付の仕訳は、
その日が来るまで含みません。JSON には使った日付が必ず入り、Web アプリ・MCP ツール・
リモートコネクタも同じ既定値を使います。申告に使う数字は、期間（`--year` または
`--from`/`--to`）を指定して出してください。

**出力形**。5つとも1つの行型の上に組み立てられています。

```text
Balance = { account, debits, credits, type?, net? }

tb      { asOf?, rows[Balance], totalDebit, totalCredit, balanced }
pl      { from?, to?, income[Balance], expenses[Balance],
          totalIncome, totalExpense, net }
bs      { asOf?, assets[Balance], liabilities[Balance], equity[Balance],
          totalAssets, totalLiabilities, totalEquity,
          currentEarnings, balanced }
ledger  { account, asOf?,
          entries[{ date, file, payee, debit, credit, balance }],
          totalDebits, totalCredits, balance }
sum     { groupBy[], from?, to?,
          rows[{ keys[], debit, credit, net, lines }],
          totalDebit, totalCredit, totalNet, totalLines }
```

`Balance` の `type` と `net` は、その科目が勘定科目表に照らして分類できたときに
入ります。`ledger.entries[].balance` はその行を反映した**後**の累計残高、`file`
は元の仕訳ファイルで、これが帳簿間の相互関連性をたどる道筋になります。
`sum.rows[].keys` は位置対応で、`--by` に渡したキーと同じ順に1つずつ並びます。

### iris search

任意のフィルタの組み合わせ（AND）で仕訳を探します。決定論的・オフライン。

```bash
iris search [--from D] [--to D] [--min N] [--max N] [--payee S] \
  [--status draft,posted,closed] [--account S] [--tag S] [--json] [path]
```

ステータス列には**実効**ステータスが表示されます。日付が締め済み会計年度に
入っている仕訳は、ファイルの記載にかかわらず `closed` と表示され、
`--status closed` はまさにそれらを絞り込みます。

**出力形**（`--json`）:

```text
[ { path, date, payee, status, amount, lines } ]
```

`amount` はその仕訳の借方合計（マイナー単位）、`lines` は明細行数です。

### iris show

パスの相互参照。資料に対してはそれを引用する仕訳、仕訳に対しては引用する資料と
兄弟を表示します。

```bash
iris show [--json] <path> [path]
```

**出力形**（`--json`）:

```text
{ ref, mode,
  citedBy[{ path, date, payee, status }],
  cites[{ path, type?, locator?, alsoCitedBy[] }] }
```

`mode` は `ref` を書類として読んだか仕訳として読んだかを示します。`type` は添付の
由来（`receipt` / `invoice` / `bank_statement`）で、補助資料には付きません。
`alsoCitedBy` は同じ書類を引いている**他の**仕訳の一覧で、領収書の二重計上を
見つける手がかりになります。

### iris export

仕訳・試算表・元帳・資産を CSV（UTF-8 BOM 付き）で書き出します。

```bash
iris export [--out DIR] [--year YYYY] [--as-of YYYY-MM-DD] [path]
iris export assets [--out DIR] [path]
```

## 固定資産

### iris asset

固定資産の減価償却とレポート。

```bash
iris asset schedule [path]                    # 各資産の償却スケジュール
iris asset depreciate --month YYYY-MM [path]  # その月の仕訳を生成（status: draft）
iris asset depreciate --year YYYY [path]      # 年度合計の仕訳を期末日付で資産ごとに生成
```

方式は会計年度ごとにどちらか一方を選びます。すでに月次仕訳がある年度への年次
実行（およびその逆）は拒否されます — 混在すると二重計上になるためです。

## 地域オーバーレイ

### iris overlay

地域オーバーレイは、帳簿が検証と計算に使う国固有のルール・レシピ・派生の
バージョン付きセットです。`config/book.yaml` の `overlay:` で固定され、帳簿独自の
`config/overlays/` があればそれで拡張されます。

```bash
iris overlay list [--json] [path]                                   # 適用中のオーバーレイ: 固定バージョン・層・ルール・レシピ・派生
iris overlay recipe <id> --set name=value ... [--write <path>] [path]  # レシピを実行。--write で根拠付きで記録
iris overlay test [--json] [path]                                   # 適用中の各層のゴールデンテストを実行
iris overlay test --dir <overlay-dir> [--json]                      # 公開オーバーレイ 1 つのゴールデンテストを帳簿の外で実行
iris overlay fetch [path]                                           # 帳簿が固定したバージョンを、この iris になければダウンロードして検証
iris overlay upgrade [--to <id>@<version>] [path]                   # 固定を公開済みの最新版（または --to）に移す
iris overlay trust [path]                                           # この帳簿の config/overlays/ をこのマシンで信頼する
```

`recipe` は提案を表示します。`--write` を付けると、償却表のレシピは資産ファイルを
書き換え（`schedule:` + `schedule_source:`）、集計レシピは `filings/` に申告記録を
書きます。マップ型のパラメータは `--set name='{"1": 90}'` のように渡します。

`upgrade` と `fetch` は公開リポジトリ
[`irisbooks/overlays`](https://github.com/irisbooks/overlays) のリリースから
ダウンロードし、使う前に署名を確認します。お使いの `iris` より前に公開された
バージョンは `iris` に含まれており、ダウンロードされることはありません。ダウンロードしたバージョンは
`~/.config/irisbooks/overlays/` に保存され（帳簿の中には置きません）、読み込むたびに
あらためて確認されます。`upgrade` は、新しいバージョンが自身のテストに合格し、
帳簿の `config/overlays/` がその上で読み込めるときにだけ変更を加えます。
`iris validate` が何かをダウンロードすることはありません。

## 編集・記帳

### iris post

仕訳を `draft` から `posted` にして記帳し、（リンク済みなら）同期します。帳簿の
オーナーが**記帳承認**（Web アプリ → 設定）をオンにしている場合、記帳は Web
アプリ専用です。`iris post` はローカルで拒否し、サーバーも push された
ステータス変更を `APPROVAL_REQUIRED` で拒否します。
事前に各ファイルが空でない・貸借一致であることを検証します。日付が締め済み
会計年度に入っている仕訳は拒否されます（*"FY \<n\> is sealed (closed period) —
run `iris reopen <n>` to amend it, then re-seal"*）。

```bash
iris post [--dry-run] <file>...
iris post [--dry-run] --all
```

`--all` はファイルを指名する代わりに、帳簿内のすべての `draft` 下書きを
記帳します — 自分が書いていない下書き(スマホ/コネクタ経由、メール取り込み、
自動生成の減価償却)も対象です。検証に失敗した下書きは報告のうえ下書きの
まま残ります。記帳ポリシー `auto` の帳簿での定型操作です。

### iris diff

push される内容 — ローカル変更と最後の同期スナップショットの差 — を表示します。

```bash
iris diff                # 保留中の全変更を一覧
iris diff <relpath>      # 1ファイルの行単位差分
iris diff --paths        # 名前と種別のみ
```

## 同期・コンフリクト（クラウド）

### iris sync

明示的な1回のパス。ローカル変更を push、リモート変更を pull し、ファイルごとの
受理/拒否を報告します。帳簿がクラウドにリンクされ、サインイン済みである必要が
あります。

```bash
iris sync [--quiet] [--json] [--allow-bulk-delete] [path]
```

終了コード: `0` クリーン · `1` 拒否/コンフリクト/IO · `2` 使い方/設定 · `3` 終端的
切断（帳簿削除、アクセス取消、セッション失効）。

1回の sync で帳簿のクラウドファイルの大半を削除しようとすると、サーバーは
安全装置としてその削除を拒否します（`BULK_DELETE_REFUSED`）。大量削除が本当に
意図したものであれば、`--allow-bulk-delete` を付けて再実行してください。

**出力形**（`--json`）— 上記すべてを1つのドキュメントに置き換えたもので、AI が
編集のたびに読むのはこれです。

```text
{ status, counts{ pushed, pulled, deleted, conflicts }, queueLeft,
  disconnected, disconnectReason?,
  newRejections[], allRejections[], applyErrors[], blockedByConflicts[],
  error? }
```

- `status` — `ok` | `rejected` | `conflicts` | `disconnected` | `error`
- `disconnectReason` — `deleted` | `forbidden` | `auth_expired`
- `newRejections` / `allRejections` — 要対応レコード。`iris attention list
  --json` と同じ形です
- `blockedByConflicts` — 未解決の `.conflicted` サイドカーがある正規パス。
  **空でなければそのパス全体が no-op** です。push も pull も起きていないので、
  先にマージするか解決してください
- `applyErrors` — リモートの変更をローカルに反映できなかったもの。作業ツリーが
  不完全な可能性があるため、いまのファイルを信用せず再実行してください

編集 → 同期 → 読み取り のループで2回目の呼び出しが要らないのはこのためです。
ファイルごとの受理**と**拒否が、この1つのレスポンスに両方入っています。

### iris conflicts

push がコンフリクト（409）すると、サーバー版が正規パスを取り、あなたの版が
`.conflicted` サイドカーになります。

```bash
iris conflicts list [path]
iris conflicts resolve <path> --keep mine|cloud [path]
```

通常は手動マージで解決します（正規ファイルを編集し、サイドカーを削除し、
`iris sync`）。[トラブルシューティング](troubleshooting.md) を参照。

### iris attention

サーバー側拒否のローカルキューを管理します。

```bash
iris attention list [path]              # パス + コード + 問題を表示
iris attention retry [path]             # 抑制を外す。次の `iris sync` で再 push
iris attention retry [path] --path <relpath>   # 1ファイルのみ
```

**出力形**（`list --json`）:

```text
{ records[ { path, local_fs, local_sha, code?,
             issues[{ field, message, rule? }], detected_at, reason? } ] }
```

`code` はそのファイルを拒否したサーバー側の不変条件です
（`UNBALANCED_JOURNAL`、`UNKNOWN_ACCOUNT`、`PERIOD_SEALED`、
`BULK_DELETE_REFUSED` など）。`OVERLAY_RULE` は地域オーバーレイのルール
（公開オーバーレイのもの、または `config/overlays/` にある帳簿独自のもの）が
拒否したことを表し、各 issue の `rule` がそのルールを示します。ルールは
`iris overlay list` で確認できます。

### iris yearend

翌年度の帳簿を作って会計年度を終えます — 年度締めの会計面です
（コンプライアンス面の年度のロックは `iris api seal`）。1つの帳簿は1会計年度分
なので、`iris yearend` は翌年度の帳簿を独立したコピーとして、この帳簿と同じ
階層の新しいフォルダに作ります（`acme-2025` → `acme-2026`。フォルダは `--to` で
指定できます）。新しい帳簿には次のものが入ります。

- `config/` — `fiscal_year` を翌年度に進め、独自の帳簿 ID を持つ `book.yaml`、
  勘定科目表、`rules.yaml`、`config/overlays/`
- ガイド（`README.md`・`LLM-GUIDE.md`・`CLAUDE.md`）と方針のノート
  （`decisions.md`・`workflow.md`・`todos.md`・`open-questions.md`）
- 新年度の開始時点でまだ保有している固定資産
- 期首残高の仕訳。`journals/<YYYY-MM>/0000-opening-balances.md` に、新年度の
  初日の日付で `opening-balance` タグを付けて作られます。貸借対照表科目は
  期末残高のまま繰り越され（外貨・暗号資産など数量を管理している保有資産は
  数量も含めて）、収益・費用はゼロにリセットされ、当期純利益は
  `config/book.yaml` の `opening_balance_equity_account` で指定した資本科目
  （未指定なら帳簿唯一の資本科目）へ折り込まれます。

すでに新年度の日付で記録した仕訳は、参照している元資料とともに新しい帳簿へ
**移動**します。それより前の仕訳、`compiled/`、`filings/`、パースキャッシュ、
処分済みの資産はこの帳簿に残ります。`--carry notes,raw` を付けると、`notes/` や
`raw/` もまるごとコピーします。

この帳簿がクラウドにリンクされている場合は、同じ実行で新しい帳簿のクラウド側も
作ります。この帳簿にアクセスできる人は全員、新しい帳簿にも同じ権限でアクセスできるように
なり、この帳簿の受信アドレスは新しい帳簿へ移ります。そのうえで両方の帳簿を同期します。
実行前に確認を求めます。`--yes` で確認を省略でき（端末が接続されていない場合は
必須です）、`--local` を付けるとローカルの帳簿だけを作ります。

作成後、2つの帳簿の間につながりはありません。前年度への遅れた訂正を反映するには、
前年度の帳簿で修正し、同じ `--to` を付けてもう一度 `iris yearend` を実行します。
新しい帳簿の期首残高仕訳が更新され（結果が同一なら何もしません）、前回の実行後に
前年度の帳簿に加わった新年度の日付の仕訳が移動します。新しい帳簿の設定とノートは
そのまま残ります。新年度が締め済みになると、期首残高仕訳はその時点の内容で
凍結されます — 不一致は対処方法とともに報告され、無言で書き換えられることは
ありません。締める年度の日付の未記帳の下書きは警告されます（繰越に含まれません）。

`<fiscal-year>` は省略できます。既定は帳簿の `fiscal_year` で、それ以外の年度を
指定すると拒否されます。

```bash
iris yearend [<fiscal-year>] [--to PATH] [--carry notes,raw] [--yes | --local] [path]
```

### iris reopen

締め済み会計年度のロックを解除して修正できるようにします。サーバー上で締めの
ロックが解除されます（締め済み期間はこれを実行するまですべての書き込みを拒否
します。再オープン中の編集は締め後の編集として恒久的にフラグされます）。年度の
ファイルは作業ツリーから離れていません — 締めは年度をロックするだけで、
ファイルを取り除きません — ので復元するものはありません。そのまま編集し、
`iris sync` で編集を push し、`iris api seal` で年度を再度締めてください。

```bash
iris reopen <fiscal-year> [path]
```

## 価格（純資産）

### iris price

単位価格をオフラインで記録・一覧し、サーバーへ同期します。ユーザー単位（帳簿には
保存されません）。

```bash
iris price add --unit BTC --price 9850000 [--currency JPY] [--date YYYY-MM-DD] [--source S]
iris price list [--unit BTC] [--json]
iris price sync
```

**出力形**。`list --json`:

```text
[ { unit, currency, date, valueMicro, source?, origin, recordedAt } ]
```

`valueMicro` は**1単位あたり**の値 × 1,000,000 です（¥9,850,000 のビットコインは
`9850000000000`）。`origin` は `local`（この端末で記録）か `server`。
`sync --json` は `{ pushed, pulled }` を返します。

## MCP サーバー

### iris mcp

`iris` の各動詞を BYO エージェントに公開する Model Context Protocol サーバーを、
1つの帳簿に固定して実行します。

```bash
iris mcp serve [--book PATH] [--http 127.0.0.1:PORT]
```

ローカルツール: `validate`・`diff`・`balance`・`report`・`status`。資産ツール:
`asset_schedule`（エンジンによる資産別の数値）と 3 つの償却計算ツール
`declining_table`・`flat_table`・`straight_line_table` — レシピのない方法について、
AI がこれらを組み合わせて `schedule:` に記録します。レシピツール: 帳簿の
オーバーレイのレシピごとに 1 つ（`jp_teiritsu`・`jp_shouhizei-general`・
`jp_shouhizei-simplified`）。`write` にパスを渡すと結果を根拠付きで記録します。
クラウドツール（認証時）: `sync`・`seal`・`export_from_cloud`。

### iris version

```bash
iris version
```

---

# クラウドコマンド（`iris api …`）

**帳簿 ID** に対して動き、認証が必要です。

## アカウント単位

### iris api login

ブラウザ補助のサインイン。このデバイス専用の CLI セッションが発行されます。
Web アプリからサインアウトしても CLI には影響せず、90 日間使用がなければ
自動失効します（使うたびに延長）。取り消しは Web アプリの「あなたの設定
（アバターメニュー） → API トークン」から行えます。

```bash
iris api login
iris api whoami     # キャッシュ済みトークンを検証
iris api logout     # このデバイスのセッションを取り消してトークンを削除
```

クラウド上の AI エージェントや、localhost へのアクセスが制限されたブラウザでは、
認可結果をファイルで受け取れます。ブラウザのダウンロード先を CLI から読み取れる
必要があります。

```bash
iris api login --handoff-file
# 表示された URL を開いてサインインし、アクセスを許可すると iris-login.json がダウンロードされます。
iris api login --complete /path/to/downloads/iris-login.json
iris api whoami
```

ダウンロードしたファイルのパスだけを CLI に渡してください。CLI がファイルを読み、
セッションの資格情報を内部で保存します。ファイルに入るのは一度だけ使える認可コードで、
セッショントークンではありません。コードは CLI が保持する秘密の PKCE 検証値に
ひも付き、許可から 5 分で失効します。CLI の待機状態は開始から 10 分で失効します。
やり直すと以前の待機状態が置き換わるため、新しい URL とダウンロードを使ってください。
完了時には、開始時に選んだ環境を使います。認可画面でキャンセルするとキャンセル結果が
ダウンロードされ、そのファイルを CLI に渡すと資格情報を保存せずに待機状態を解除します。
完了後はダウンロードしたファイルを削除してください。その後は通常どおり
`iris api books …` と `iris sync` を使えます。

### iris api books

クラウド帳簿の一覧・作成、またはローカル帳簿のリンク。

```bash
iris api books list [--json]
iris api books new [flags] [--json]
iris api books link <book-id> [path]
```

クラウド ID をまだ持たないローカル帳簿の中で `new` を実行すると、作成した帳簿が
そのフォルダに自動で link されます。`books link` と同じ効果なので、続けて
`iris sync` がそのまま動きます。クラウド帳簿はそのフォルダの `config/book.yaml`
（帳簿名、会計年度、地域、通貨、個人・法人の区分、会計年度の開始月）から作られる
ため、フラグは不要です。ファイルと食い違うフラグを指定すると拒否します。作成時点の
クラウド帳簿は空で、最初の同期でフォルダ自身のファイルが push されます。
`--no-link` を付けると、これらをすべて行いません。すでに link 済みの
帳簿の中で `new` を実行した場合は拒否します。そこに2つ目のクラウド帳簿を作っても、
`iris sync` は最初の帳簿に push し続けるため、空のまま残るだけだからです。

### iris api token

パーソナルアクセストークン（PAT）の一覧表示と失効。新しい PAT の発行は
Web のみ（あなたの設定 → API トークン）ですが、失効はここからも行えるため、
自動化された処理が終了時に自分の使った PAT を失効できます。サインイン
済みセッションまたはフルアクセス PAT が必要です。

```bash
iris api token list [--json]
iris api token revoke <token-id>
```

### iris api config

ユーザー単位の設定（レポート通貨、既定の単位スケール）を表示・設定します。
`iris init` 時に新しい帳簿へ取り込まれます。

```bash
iris api config
iris api config set --base-currency USD
iris api config set --set-unit BTC:8,XAU:4
iris api config set --remove-unit XAG
```

## 帳簿単位

### iris api grants

帳簿のアクセス権を管理します（オーナーのみ）。

```bash
iris api grants list [--json] <book-id>
iris api grants invite --email EMAIL <book-id>
iris api grants role --user USER_ID --to OWNER|BOOKKEEPER|REVIEWER <book-id>
iris api grants revoke --user USER_ID <book-id>
```

### iris api inbox

帳簿の受信メール管理: 受信アドレスの表示、送信者許可リストの管理、隔離
メールの確認。「メールで書類を取り込む」を参照してください。

```bash
iris api inbox show [--json] <book-id>
iris api inbox allow <pattern> <book-id>       # user@host または *@host
iris api inbox disallow <pattern> <book-id>
iris api inbox quarantine [--json] <book-id>
```

### iris api seal

会計年度を締めます（seal）。締め済み期間は**ロック**され、そこへの書き込みはどの作業面でもすべて拒否され
ますが、年度のファイルは作業ツリーにそのまま残ります。締め済み年度を修正するには
`iris reopen <fy>` を実行します — 再オープン中の編集は監査証跡（`iris api
history`）にフラグ付きで記録されます — 修正が終わったらこのコマンドを再実行して
年度を再度締めます（新しい締めが古い締めを引き継ぎます）。`--preview` は、
締めでロックされるファイルの一覧を表示するだけで、何も締めません。
年度内に `draft` の下書きが残っている場合、締めは**拒否**されます —
締めた年度は完全に整理されていなければなりません。年度に属する仕訳なら先に
記帳し、不要なら削除し、翌期のものなら日付を開いている年度へ変更してください。
`--preview` がブロックしているドラフトを一覧表示します。

```bash
iris api seal --period YYYY [--type yearly] [--preview] <book-id>
```

### iris api balance / holdings / history

```bash
iris api balance [--as-of YYYY-MM-DD] <book-id>              # サーバー側試算表（JSON 出力）
iris api holdings [--as-of YYYY-MM-DD] [--json] <book-id>    # 単位ごとの純ポジション
iris api history [--path PATH] [--from D] [--to D] [--all] [--limit N] [--json] <book-id> # 訂正・削除の履歴
```

**出力形:**

```text
balance   [ { account, debits, credits, type?, net? } ]
holdings  [ { account, unit, quantity } ]
history   [ { id, path, op, sha?, version_id?, size_bytes,
              actor, actor_display?, source?, reason?,
              post_seal_period?, moved_from_path?, ts } ]
```

`holdings` は単位が付いた行だけを数え、正味ゼロのポジションはサーバー側で
除かれます。

`history`（訂正・削除の恒久的な記録）の `actor` は安定したアカウント識別子
（監査上の身元）で、`actor_display` はそれをサーバーが読み取り時に名前や
メールへ解決した人間向けの表示です。`post_seal_period` は、その会計年度を
締めた**後**に着地した変更に付きます — 監査人が探すのはこの印です。
`moved_from_path` は削除+作成ではなく改名であったことを記録します。

`history` は、絞り込まなければ新しい順に 100 件を返します。

- `--path` — 1 つのファイルの履歴。
- `--all` — すべてのイベント。帳簿は1会計年度なので、これがその年度の記録の
  すべてで、締め後に行った訂正も含みます。
- `--from` / `--to` — 2 つの日付の間に行われた変更。日付は帳簿のタイムゾーン
  （日本の帳簿なら日本時間）で解釈します。

`--from`、`--to`、`--all` のいずれかを付けると、該当するすべての
イベントを返します（`--limit` を指定すればその件数で止まります）。税務署から
求められたときなど、記録をファイルで渡すには JSON で書き出します。

```bash
iris api history --all --json <book-id> > history-2025.json
```

他のクラウドコマンドの `--json`（`books list`、`grants list`、`token list`、
`inbox show`、`inbox quarantine`）は、サーバーのレスポンスをそのまま通します。

### iris api export

```bash
iris api export [--out DIR] [--year YYYY] [--as-of YYYY-MM-DD] <book-id>  # CSV 群
```

`--year` を指定すると、その会計年度に属する仕訳のみがエクスポートされます。
締め済み年度もファイルはライブツリーに残っているため、他の年度と同じように
エクスポートされます。

### iris api price / networth

```bash
iris api price add --unit BTC --price 9850000 [--date YYYY-MM-DD] [--source S]
iris api price list [--unit BTC] [--json]

iris api networth [--as-of YYYY-MM-DD] [--json]              # 帳簿横断の合計
iris api networth --book <book-id> [--as-of YYYY-MM-DD] [--json]
iris api networth settings [--include|--exclude|--reset <id>]
iris api networth history [--months N] [--refresh] [--json]
iris api networth movers [--as-of D] [--compare D] [--json]
```

`networth` は帳簿ごとの貸借対照表 — 資産から負債を引いたもの（`owner: true` の
科目は除く）— を評価します。単位で管理する保有は記録した価格（`basis: price`）、
それ以外と価格のない単位は簿価（`basis: book`）です。帳簿は自分の会計年度の中
だけで集計され、帳簿横断の合計は、集計に含めなかった帳簿を理由
（`year_ended` または `year_not_started`）とともに `excluded` に挙げます。変動要因は
帳簿をまたいで科目と単位ごとに比べるので、翌年度の帳簿への移行が売却には見えません。

## 環境変数

| 変数 | 用途 |
| --- | --- |
| `IRIS_API_TOKEN` | パーソナルアクセストークン。キャッシュ済みログイントークンより優先 |
| `IRIS_BOOK` | クラウドコマンドの既定帳簿 ID（位置引数があればそちらが優先） |
| `IRIS_API_ENDPOINT` | API エンドポイントの上書き。以下のすべてより優先 |
| `IRISBOOKS_APP_BASE` | アプリのベース URL（既定 `https://irisbooks.jp`） |
| `IRISBOOKS_API_BASE` | API のベース URL（既定 `<app-base>/api`） |

エンドポイント系の変数が未設定のときは、最後の `iris api login` で保存
されたエンドポイントを使います。ある環境にサインインしたセッションは、
そのまま同じ環境と通信し続けます。

## よくある終了コード

| コード | 意味 |
| --- | --- |
| `0` | 成功 |
| `1` | 検証エラー、拒否、または I/O 失敗 |
| `2` | 使い方・設定エラー（帳簿外、フラグ不正） |
| `3` | 終端的切断 — 同期コマンドのみ（帳簿削除、アクセス取消、セッション失効） |
