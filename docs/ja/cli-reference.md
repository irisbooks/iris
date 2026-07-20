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

> このページを正しく保つために: コマンド一覧は `iris/cmd/iris/main.go` の
> `commands` テーブルをミラーしています。そこでコマンドを追加・改名したら、この
> ページ（と日本語版）も更新してください。

## セットアップ

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
| `--chart` | 勘定科目テンプレート: general / it / food（既定 general） |
| `--currency` | 通貨（ISO 4217。地域既定） |
| `--fiscal-start-month` | 会計年度開始月 1〜12 |
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
必要です。Web アプリや `iris api books new` で作ったばかりの帳簿でもすぐに使え
ます。サーバーで作成された帳簿には、最初から `config/book.yaml` とひな形の
勘定科目表が入っています。

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

### iris validate

帳簿の構造とエントリを検証します。YAML、貸借一致、科目の存在、日付の整合、
ステータスの値、（日本の課税事業者は）税区分。

```bash
iris validate [--v] [--json] [path]
```

`--v` は走査した全ファイルを表示、`--json` は問題と件数を出力しエラー時に 1 で終了。

### iris hash

単一ファイルの正規コンテンツハッシュを表示します（ローカルのバイト列とサーバーが
受理した内容を比較するときに便利）。

```bash
iris hash [--raw] <file>
```

### iris organize

帳簿のレイアウトを正規の形に整えます。既定はドライラン。

```bash
iris organize [--apply] [--fix fy-folders,extensions,empty-raw,config-typos] [--json] [path]
```

## レポート・検索

### iris balance

基準日時点の試算表（posted のみ）。

```bash
iris balance [--as-of YYYY-MM-DD] [path]
```

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

`report sum` は posted の仕訳明細を指定キー — `account`、`unit`、`payee`、
`month`、または `tax.category` のようなドット記法のフィールド — でグループ化し、
グループごとの借方・貸方・純額と明細数を返します（例: 消費税の集計は
`--by tax.category,tax.rate --year 2026`）。キーを持たない明細は空キーの
グループとして明示されるため、未分類の明細が黙って消えることはありません。
`--year` は会計年度（開始年ベース）、`--from/--to` は任意の日付範囲（両端含む）です。

### iris search

任意のフィルタの組み合わせ（AND）で仕訳を探します。決定論的・オフライン。

```bash
iris search [--from D] [--to D] [--min N] [--max N] [--payee S] \
  [--status draft,posted,closed] [--account S] [--tag S] [--json] [path]
```

ステータス列には**実効**ステータスが表示されます。日付が Seal 済み会計年度に
入っている仕訳は、ファイルの記載にかかわらず `closed` と表示され、
`--status closed` はまさにそれらを絞り込みます。

### iris show

パスの相互参照。資料に対してはそれを引用する仕訳、仕訳に対しては引用する資料と
兄弟を表示します。

```bash
iris show [--json] <path> [path]
```

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

## 編集・昇格

### iris post

仕訳を `draft` から `posted` へ昇格し、（リンク済みなら）同期します。帳簿の
オーナーが**記帳承認**（ウェブアプリ → 設定）をオンにしている場合、記帳は
ウェブ専用です: `iris post` はローカルで拒否し、サーバーも push された
ステータス変更を `APPROVAL_REQUIRED` で拒否します。
事前に各ファイルが空でない・貸借一致であることを検証します。日付が Seal 済み
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

## 同期・コンフリクト（有料）

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
iris attention retry [path]             # 抑制を外しエンジンに再 push を依頼
iris attention retry [path] --path <relpath>   # 1ファイルのみ
```

### iris yearend

年度の期末残高から翌期の期首残高仕訳を書き出します — 年度締めの会計面です
（コンプライアンス面のロックとアーカイブは `iris api seal`）。貸借対照表科目は
期末残高のまま繰り越され、収益・費用はゼロにリセットされ、当期純利益は
`config/book.yaml` の `opening_balance_equity_account` で指定した資本科目
（未指定なら帳簿唯一の資本科目）へ折り込まれます。仕訳は
`journals/<fy+1>/<MM>/0000-opening-balances.md` に `opening-balance` タグ付きで
作成されます — レポートは最新のこの仕訳を残高計算の起点として扱うため、
各会計年度が自己完結します。

翌期がまだ開いている間は再実行しても安全です。締めた年度への遅れた訂正は
仕訳へ反映されます（結果が同一なら何もしません）。翌期が Seal 済みになると
仕訳は確定として凍結されます — 不一致は対処方法とともに報告され、無言で
書き換えられることはありません。年度内の未記帳の下書きは警告されます
（繰越に含まれません）。オフラインで動作します。実行後は `iris sync` で
push してください。

```bash
iris yearend <fiscal-year> [path]
```

### iris reopen

Seal 済み会計年度のロックを解除して修正できるようにします。サーバー上で Seal の
ロックが解除されます（Seal 済み期間はこれを実行するまですべての書き込みを拒否
します。再オープン中の編集は Seal 後の編集として恒久的にフラグされます）。年度の
ファイルは作業ツリーから離れていません — Seal はロックとアーカイブ作成であり、
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

## MCP サーバー

### iris mcp

`iris` の各動詞を BYO エージェントに公開する Model Context Protocol サーバーを、
1つの帳簿に固定して実行します。

```bash
iris mcp serve [--book PATH] [--http 127.0.0.1:PORT]
```

ローカルツール: `validate`・`diff`・`balance`・`report`・`status`。クラウドツール（認証時）:
`sync`・`seal`・`export_from_cloud`。

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
自動失効します（使うたびに延長）。取り消しは Web アプリの「設定 → API
トークン」から行えます。

```bash
iris api login
iris api whoami     # キャッシュ済みトークンを検証
iris api logout     # このデバイスのセッションを取り消してトークンを削除
```

### iris api books

クラウド帳簿の一覧・作成、またはローカル帳簿のリンク。

```bash
iris api books list [--json]
iris api books new [flags] [--json]
iris api books link <book-id> [path]
```

### iris api token

パーソナルアクセストークン（PAT）の一覧表示と失効。新しい PAT の発行は
Web のみ（設定 → API トークン）ですが、失効はここからも行えるため、
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

会計年度を締めて（期間 Seal）、そのアーカイブスナップショットを作成します。
Seal 済み期間は**ロック**され、そこへの書き込みはどの作業面でもすべて拒否され
ますが、年度のファイルは作業ツリーにそのまま残ります。Seal 済み年度を修正するには
`iris reopen <fy>` を実行します — 再オープン中の編集は監査証跡（`iris api
history`）にフラグ付きで記録されます — 修正が終わったらこのコマンドを再実行して
年度を再度締めます（新しい Seal が古い Seal を引き継ぎます）。`--preview` は、
Seal のアーカイブが収録するファイルの一覧を表示するだけで、何も Seal しません。
年度内に `draft` の下書きが残っている場合、Seal は**拒否**されます —
締めた年度は完全に整理されていなければなりません。年度に属する仕訳なら先に
記帳し、不要なら削除し、翌期のものなら日付を開いている年度へ変更してください。
`--preview` がブロックしているドラフトを一覧表示します。

```bash
iris api seal --period YYYY [--type yearly] [--preview] <book-id>
```

### iris api archive

Seal 済み会計年度のアーカイブをダウンロードします（ビルドを起動し待機）。

```bash
iris api archive download --year YYYY [--out DIR] [--timeout 5m] [--interval 5s] <book-id>
```

### iris api balance / holdings / history

```bash
iris api balance [--as-of YYYY-MM-DD] <book-id>              # サーバー側試算表（JSON 出力）
iris api holdings [--as-of YYYY-MM-DD] [--json] <book-id>    # 単位ごとの純ポジション
iris api history [--path PATH] [--limit N] [--json] <book-id> # 訂正・削除の履歴
```

### iris api export

```bash
iris api export [--out DIR] [--year YYYY] [--as-of YYYY-MM-DD] <book-id>  # CSV 群
iris api export audit <book-id>                                          # 監査人向け一式
```

`--year` を指定すると、その会計年度に属する仕訳のみがエクスポートされます。
Seal 済み年度もファイルはライブツリーに残っているため、他の年度と同じように
エクスポートされます。

### iris api price / networth

```bash
iris api price add --unit BTC --price 9850000 [--date YYYY-MM-DD] [--source S]
iris api price list [--unit BTC] [--json]

iris api networth [--as-of YYYY-MM-DD] [--json]              # 帳簿横断の合計（有料）
iris api networth --book <book-id> [--as-of YYYY-MM-DD] [--json]
iris api networth settings [--include|--exclude|--reset <id>]
iris api networth history [--months N] [--refresh] [--json]
iris api networth movers [--as-of D] [--compare D] [--json]
```

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
