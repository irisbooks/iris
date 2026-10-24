# CLI コマンドリファレンス

`iris` の全コマンドを目的別にまとめます。`iris --help` は、帳簿、記帳、
レポート、同期、資産管理、AI 連携、クラウド管理、インストールに分けて表示します。
トップレベルにあるコマンドでも、サーバーと通信する場合があります。

- ローカルの帳簿は `--book-path PATH` または各コマンドの位置引数で指定します。
  どちらも省略すると、現在のフォルダから上にたどって帳簿を探します。
  複数帳簿の資産集計には `--books-dir PATH` または帳簿フォルダの一覧を使います。
- 帳簿単位のクラウド操作（`iris api …`）は、`--book-id ID`、位置引数の帳簿 ID、
  `IRIS_BOOK` の順で指定できます。アカウント単位の操作には帳簿の指定は不要です。
  クラウドへのアクセスには `iris api login` または `IRIS_API_TOKEN` が必要です。
- `clone`・`sync`・`reopen` は通信します。`post` は記帳後に連携済みの帳簿全体を
  同期し、`--local` を付けると同期を省略します。連携済み帳簿の `yearend` は、
  `--local` を選ばない限り翌年度のクラウド帳簿を作成・同期します。
  `price sync`、パッケージのダウンロード、`update` も通信します。

最新の使い方は `iris <command> --help` または `iris help <command>` で確認できます。
ヘルプは帳簿・ログイン・通信なしで動き、標準出力に表示して終了コード 0 を返します。
フラグは引数の前後どちらにも置けます。`--` 以降はフラグとして解釈しません。
真偽値を明示する場合は `--flag=true` または `--flag=false` と書きます。

計算・修復（`journal complete`・`organize`・`financial prepare`・`overlay recipe`、
`validate` の導出値）は、`--apply` を付けたときだけ書き込みます。レシピには
`--out PATH`、計算結果の保存には確認済みの `--revision` も必要です。
`post`・`yearend`・`overlay select`・`overlay upgrade`・`api seal` は指定した操作を
実行し、`--dry-run` を付けると変更せずに確認できます。`yearend` は翌年度の帳簿に
残高を繰り越します。今年度のロックは別途 `api seal` で行い、修正時は `reopen` で
解除します。

`report`・`balance`・`reconcile`・`allocation`・`context`・`financial`・
`journal complete`・`networth`・`analytics export` は常に JSON を出力します。
ほかの参照コマンドでは、各ヘルプに記載された `--json` を使えます。
`sync issues list`・`conflicts list`・`api config show` も対応しています。
結果は標準出力、エラーは標準エラー出力に出します。終了コードは成功が 0、
処理・検証の失敗が 1、引数・設定の誤りが 2、同期の切断が 3 です。

コマンド名は `journal complete`・`references`・`sync issues` に統一し、旧名の
`autocomplete`・`show`・`attention` は削除しました。フォルダ指定には
`--book-path` を使い、曖昧だった `--book` は削除しました。締めの確認は
`api seal --dry-run`、計算結果の書き込みは `validate --apply`・
`financial prepare --apply`・`overlay recipe --out PATH --apply` を使います。

JSON を出すコマンドには共通の約束があります。**金額は帳簿通貨のマイナー単位の
整数**（scale 0 なら ¥1,200 は `1200`、scale 2 なら $12.00 が `1200`）、日付は
`YYYY-MM-DD` の文字列、出力は2スペースインデントで整形されます。以下の出力形は
キーの骨組みで書いてあり、`?` は値が空のとき省略されるキーです。

## セットアップ

### iris docs

使用中の実行ファイルに同梱された、LLM 向けの英語資料を読みます。帳簿・ログイン・
通信・キャッシュのダウンロードは不要です。各章はその実行ファイルのリリースに
対応します。人向けの日本語マニュアルはオンラインで参照できます。

```bash
iris docs                                      # トピック一覧
iris docs cli-reference                         # 節 ID と語数の一覧
iris docs cli-reference --full                  # 章の全文を明示的に読む
iris docs cli-reference --section iris-sync     # 指定した節とその下位の節
iris docs --json cli-reference --section iris-sync
```

フラグはトピックの前後に置けます。トピックを指定すると、既定で節の一覧を返します。
`--list` でも同じ一覧を明示的に指定できます。`--section` は指定した節と下位の節、
`--full` は章の全文を読みます。これらの指定は併用できません。一覧には語数も含みます。
JSON には `version`・`source: "bundled"`・`language: "en"`・`words` と、指定に応じて
`topics`・`sections`・`markdown` が含まれます。存在しない指定は終了コード 2 で
確認方法を案内し、全マニュアルへ切り替えることはありません。
実行方法は `iris <command> --help`、クラウドの利用条件や認証手順は現在の
オンライン情報も確認してください。資料の参照は操作の許可にはなりません。
ローカル MCP の `read_docs(topic?, section?, outline?, full?)` も同じ内容を返し、
帳簿の指定は不要です。トピックだけなら節の一覧、`full=true` なら章の全文です。
オフライン資料の参照先には `iris docs` コマンドを示し、MCP でも同じ topic と section を使えます。

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
指定できます（既定は `https://irisbooks.io/dl`）。署名は組み込みの公開鍵で必ず検証し、
`minisign` のインストールは不要です。検証に失敗した場合、古い実行ファイルは残ります。
開発版の置き換えや、古いバージョンへの更新は自動では行いません。

`.mcpb` の場合、確認結果に対応するバンドルの URL が表示されます。クライアントの
拡張設定から入れ直してください。CLI の更新後は帳簿のフォルダーで `iris onboard` を
再実行し、MCP を再起動します。`check_update` で AI が使うバージョンを確認してください。
Windows で使用中のファイルを置き換えられない場合は、MCP サーバーを停止して再実行します。
このコマンドがない古い版は、まずインストーラーで更新します。

### iris init

新しい帳簿を作ります。引数なしの `iris init` は現在のフォルダでガイド付きウィザードを開きます。
フラグを指定する場合は、作成先のパス（現在のフォルダなら `.`）も指定すると、
質問を飛ばせます。

```bash
iris init [flags] <path>
```

| フラグ | 意味 |
| --- | --- |
| `--name` | 帳簿の表示名 |
| `--region` | 地域コード（JP, US。既定 JP） |
| `--preset` | 用途: `personal`（家計の勘定科目）/ `business`（事業用。既定）。法人・個人事業の区分や税務上の取扱いは別に設定 |
| `--language` | 言語（ISO 639-1） |
| `--chart` | 勘定科目テンプレートの種類（地域に複数ある場合）— 日本: general / it / food（既定 general）。専用の勘定科目表が無い地域では、特定の国に依存しない最小構成の勘定科目表になります |
| `--currency` | 通貨（ISO 4217。地域既定） |
| `--fiscal-start-month` | 会計年度開始月 1〜12（既定は 1 月。4 月に始まる年度なら `4`） |
| `--fiscal-year` | この帳簿が扱う会計年度（YYYY。既定は今日を含む年度）— 前年度の申告をこれから済ませる場合は前年度など |
| `--sample` | 事業用の勘定科目に対応するデモ仕訳を約40件追加。personal では利用不可 |
| `--posting` | AGENTS.md に書き込む記帳ポリシー: `approve`(既定 — あなたが確認して記帳)/ `auto`(検証を通った仕訳をアシスタントが自動記帳) |
| `--book-id` | 既存のサーバー帳簿に事前リンク（上級） |

対話形式の初期設定、親フォルダーの MCP `create_book`、Web・API の明示的な新規作成は、
同じ作成処理を使います。personal は共通パッケージと家計の勘定科目、business は共通・
地域パッケージと事業用の勘定科目を選びます。固定バージョンのコピーを保存してから、
選択内容を帳簿設定に書き込みます。設定内の `creation` は作成時のプリセットと版の記録です。
編集・複製・年度更新では帳簿の実際のファイルを使い、プリセットを適用し直しません。
税務上の適用条件、証拠資料、勘定科目の対応は、初期設定の案内に従って別に判断します。
初期化後は、選択したパッケージと解決できた出典、最大3件のタスクへのリンクも表示します。
共通のコンテキスト取得処理を使い、古い定義にタスク情報がなければ、その制約を示します。
新版のタスクを旧版のものとして表示しません。

新しいクラウド帳簿にも、`iris api books new --preset personal --name "家計" --fy 2026`
で同じ設定を使えます。新規作成時は `--chart general|it|food` と `--language en|ja`
も指定できます。既存のローカル帳簿を接続する場合は、実際の設定・勘定科目・記帳方針を
保持し、プリセットによる上書きを拒否します。クラウドで作成を再試行しても、最初に
保存した初期ファイルとハッシュを使います。ローカル帳簿の接続では、サーバーが保持する
元の初期ファイルと変更履歴を確認してから、設定・勘定科目・記帳方針を置き換えます。

### iris onboard

このマシンの AI アシスタントを帳簿につなぎます。`iris mcp serve` を MCP クライアント
に登録し、Claude Code スキルを書き込みます。Claude Code のプロジェクト設定
（`.mcp.json`）は常に書き込まれます。Claude Desktop・Codex CLI・Cursor・
Gemini CLI・VS Code は、マシン上で検出された場合（または各フラグで強制した
場合）に登録されます。

```bash
iris onboard [--book-path PATH] [--claude-desktop] [--codex] [--cursor] [--gemini] [--vscode] [--install-path] [--no-skill] [--dry-run]
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
iris offboard [--book-path PATH] [--keep-skill] [--remove-path] [--dry-run]
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
場合は、先に `iris offboard --book-path PATH` を実行してください。

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
`config/book.yaml`、ひな形の勘定科目表、`AGENTS.md` が入っています（ローカル帳簿の中で作った
クラウド帳簿は空の状態で作られ、最初の `iris sync` でそのフォルダのファイルが
入ります）。同期済みの `AGENTS.md` と記帳ポリシーはそのまま取得します。
古い帳簿でガイドが不足する場合は、クローンの完了前に追加します。ローカルの
`CLAUDE.md` と `README.md` も不足していれば追加し、既存の内容は上書きしません。

```bash
iris clone [--force] <book-id> [dest]
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
  draftCount?, remoteDeleted?, packageContext?,
  sealStatus{ fiscalYear, state, source, checkedAt?, sealId?, sealedAt?, supersedesSealId? } }
```

`archive` はアーカイブフォルダのときだけ、`draftCount` は下書きを数えられたとき
だけ、`remoteDeleted` はサーバー側で帳簿が消えていると報告されたときだけ現れます。

`sealStatus` は、この年度の最後に確認できた状態をオフラインで表示します。
`closed`（締め済み）と `reopened`（再オープン済み）には、分かる範囲で締めの ID、
締め日時、引き継いだ締めの ID を含めます。`checkedAt` はサーバーからの取得、締め、
再オープンに成功したときの確認日時です。更新に失敗しても古い確認日時を保持します。
`unsealed` は最後の一覧取得時に締めがなかったことを表し、情報の不足・破損や
接続先の不一致は `unknown` です。古い形式の締め済み情報には ID や確認日時が
ない場合があります。`local-only` はクラウドの締めがないローカル帳簿、`archive` は
手元のアーカイブを表し、現在のクラウドの状態を保証しません。通信やログインは
行いません。更新には `iris sync` を使ってください。未同期のファイルは締めの
対象データと異なる場合があります。

通常の帳簿では、選択したパッケージと解決できた出典、最大3件のタスクへのリンク、
コンテキストの診断件数も表示します。JSON では `packageContext` に含めます。
`iris context` と同じ取得処理を使うオフラインの読み取りで、検証や適用可否の判定では
ありません。定義のコピーがなければ診断を示し、インストールはしません。
アーカイブではこの取得を省略します。タスクの全一覧、出典・会計ビューのエラー、
メタデータの制約は `iris context` で確認してください。

### iris validate

帳簿の構造とエントリを検証します。YAML、貸借一致、科目の存在、日付の整合、
ステータスの値、（日本の課税事業者は）税区分。

```bash
iris validate [--v] [--json] [--apply] [path]
```

`--v` は走査した全ファイルを表示、`--json` は問題と件数を出力しエラー時に 1 で終了。
`--apply` は地域オーバーレイが導いた値（ヒントとして報告されるもの。たとえば税抜経理の
帳簿で明細に含まれる消費税額）をファイルに記録してから、もう一度検証します。

Overlay の入力・計算量・出力の上限は帳簿全体で共有します。上限に達すると
`overlay.checks-incomplete` エラーになり、`--apply` は先に得た提案も書き込みません。
貸借一致などの基本の検証は続けます。検証は記録済みの候補を確認する処理で、
追加フィールドの計算を実行して修正することはありません。上限の詳細は
帳簿フォーマットリファレンスを参照してください。

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

### iris journal complete

既存の下書き仕訳を補完し、結果をプレビューします。帳簿のオーバーレイと
組み込みのルールを使います。金額だけの仕訳では、貸借を合わせる1行の金額を
`null` にできます。在庫のオーバーレイは、記録済みの数量・決済額と過去の
記帳済み取得仕訳から売却原価を計算し、損益の行を提案します。

```bash
iris journal complete [--book-path PATH] [--view NAME] [--apply] [--revision HASH] <journal>
iris journal complete journals/2026-10/2026-10-21-sale.md
iris journal complete --apply --revision <preview-revision> journals/2026-10/2026-10-21-sale.md
```

パスは帳簿からの相対パスです。`--book-path` の省略時は現在の帳簿を探し、
`--view` の省略時は既定のビューを使います。ビューを指定すると、そのビューの
行だけを更新し、共通の行と他のビューを保持します。

出力は常に JSON です。`proposal` に Markdown 全文、`allocations` に数量・原価・
ロット・適用方法、`revision` に入力と提案を識別する値を返します。
プレビューでは書き込みません。`--apply` は書き込む前に再計算し、指定した
リビジョンが古ければ拒否します。適用後も下書きで、記帳・同期は行いません。
アーカイブ帳簿と、締め済みと確認できる年度には適用できません。

Bindings v5 の定義があるパッケージでは、分類・計算の順に、未記入の追加フィールドを
先に埋められます。対象は単一の値で、元の仕訳は貸借が一致している必要があります。
JSON の `preparation_plan` と `preparation_trace` に、計算元の固定バージョン、
使った入力、提案した値を返します。適用時はフィールドごとの計算情報を
`preparation_source` に保存し、`iris validate` で帳簿内の定義から再計算できます。
記入済みの値は保持します。同じプレビューとリビジョンによる適用確認を、
ローカル MCP の `complete_journal` でも使えます。

**原価配分は先入先出法（FIFO）が既定**です。損益の計上先を
`config/book.yaml` の `inventory.params.gain_account` に一度指定します。
仕訳ごとの方法指定や、自動採番したロットの記入は不要です。
対象に一致する `inventory.params.method` を優先し、なければ期首の方法、
それもなければ FIFO を使います。`accounts.exact` と `commodity` で対象を
絞れます。売却仕訳の最小例は
[省略できる項目と自動で決まる値](book-format-reference.md#省略できる項目と自動で決まる値)
を参照してください。記録済みの金額と計算結果の不一致、決済額・手数料の未記入、
保有数量不足、期首の取得原価不明はエラーになります。
計算する金額には `null` を指定します。手数料は明記してください。
空売りと取得原価ゼロの売却には対応していません。

公開[オーバーレイリポジトリ](https://github.com/irisbooks/overlays)の
`journal-balance` と `inventory-disposal` を個別に選択します。それぞれ固定バージョンの
選択と、帳簿の `config/overlay-packages/` にあるコピーが必要です。
新規帳簿は二つを明示的にコピーして選択します。売却原価計算を外しても貸借補完は
使え、貸借補完を外しても売却原価計算は使えます。空の選択ではどちらも動作しません。
同梱版やキャッシュを実行時の代替には使いません。専門パッケージや信頼済みの帳簿独自の
定義は、同じ ID の共通補完を置き換えられます。

`iris overlay list --json` とローカル MCP の `describe_overlay` で補完ルールを
確認できます。信頼済みの帳簿ローカル定義や選択済み公開パッケージの
`completions/*.yaml` から、組み込み計算の `balance` または `inventory` を呼べます。
同じ ID の定義は組み込みルールを置き換えます。有効な提案同士が食い違う場合は
処理を止めます。選択したポリシーが取得できない場合や未信頼の場合は、先に修正が必要です。

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

### iris reconcile

`config/balance-assertions.yaml` の観測残高を、取得したローカルのルート仕訳と
元資料のハッシュで照合します。パッケージ・ログイン・通信は不要です。

```bash
iris reconcile [--json] [path]
```

出力は常に JSON です。科目・基準日・年度、金額または数量、単位と小数桁数、
記帳済みまたは明示した下書き込みの範囲、科目の通常の向き、正確な記録上・資料上の
残高と差額を、10進数と整数の文字列で返します。元資料の状態も含みます。
不一致、資料の不足・変更、入力エラーがあれば終了コードは1です。観測の一覧が空なら
照合対象はありません。書き換えや記帳は行わず、`iris validate` でも失敗を報告します。
ローカル MCP の `reconcile` も、単一帳簿・親フォルダの両モードで同じ処理を使います。
クラウドの締めプレビューでも、受け入れ済みデータに対して同じ共通処理を実行し、
未解決の観測残高があれば締めを拒否します。ローカルの変更は先に同期してください。
Overlay の判定や元資料の真正性を証明するものではありません。
[書式と一連の例](book-format-reference.md#残高照合)を参照してください。

### iris allocation

費用の全額を、根拠のある事業割合と対象期間で分けて計算します。帳簿やログインは不要で、
証拠の読み取りや書き込みは行いません。正確な入力形式は `--schema` で確認できます。
金額は文字列、精度と丸め方は明示指定です。費用の対象期間全体が一つの根拠の有効期間に
収まる必要があります。結果にはバージョンと入力の識別情報を残し、証拠は未確認と表示します。
元資料と両帳簿の対応仕訳は別途確認してください。

```bash
iris allocation --schema
iris allocation --input raw/allocation-jan.json
iris allocation --input -     # 標準入力から一つのJSONオブジェクトを読む
```

入力の上限は8192バイトです。入力の不備は終了コード1、使い方の誤りは2を返します。
取得価額の按分や記帳は行いません。
[費用の按分の例](book-format-reference.md#費用の事業分と家事分を分ける)も参照してください。

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

レポートの出力は **JSON** です（金額は最小単位の整数）。クラウドのレスポンスには、
リビジョンや鮮度などの追加情報が含まれる場合があります。
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
Balance = { account, debits, credits, type?, net }

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

`net` は数値で返し、相殺済みの科目でも `0` を省略しません。`type` があれば
科目の通常残高の向き、未分類なら `debits - credits` です。現在のCLIは、旧サーバーが
省略した `net` も補ってからJSONを出します。既存の絞り込みで残高ゼロの行全体を
除く場合はあります。`ledger.entries[].balance` はその行を反映した**後**の累計残高、`file`
は元の仕訳ファイルなので、元帳のどの行からも元の仕訳へたどれます。
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

### iris references

パスの相互参照。資料に対してはそれを引用する仕訳、仕訳に対しては引用する資料と
兄弟を表示します。

```bash
iris references [--json] <path> [path]
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
iris export assets [--year YYYY] [--out FILE] [path]
```

## 固定資産

### iris asset

固定資産の減価償却とレポート。

```bash
iris asset schedule [--year YYYY] [path]    # 各資産の償却スケジュール
iris asset depreciate --month YYYY-MM [path]  # その月の仕訳を生成（status: draft）
iris asset depreciate --year YYYY [path]      # 年度合計の仕訳を期末日付で資産ごとに生成
```

方式は会計年度ごとにどちらか一方を選びます。すでに月次仕訳がある年度への年次
実行（およびその逆）は拒否されます — 混在すると二重計上になるためです。
作成中は作業ツリーをロックし、締め済みと分かっている年度や、年度が決まった帳簿と
異なる年度への作成も拒否します。締め情報は手元の写しなので、情報がないことから
現在のクラウドでも締めていないとは判断できません。兼用資産では全額の償却仕訳を一度残し、
家事分を別に振り替える[確認済みの例](book-format-reference.md#兼用資産の取得価額を保って費用を分ける)を参照してください。

資産の計算量には上限があります。不正な償却表や上限を超えた入力はエラーになります。
[償却表の上限](book-format-reference.md#schedule-計算させるか表を記録するか)を参照してください。

## 地域オーバーレイ

### iris context

会計パッケージは、帳簿で使うフィールド・チェック・計算・ガイドをまとめたものです。
まず短いタスク一覧を確認し、必要なタスクとレコードだけを指定します。

```bash
iris context [path]
iris context --task jp-small-asset-deduction.equipment --record assets/2026/laptop.md [path]
iris context --task jp-tax-classification.classify --record journals/2026-10/purchase.md [path]
```

タスクは、帳簿が選択した固定バージョンに含まれている必要があります。
古いリリースでは案内が限定的であることを明示し、新版の情報を旧版のものとして
表示しません。出典、入力、診断、対応操作と人の判断が必要な点を分けて返します。
ローカル MCP の `get_book_context(task?, record?, view?)` も同じ内容を返します。
親フォルダモードでは `book` も必要です。`--view` は既存の会計ビューを選び、
複数指定で明示的に組み合わせられます。レコード検査は資産と仕訳が対象です。帳簿設定のタスクではレコードの指定は不要です。
参照の取得だけで、インストール・設定変更・提案の適用・記帳はしません。

リモート MCP の `get_book_context(book_id, package?, task?, field?, guide?, example?)`
は、同期済みの帳簿から参照情報だけを返します。保存されたパッケージの選択・設定、
項目・タスクの定義、受け付けたファイルのハッシュ、確認済みの帳簿リビジョン・日時を含みます。
ガイドには正確なパッケージ出典を、例にはそれを参照するタスクも指定します。
パッケージや `book:<hash>` の式はコンパイルしません。互換性・適用可否・必須条件・
会計ビューの解決・実行計画・検証・再現計算は未評価です。税の設定がなければ未設定のまま扱い、
未同期のローカル変更は含めません。参照情報は操作の許可ではなく、読み込みごとに
現在の帳簿アクセス権とトークンの範囲を確認します。

### iris overlay

地域オーバーレイは、帳簿が検証と計算に使う国固有のルール・レシピ・派生の
バージョン付きセットです。`config/book.yaml` の `overlay:` または `overlays:` で固定され、帳簿独自の
`config/overlays/` があればそれで拡張されます。

```bash
iris overlay install [--pin id@version ...] [path]                  # 固定バージョンを帳簿へコピー（選択は変更しない）
iris overlay select --pin id@version [--pin ...] [--dry-run] [--json] [--revision HASH] [path]  # 有効な組み合わせ全体を指定。--off で追加パッケージを無効化
iris overlay example <task> <file#case> [path]                      # タスクの実行可能な検証例を読む
iris overlay list [--json] [path]                                   # 適用中のオーバーレイ: 固定バージョン・層・ルール・レシピ・派生
iris overlay guide <id[#section]> [path]                                     # 固定したパッケージの手順書を読む
iris overlay recipe <id> --set name=value ... [--out <path> --apply] [path]  # レシピを実行。--apply で根拠付きで記録
iris overlay test [--json] [path]                                   # 適用中の各層のゴールデンテストを実行
iris overlay test --dir <overlay-dir> [--json]                      # 公開オーバーレイ 1 つのゴールデンテストを帳簿の外で実行
iris overlay fetch [path]                                           # 帳簿が固定したバージョンを、この iris になければダウンロードして検証
iris overlay upgrade [--to <id>@<version>] [--dry-run] [--json] [--revision HASH] [path]                   # 固定を公開済みの最新版（または --to）に移す
iris overlay trust [--source book:HASH] [path]                       # 現在の層か、保存済みの正確な独自定義をこのマシンで信頼する
```

`list --json` には、`pins`、候補値を含む `fields`、ルールの条件・検証式、
パラメーターの定義、手順書の ID が含まれます。ローカル MCP では
`describe_overlay` と `read_overlay_guide` で確認できます。複数指定の場合、
`fetch` は各パッケージの署名を検証し、`upgrade` は更新後の組み合わせ全体を
確認します。`--dry-run` は検証済みキャッシュを保存する場合がありますが、
帳簿のファイルは変更しません。既定値と科目選択の設定は
[帳簿の設定例](book-format-reference.md#帳簿ごとにルールとレシピの入力を設定する)を参照してください。

`recipe` は提案を表示します。`--apply --out PATH` を付けると、償却表のレシピは資産ファイルを
書き換え（`schedule:` + `schedule_source:`）、集計レシピは `filings/` に申告記録を
書きます。マップ型のパラメータは `--set name='{"1": 90}'` のように渡します。

`fetch` は署名を検証して配布キャッシュに保存します。`install` は同梱版または
署名済みリリースの正確な内容を `config/overlay-packages/` にコピーし、選択は
変更しません。`select` は組み合わせ全体の固定バージョン、設定、依存関係と
帳簿独自の層との互換性を確認します。省略・空リスト・`select --off` では
追加パッケージは動作せず、基本の構造・会計チェックは引き続き動作します。

#### 有効な組み合わせを変更する

`iris context` またはローカル MCP の `get_book_context` で、帳簿内にあるコピー、
有効なバージョン、タスクへの適用条件を確認できます。コピーの追加やガイドの参照だけでは
方針は有効になりません。選択は 1 回の操作で検証して適用できます。

```bash
iris overlay select --off ./books/example
```

帳簿フォルダー内で `iris diff config/book.yaml` を実行すると、最後に同期した状態からの
未同期の選択変更を確認できます。一度も同期していない場合は、ファイルが追加として
表示されます。同期済みの過去の変更はファイル履歴で確認します。適用前に定義や出典への
影響を確認したい場合は、任意でプレビューできます。

```bash
iris overlay select --off --dry-run --json ./books/example
iris overlay select --off --revision REVISION_FROM_PREVIEW ./books/example
```

別の組み合わせに変える場合は、依存先も含め、必要な固定バージョンをすべて `--pin` で
指定します。プレビューと適用結果には変更前後の選択、依存先の対応バージョン、変わるルール・
レシピ・派生・補完・項目定義・準備処理の定義が表示されます。依存先の不足、非対応の
組み合わせ、循環があれば適用できません。互換性のある組み合わせを明示して指定し、
依存先を勝手にダウンロードしたり有効にしたりすることはありません。

`affected_results` は、記録された出典が無効になる資産の償却表、申告記録、準備済みの
仕訳項目を列挙します。各行にはファイル、仕訳行番号（0 始まり。記録全体は `-1`）、
項目、保存された `source_view` 宣言が含まれます。出典の一覧であり、会計ビューを
解決した結果や再計算結果ではありません。`retained` は出典の内容を確認できたこと、
`will-retain` は現在の帳簿独自の定義と元の親バージョンを適用時に保存することを表します。
内容の存在、このマシンでの信頼、再計算の成功は別の情報です。過去の出典が不足していれば
警告しますが、選択操作で補修はしません。帳簿の集計や過去のレシピ再計算は行わず、
記録された金額や項目も書き換えません。

#### ローカル MCP で適用する

ローカル MCP では、組み合わせ全体の `pins` 配列（無効化は `[]`）を
`select_overlays` に渡すと、1 回で検証・適用し、変更内容を返します。
親フォルダーモードでは `book` も必須です。有効な組み合わせ全体を置き換えるため、
引き続き使う既存の固定バージョンもすべて含めます。プレビューとリビジョンは任意です。

事前に確認したい場合は `preview_overlay_selection` を呼び、同じ配列と返された
`revision` を `select_overlays` に渡します。CLI でも `--revision` を付ければ、
確認後の変更を検出して拒否します。適用時は同期ロックを取り、設定・定義・信頼状態・記録の追加削除・
出典を再確認します。アーカイブや、既知の締め済み設定は変更できません。締めの情報は
キャッシュなので、ローカルで変更できても最新のクラウド権限や締め状態の証明には
なりません。プレビューは実行用ファイルやキャッシュを作らず、外部にも接続しません。

現在の書き込み処理は、未解決の設定ビューや、ほかの設定を変えてしまう YAML の別名参照・
マージを拒否します。確認漏れを防ぐため、選択は 16 パッケージ、依存ファイルは
1,024 件・64 MiB、確認対象全体は 10,000 ファイル・128 MiB、出典は 2,048 件を上限とし、
影響を受ける出典は 64 種類、結果の JSON は 2 MiB を上限とします。
超過時は部分的な結果を返さず拒否します。更新操作にも同じ上限と変更前後の確認を使います。
空の選択から地域を推測して更新することはありません。

#### 選択中のバージョンを更新する

```bash
iris overlay upgrade --to id@version --dry-run --json ./books/example
iris overlay upgrade --to id@version --revision REVISION_FROM_PREVIEW ./books/example
```

`--to` は選択中のパッケージを 1 つ置き換えます。省略すると、選択中のパッケージの
公開済み最新版を確認します。依存先は互換性のあるバージョンを明示して選択する必要があり、
勝手に追加しません。指定した正確なバージョンが帳簿内にあり、内容を確認できれば
オフラインで使えます。不足時はプレビューでも署名を検証して配布キャッシュに保存する
場合がありますが、帳簿のファイルは変更しません。

プレビューには保存予定の `copies`、パッケージ自身の検証例 `golden_tests`、依存関係・
記録済みの結果への影響と、変更前後の `local_source` / `local_source_after`・信頼状態が
含まれます。検証例の成功は、利用者の帳簿の集計や記録済みの結果の再計算が成功したことを
意味しません。単一・複数の選択形式とほかの設定は保ち、帳簿独自の層の親を更新する前に、
元の内容と親バージョンを保持します。有効で信頼済みの層は、確認した親の変更だけなら
信頼を引き継ぎます。未信頼の層を勝手に有効にはしません。

ローカル MCP は `preview_overlay_upgrade(to?)` で確認し、同じ `to` と必須の `revision` を
`upgrade_overlays` に渡して適用します。親モードでは `book` も指定します。CLI も
`--revision` で確認後の変更を拒否できます。書き込みに失敗した場合、提案が書いた後に
変更されていない内容だけを戻し、ほかの編集者の変更は保ちます。確認済みの出典コピーが
先に保存されている場合はあります。中断によって信頼済みの層と親の選択が食い違った場合は、
公開パッケージの方針で代用せず実行を止めます。状態を確認し、改めて更新内容を確認してから
続けてください。

実行と過去のレシピ再計算には、帳簿内の定義だけを使います。コピーの不足・改変・
非互換・同一 ID の競合は診断として返し、地域・同梱版・キャッシュで代用しません。
`upgrade` はテストと設定を確認し、新しい定義を保存してから選択を更新します。
旧版と、元の親バージョンを含む帳簿独自の層も保持します。無効化しても既存の
フィールドや計算結果は削除しません。コピーは clone・sync で帳簿とともに移り、
参照操作が不足分を勝手にインストールすることはありません。クラウドは定義と
結果をデータとして保存し、基本の整合性・権限チェックを行います。Overlay の
式のコンパイル・評価や締め時のレシピ再計算は行いません。

#### 保存済みの過去の定義を信頼する

clone は、別のマシンの独自定義への信頼を引き継ぎません。現在の独自定義が変わった後に
記録済みの `book:HASH` を再計算するには、`config/overlay-packages/local/HASH/` に
保存された定義と元の親を確認し、このマシンで明示的に信頼します。

```bash
iris overlay trust --source book:HASH ./books/example
```

`HASH` は記録された出典の実際のハッシュに置き換えてください。保存済みの内容と
帳簿内の元の親を確認し、指定した出典だけへの信頼を記録します。パッケージの選択や
帳簿の出典は変更しません。不足・改変・シンボリックリンクがあれば拒否し、現在の定義や
配布キャッシュで過去の内容を代用しません。年度繰越では翌年度の選択を保ったまま
保存済みのコピーを引き継ぎ、コピー前に両年度を合わせた保存先の上限を確認します。

## 編集・記帳

### iris post

記帳後は、ほかの未同期変更も含む連携済み帳簿の全体を同期します。
`--local` を付けると、ローカルで記帳するだけで同期しません。

仕訳を `draft` から `posted` にして記帳し、（リンク済みなら）同期します。帳簿の
オーナーが**記帳承認**（Web アプリ → 設定）をオンにしている場合、記帳は Web
アプリ専用です。`iris post` はローカルで拒否し、サーバーも push された
ステータス変更を `APPROVAL_REQUIRED` で拒否します。
Web アプリでは保存済みのソースを確認してから承認します。送信するのは
`status: posted` と、確認したファイルのハッシュだけです。一括承認では最大32件の
ソースを先に表示し、同じハッシュを使います。その後ファイルが変わった場合は
再確認が必要です。未確認の最新版を取り直して記帳することはありません。
ブラウザーでの通常の記録の作成・編集・削除・復元はできません。修正は、オーナーが
定めた記帳方針に従ってローカルクライアントで行います。
事前に各ファイルが空でない・貸借一致であることを検証します。日付が締め済み
会計年度に入っている仕訳は拒否されます（*"FY \<n\> is sealed (closed period) —
run `iris reopen <n>` to amend it, then re-seal"*）。

```bash
iris post [--dry-run] [--local] <file>...
iris post [--dry-run] [--local] --all
```

`--all` はファイルを指名する代わりに、帳簿内のすべての `draft` 下書きを
記帳します — 自分が書いていない下書き(スマホ/コネクタ経由、メール取り込み、
自動生成の減価償却)も対象です。検証に失敗した下書きは報告のうえ下書きの
まま残ります。記帳ポリシー `auto` の帳簿での定型操作です。

記帳時は元の文書の `status` を変更し、ほかのフィールド・添付・数量・注記・
Markdown 本文を残します。YAML の字下げは変わることがあるため、スクリプトでは
文字列の書式に依存せず YAML を解析してください。仕訳の旧フィールド `source` と
`source.ref` は書き込み前に拒否します。代わりに `attachments` に
`path: raw/bank/x.csv`、`type: bank_statement`、`locator: L2` を指定すると、
1行のヘッダーに続く最初のデータレコードを指します。CSV の `L` はヘッダーや
引用符内の改行も含めた物理行の番号です。不明な単位も仕訳を変更せず拒否します。
単位は `config/book.yaml` に宣言してください。

### iris diff

push される内容 — ローカル変更と最後の同期スナップショットの差 — を表示します。
ローカルだけの帳簿でもオフラインで使え、一度も同期していない場合はファイルを追加として
表示します。同期済みの過去の変更は、ファイル履歴で確認してください。

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

同期対象は `AGENTS.md`、`config/` の `book.yaml`・`chart-of-accounts.yaml`・`rules.yaml`・`balance-assertions.yaml`、
`config/overlays/` の YAML、`config/overlay-packages/` の保持ファイル、
`journals/`・`assets/`・`notes/`・`filings/` の
Markdown、および `raw/` の原資料です。`.iris/`、競合サイドカー、OS・エディタの
一時ファイル、生成した `compiled/`、エクスポート、ローカルの `README.md`・
`CLAUDE.md` は同期しません。`AGENTS.md` は帳簿の共有方針であり、
クラウドでの変更には Owner 権限が必要です。

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
- `newRejections` / `allRejections` — 要対応レコード。`iris sync issues list
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
iris conflicts list [--json] [path]
iris conflicts resolve <path> --keep mine|cloud [path]
```

通常は手動マージで解決します（正規ファイルを編集し、サイドカーを削除し、
`iris sync`）。[トラブルシューティング](troubleshooting.md) を参照。

### iris sync issues

サーバー側拒否のローカルキューを管理します。

```bash
iris sync issues list [--json] [path]              # パス + コード + 問題を表示
iris sync issues retry [path]             # 抑制を外す。次の `iris sync` で再 push
iris sync issues retry --path <relpath> [path]   # 1ファイルのみ
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

翌年度の帳簿を作り、期首残高を繰り越します。今年度はロックされません。
締めるときは別途 `iris api seal` を実行します。1つの帳簿は1会計年度分
なので、`iris yearend` は翌年度の帳簿を独立したコピーとして、この帳簿と同じ
階層の新しいフォルダに作ります（`acme-2025` → `acme-2026`。フォルダは `--to` で
指定できます）。新しい帳簿には次のものが入ります。

- `config/` — `fiscal_year` を翌年度に進め、独自の帳簿 ID を持つ `book.yaml`、
  勘定科目表、`rules.yaml`、`config/overlays/`
- ガイド（`README.md`・`AGENTS.md`・`CLAUDE.md`）と方針のノート
  （`decisions.md`・`workflow.md`・`todos.md`・`open-questions.md`）
- 新年度の開始時点でまだ保有している固定資産
- 期首残高の仕訳。`journals/<YYYY-MM>/0000-opening-balances.md` に、新年度の
  初日の日付で `opening-balance` タグを付けて作られます。貸借対照表科目は
  期末残高のまま繰り越され（外貨・暗号資産など数量を管理している保有資産は
  数量も含めて）、収益・費用はゼロにリセットされ、当期純利益は
  `config/chart-of-accounts.yaml` で `retained_earnings: true` を付けた資本科目
  （どの科目にも付いていなければ勘定科目表で唯一の資本科目）へ折り込まれます。
  資本科目が複数あってどれにも付いていない場合は、いずれか 1 つに付けるよう
  求めて止まります。

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
iris yearend [<fiscal-year>] [--to PATH] [--carry notes,raw] [--yes] [--local | --link-existing BOOK_ID] [--dry-run] [path]
```

`--link-existing BOOK_ID` は Owner 権限のある新年度の初期クラウド帳簿を再利用します。
移動前にリンク先を確認し、設定と勘定科目表の反映が成功してから仕訳を移動します。
リンク先の権限と受信アドレスは保持し、プレビューの `copy_grants` と
`transfer_inbox` は false です。クラウド帳簿の新規作成は行いません。
`--local` とは併用できません。同じリンク済み新年度へ再実行する場合はクラウドの
設定と締めを確認して更新します。新年度の同期が成功してから旧年度を同期します。
親フォルダの MCP `yearend` でも `link_existing="<book-id>"` を使えます。

`--dry-run` は開始仕訳、移動、クラウド操作、繰越から除外する未記帳の下書き件数を
JSON で表示します。ファイルやクラウドには書き込みません。

### iris reopen

締め済み会計年度のロックを解除して修正できるようにします。サーバー上で締めの
ロックが解除されます。対象は年度内の仕訳と `config/`・`assets/`・`filings/`・
`compiled/` で、再オープン後の対象ファイルの変更は締め後の編集として恒久的に
記録されます。`raw/` と `notes/` は締めたままでも変更できます。年度の
ファイルは作業ツリーから離れていません — 締めは年度をロックするだけで、
ファイルを取り除きません — ので復元するものはありません。そのまま編集し、
`iris sync` で編集を push し、`iris api seal` で年度を再度締めてください。

```bash
iris reopen <fiscal-year> [path]
```

## 価格（純資産）

### iris networth

```bash
iris networth --books-dir ~/IrisBooks --as-of 2026-10-06
iris networth --currency JPY ~/IrisBooks/business-2026 ~/IrisBooks/personal-2026
iris networth history --books-dir ~/IrisBooks --months 12
iris networth movers --books-dir ~/IrisBooks --compare 2026-09-30
```

ローカルの記帳済み仕訳と価格記録を使い、通信せずに帳簿を横断して評価します。
親フォルダ直下の帳簿、または明示的なフォルダ一覧を選びます。
通貨が異なる場合は `--currency` が必要です。年度間のリンクを明示した帳簿は、
期首残高を照合して一続きの履歴として扱います。翌年度の期首残高は前年度の残高に
置き換わり、二重に加算しません。翌年度がない場合も最後の保有残高を引き継ぎます。
下書きは除外します。価格がない保有は簿価を使い、`unpriced` に示します。
帳簿のコピーを二重に数えないよう、重複するフォルダ・帳簿 ID は拒否します。
出力は JSON です。クラウドの集計対象設定は使いません。

### iris analytics

```bash
iris analytics export --books-dir ~/IrisBooks --out portfolio.duckdb --currency JPY
duckdb -readonly portfolio.duckdb
```

`export` は未同期の編集を含むローカルの記帳済み仕訳と価格記録から、分析用ファイルを
作ります。DuckDB CLI をインストールするか、`--duckdb /path/to/duckdb` で指定して
ください。`--books-dir` または帳簿フォルダの一覧を指定します。出力先に既存のファイルは
使えません。価格の競合がある場合は、解消してから実行してください。

ファイルには出典、仕訳の増減、保有残高の履歴、価格、不足情報と、時点評価用の
`portfolio_at` マクロが入ります。SQL やピボットで分析できます。

```sql
SELECT account, unit, valuation, cost, inventory_method FROM portfolio_at('2026-10-19', 'JPY', 0);
PIVOT journal_lines ON unit USING sum(debit-credit) GROUP BY book_id, account;
```

`iris yearend` は完全な期首ロットと取得原価を翌年度の帳簿に引き継ぎます。
各年度の帳簿は単独で使え、その会計年度の期間だけ集計に含まれます。
過去の期間を見る場合は過年度の帳簿も選びます。帳簿のない年度は空白です。
帳簿間の関係は保存せず、リンクも不要です。

取得額は現在保有する分の取得原価です。簿価、累計入金額、実現損益とは別の値です。
原価配分は FIFO が既定です。対象に一致する帳簿直下の方法指定を優先し、
指定がなければ期首在庫の方法を引き継ぎます。個別法・移動平均にも対応し、
個別法の売却ではロットを選ぶ必要があります。取得履歴や期首の取得原価が
不明なら、不明のまま表示します。`inventory_method` で保有残高ごとの方法を
確認できます。
名前付き帳簿では、現在の入力に対して承認済みの既定ビューを使い、
ビュー名と計算結果の識別子も保持します。未承認・入力変更後の結果では出力しません。

### iris financial

名前付きビューを読み取り専用で計算し、JSON の集計額と識別子を確認してから、その計算結果を保持します。

```sh
iris financial prepare --view management ./my-book
iris financial prepare --view management --apply --revision GENERATION_ID ./my-book
iris financial accept --generation GENERATION_ID ./my-book
iris report pl --view management --from 2026-01-01 --to 2026-12-31 ./my-book
```

`prepare` のビュー省略時は既定のビューを使います。`calculations/financial/` に元文書、型付きの raw 証憑参照のハッシュ、計算後の仕訳、標準計算エンジンの版と状態を保持します。承認はその識別子に対するもので、元仕訳の記帳とは別です。元文書は変更しません。ファイルの追加・削除、内容、ビュー定義、証憑が変わると、現在の入力に対する承認は無効になります。過去の計算結果は標準計算の再現に使えます。

人による記帳承認が必要な帳簿では、下書きの計算結果を保持・同期し、Web の**帳簿設定 → 会計ビューの承認**で確認します。現在の Owner/Bookkeeper のブラウザーセッションで承認できます。ローカル承認はローカル操作を記録するもので、認証済みの承認者を示しません。ローカル MCP は `preview_financial_ledger`、`retain_financial_ledger`（確認した `revision`）、`accept_financial_ledger`（`generation`）を提供し、親フォルダモードでは `book` も指定します。

承認済みレポートは1つの承認済みビューを選びます。複数ビューの合成はローカルの未承認比較用です。出力にはビュー名、計算結果の識別子、入力の最終日、未記帳の元取引数を残します。純資産・分析は各帳簿の承認済みの既定ビューを使います。年度締めは同一の入力版に対して全ビューが確定していることを確認し、承認済みのクラウド版を固定します。SQLite スキーマ2は各ビューと元の計算結果を別々に保存し、通常の表には既定ビューの金額を入れます。再開後の訂正でも、作成済みアーカイブは変わりません。

対象は標準の在庫原価計算と当年度取得資産の減価償却です。地域別 Overlay レシピや申告要件の適否は評価しません。ビュー別の期首・翌年度繰越、例外取引、期別原価配分、勘定科目表・ルールの差分は未対応です。入力・参照は1,024パス、元文書512 KiB、資産64件、計算後明細8,192行、証憑1件16 MiB・合計128 MiB、計算結果1 MiBまでです。履歴は1,024件・64 MiBまでで、上限超過時は切り詰めずに拒否します。

### iris price

10,000口当たりの基準価額、実際の口数、現金の照合と更新時点は、[投資信託の例](book-format-reference.md#投資信託の口数一部売却時点別の評価を確認する)を参照してください。

単位価格をオフラインで記録・一覧し、サーバーへ同期します。ユーザー単位（帳簿には
保存されません）。

```bash
iris price add --unit BTC --price 9850000 [--currency JPY] [--date YYYY-MM-DD] [--source S]
iris price list [--unit BTC] [--currency JPY] [--year 2026] [--json]
iris price sync [--json]
iris price conflicts [--json]
iris price resolve --unit BTC --currency JPY --date 2026-10-07 --choose local --revision 43 --edit <edit-id>
```

**出力形**。`list --json`:

```text
[ { unit, currency, date, valueMicro, source?, origin, recordedAt,
    revision?, baseRevision?, editId?, conflict?, pending? } ]
```

`valueMicro` は**1単位あたり**の値 × 1,000,000 です（¥9,850,000 のビットコインは
`9850000000000`）。`origin` は `local`（この端末で記録）か `server`。
`sync --json` は `{ pushed, pulled, conflicts }` を返します。
競合が残る場合は、他の価格の同期を進めたうえで終了コード 1 を返します。

価格は観測日の暦年ごとに `~/.config/irisbooks/prices/YYYY.jsonl` に保存します。
従来の `prices.jsonl` は初回利用時に移行し、元のファイルも残します。
同期は前回取得したページ以降の変更を取得します。過年度の価格訂正も対象です。

同じ単位・通貨・日付への編集は、価格と出典が一致すれば自動で合流します。
異なる場合は両方の候補を残します。競合が判明した価格は、ローカル集計でも
サーバーの確定値を使い、影響する保有を `priceConflicts` に示します。
推移では該当する時点、変動要因では比較する両時点に情報を添えます。
他の価格や記帳レポートの利用は続けられます。
`price conflicts --json` で確認し、表示されたサーバーの revision とローカル編集 ID
を指定して解決します。`--choose local` は次の同期で送る訂正を残し、
`--choose server` はその編集を破棄します。別の値に直す場合は local を選んでから
価格を再記録して同期します。候補が変わった後の古い解決指定は拒否されます。

## MCP サーバー

### iris mcp

1 つの帳簿、または帳簿をまとめた親フォルダに対してローカル MCP サーバーを実行します。

```bash
iris mcp serve [--book-path PATH | --books-dir PATH] [--http 127.0.0.1:PORT]
```

引数は利用中のツールの入力形式で確認してください。以下は作業ごとの案内です。

#### ローカル帳簿を選ぶ

`--books-dir` には `~/IrisBooks` などの既存の親フォルダを指定し、その直下に帳簿を置きます。
`list_books` で確認し、各操作の `book` に子フォルダ名を渡します
（例: `validate(book="freelance-2026")`）。帳簿を追加しても再起動は不要です。
帳簿名にパスは指定できず、外部を指すシンボリックリンクも拒否します。
税理士の作業では、親フォルダと認証情報の範囲を顧客ごとに限定してください。

`--book-path` は単一帳簿を扱い、各操作の帳簿指定は不要です。未作成または空の指定先は
自動作成します。2 つのフォルダ指定は併用できません。ホストと AI に見えるパスは
異なる場合があり、ファイルへのアクセス権とツールへの接続は別に必要です。

#### ローカル帳簿を作る

空の親フォルダでも利用できます。新規作成には
`create_book(book="freelance-2026", name="Acme", region="JP", fiscal_start_month=1,
fiscal_year=2026)` を使います。既存の帳簿や空でないフォルダは上書きせず、親自体も
帳簿にしません。既存のクラウド帳簿を使う場合は、先に作成せず、後述の clone を使います。

#### 記録を作成して検証する

`AGENTS.md` を読み、元資料の確認や下書き・ノートの編集には通常のファイルツールを
使います。MCP は計算、検証、専用の更新処理に使います。`validate`・`balance`・
`report`・`status`・`diff`・`complete_journal` は対象帳簿に対する操作です。
complete_journal はプレビュー後、版を確認して下書きへ適用します。`post` は対象パス、
または明示的な全下書きの処理を受け取り、記帳ポリシーとサーバーの承認条件に従います。
`dry_run=true` でプレビューできます。`local=true` は認証や同期をせずローカルで転記します。
省略時は、接続済み帳簿の全体を自動で同期し、対象仕訳以外の未同期の変更も含みます。

選択中のオーバーレイは `describe_overlay` で確認します。両モードで `list_recipes` と
`run_recipe` を使います。一覧は CLI と同じレシピ ID と入力形式を返します。
`run_recipe(recipe="jp-declining-balance.teiritsu", params={...})` で結果を確認し、
保存時は `apply=true, out="assets/2026/equipment.md"` を追加します。申告用の計算補助資料は
`filings/` 内を指定します。`out` だけでは保存せず、これらの保存指定は `params` の外に置きます。
親モードでは両ツールに `book` も指定します。償却の計算ツール、`check_update`、
`read_docs` には帳簿の指定が不要です。費用の按分計算 `allocation` も帳簿を指定せずに使えます。`read_docs` は既定でトピックや節の一覧を返し、
節を指定すると本文を読みます。不明な引数や型の誤りは実行前にエラーとなり、文字列の `"true"` は真偽値として扱いません。参照関係の確認には
ファイルツールまたは CLI の `iris references` を使います。

#### クラウドの利用を承認する

最初に `auth_status` を呼び、`signed_in` ならその認証を使います。それ以外は `login` を
呼び、ホストのブラウザでユーザーが許可した後、`auth_status` の
`status="signed_in"` を確認します。`login` は `authorization_url` と 5 分後の有効期限を
返し、許可待ちの再呼び出しでは同じ URL を返します。`auth_status` の
`validate=false` は認証情報の有無だけを調べます。

`login`・`auth_status`・`logout`・`list_cloud_books` に帳簿の指定は不要です。
認証情報はホスト内で CLI とローカル MCP の間で共有し、ツール結果には出しません。
`logout` は保存したセッションを失効し、許可待ちも取り消します。環境変数
`IRIS_API_TOKEN` があればそちらを優先します。その権限を使うか、ブラウザでの認証を
選ぶ場合はホスト設定から変数を外して再起動してください。現在のサービスの認証手順は
`/start/cloud/` にあります。

#### クラウドのミラーを作成・接続する

帳簿の識別情報を変える前に、状況を確認します。

| 状況 | ツール |
| --- | --- |
| 接続済みのローカル帳簿 | `sync(book=...)` |
| 未接続のローカル帳簿を新しいクラウドへ | `create_cloud_book(book=...)`、その後 `sync` |
| 未接続のローカル帳簿を未編集の既存クラウドへ | `list_cloud_books`、その後 `link_book(book=..., cloud_book_id=...)` |
| 既存のクラウド帳簿を手元へ | 後述の `clone_book` |

作成時はローカル帳簿の設定を使い、応答が不明な場合の再試行キーも保持します。
接続には Owner 権限、年度・地域・通貨などの一致、未編集の初期帳簿またはファイル履歴のない
接続先が必要です。設定・科目表・`AGENTS.md` を一括で採用してからローカルの接続先を変えます。
記録済み・編集済み・締め済み・同時変更された接続先は拒否します。別フォルダへ clone して
比較してください。強制指定でこの条件を回避することはできません。アーカイブと接続済み帳簿の
新規作成・接続も拒否します。同期の拒否やエラーは別途確認します。

#### 既存のクラウド帳簿を clone する

認証後に `list_cloud_books` で対象を確認し、未作成または空の子フォルダへ
`clone_book(book="freelance-2026", cloud_book_id="bk_...")` を実行します。
先に `create_book` は呼びません。同期済みファイルとポリシーを保持し、不足する案内を追加し、
同期状態とスナップショットを設定してからフォルダを公開します。通常は未同期の差分がありません。
古い帳簿に `AGENTS.md` がなければ追加し、そのファイルは初回同期の対象として残ります。

結果にはホスト側のパスと帳簿情報が含まれ、再起動せず `list_books` から見つけられます。
既存の内容、シンボリックリンク、アーカイブ、既存の `<book>.partial` は拒否します。
強制上書きはできません。clone は `--books-dir` の場合に利用できます。

#### 競合の解決と翌年度の作成

`list_conflicts` と `resolve_conflict` で競合を確認・解決します。mine を残すと直後に同期し、
cloud を残すとサイドカーを削除します。`list_conflicts` は JSON `{conflicts: [{path, local}]}`、
`list_sync_issues` は拒否の詳細を含む JSON `{records: [...]}` を返します。`retry_sync_issues` は拒否記録の
抑制を解除します。その後に明示的に同期します。削除などは事前にプレビューし、帳簿の方針に従います。

`asset_depreciate` は下書きを作ります。クラウド接続済み帳簿の `fiscal_years`・`history`・
`seal`・`reopen` には認証と対応するサーバー権限が必要です。
`seal(period="2026", dry_run=true)` は締めずに確認し、`dry_run` の省略または false は締めを実行します。親モードの
`yearend(book=..., next_book=...)` は既定でプレビューし、`dry_run=false` で実行、
`local=true` でクラウド処理を省略します。仕訳の移動、権限のコピー、受信先の移管が発生する
場合がありますが、旧年度は締めません。`link_existing` は未編集で設定の一致する翌年度帳簿だけに
接続し、既存の権限と受信先を保持します。詳しくは [年度更新](cli-reference.md#iris-yearend) を参照してください。

#### 資産価値と価格

`get_networth` はローカルの記帳済み記録を未同期の編集も含めて集計し、通信や認証は不要です。
設定ルート内の `books_dir="."` または `books=["business-2026", "personal-2026"]` を指定します。
単一帳簿モードでは兄弟フォルダを選べません。`as_of`・`currency`・
`mode="current"|"history"|"movers"`・`months`・`compare` で参照を指定し、通貨が異なる場合は
`currency` が必要です。`get_holdings` は代わりに接続済みクラウド帳簿を読みます。

`list_prices` は CLI の `iris price list` と同じく、既定でローカルのオフライン価格を読みます。
認証済みのクラウドの価格は `source="cloud"` で読みます（CLI の `iris api price list` に相当）。
`record_price` は小数点以下 6 桁以内の文字列で価格を記録し、`sync_prices` は帳簿とは別に
価格を送受信します。価格は税務用帳簿ではなくユーザー設定に保存します。クラウド一覧は
1 ページを返すので、同じ条件で `nextCursor` を渡して続きを読みます。`list_price_conflicts` で候補を
確認し、ユーザーが選んだ場合にだけ、表示された版と編集 ID で `resolve_price_conflict` を実行して
同期します。価格と出典が同じ編集は自動で合流します。`get_holdings` 以外にはローカルの帳簿指定は不要です。

#### ローカル HTTP 接続

`--http` は stdio の代わりに localhost で待ち受け、`Authorization: Bearer <トークン>` を要求します。
トークンは初回に `~/.config/irisbooks/mcp-http.token` に作成し、所有者だけが読めます。
再起動しても同じ値なのでクライアントのヘッダーは一度設定すれば使えます。ファイルを削除すると
次回起動で新しい値になり、ヘッダーの更新が必要です。

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

VM 上の AI エージェントには、スマートフォンからの承認が使えます。
VM にブラウザやパスキー、共有のダウンロードフォルダは必要ありません。

```bash
iris api login --device
# 表示された IrisBooks の URL とリクエスト番号をユーザーに伝えます。
# ユーザー自身のスマートフォンでサインインし、番号を入力してアクセス内容を確認・承認します。
iris api login --device-complete
iris api whoami
```

登録済みのパスキー、またはパスワードと認証アプリのコードでサインインできます。
パスワードや認証コードはユーザー自身のブラウザに入力し、エージェントには
渡さないでください。番号を入力するだけではアクセスは許可されません。
アカウント・権限・注意書きを確認してから承認してください。デバイス名は
アクセスを要求した側が指定したもので、本人確認済みの情報ではありません。

`--device-complete` は一度だけ状態を確認します。終了コードが 0 でも、待機の
メッセージが出た場合は未承認で、新しい資格情報は保存されていません。
再確認は 5 秒以上空けてください。`Authorized` が表示され、`whoami` が成功してから
先に進みます。リクエストは開始から 10 分で失効します。やり直すとローカルの
待機状態が置き換わるため、最新の番号を使ってください。拒否・期限切れ・完了したか
不明な場合は新しいリクエストを開始します。完了時には開始時の環境を使います。
秘密の検証値や資格情報は CLI が内部で扱うため、待機ファイルやトークンファイルを
読んだり共有したりしないでください。`iris api logout` でローカルの待機状態も解除できます。

ブラウザのダウンロード先を CLI から読み取れる場合は、認可結果をファイルで
受け取る方法も使えます。

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

### アカウントと環境を分ける

**アカウントと環境の組合せごとに専用の非公開フォルダー**を使い、Bookの外に置きます。
ログイン前に `IRISBOOKS_TOKEN_FILE` でその中のトークン保存先を指定し、完了操作と後続のCLIでも同じパスを使います。
接続先の設定、許可待ちの情報、ユーザー単位の価格データも同じフォルダーに保存されます。
同じフォルダーで `personal.json` と `business.json` に名前を分けるだけでは、これらを分離できません。
Bookのフォルダーを変えても、ログインするアカウントは切り替わりません。

POSIXシェルで、個人用の本番プロファイルを選ぶ例です。

```bash
export IRISBOOKS_TOKEN_FILE="$HOME/.config/irisbooks/profiles/personal-prod/token.json"
unset IRIS_API_TOKEN IRIS_API_ENDPOINT IRISBOOKS_APP_BASE IRISBOOKS_API_BASE
IRISBOOKS_APP_BASE=https://irisbooks.io IRISBOOKS_API_BASE=https://irisbooks.io/api iris api login --device
# Approve on your own device, then keep the same IRISBOOKS_TOKEN_FILE:
iris api login --device-complete
iris api whoami
iris api books list
```

PowerShellでも、専用フォルダーを指定します。

```powershell
$env:IRISBOOKS_TOKEN_FILE = Join-Path $HOME '.config/irisbooks/profiles/personal-prod/token.json'
'IRIS_API_TOKEN','IRIS_API_ENDPOINT','IRISBOOKS_APP_BASE','IRISBOOKS_API_BASE' | ForEach-Object { Remove-Item "Env:$_" -ErrorAction SilentlyContinue }
$env:IRISBOOKS_APP_BASE = 'https://irisbooks.io'
$env:IRISBOOKS_API_BASE = 'https://irisbooks.io/api'
iris api login --device
# Approve on your own device, then keep the same IRISBOOKS_TOKEN_FILE:
iris api login --device-complete
iris api whoami
iris api books list
```

URLはこのサービスでの例です。使うサービスの実際のapp/APIの組合せを指定してください。
フォルダー名は識別用です。接続先はURLの設定で決まります。
`Authorized` と `whoami` の成功を確認します。端末承認が許可待ちの場合は、終了コード0でも新しい認証情報は保存されません。
本人の承認画面でアカウントと権限を確認してください。別のアカウントは `.../profiles/business-prod/token.json` など別のフォルダーを選んで承認します。
元のアカウントへ戻るときは、元のパスを指定します。意図して別サービスを選ぶ場合を除き、接続先の上書き設定は解除しておきます。
認証情報や認可ファイルを `raw/`、メモ、チャット、同期対象のBookファイルに入れないでください。

クラウドAPIの接続先は、`IRIS_API_ENDPOINT`、`IRISBOOKS_API_BASE`、`IRISBOOKS_APP_BASE` に `/api` を付けたURL、
選択中のフォルダーの `config.json`、本番の既定値の順に決まります。
ログイン時のapp/APIは `IRISBOOKS_APP_BASE` と `IRISBOOKS_API_BASE` で選びます。
`IRIS_API_ENDPOINT` は後続のリクエスト用の別の上書き設定なので、残っていると別の接続先へ送られる場合があります。
ログインが成功すると、開始時に選んだ接続先が保存されます。`whoami` は実際に使うAPI接続先と認証情報を確認します。
`IRIS_API_TOKEN` があれば保存済みセッションより優先します。この場合、保存済みの別ユーザー名は表示せず、拒否されても保存済みトークンへ切り替えません。
環境変数のトークンからローカルでアカウント名は特定できません。認証の成功だけで、すべてのBook操作が許可されたことにはなりません。

認可を開始しただけでは、既存のセッションは置き換わりません。完了時に選択中のローカル認証情報が置き換わります。
以前のサーバー側セッションは自動で失効しないため、不要ならWebの「設定 → APIトークン」で取り消してください。
`iris api logout` はサーバー側の失効を試み、選択中のローカルセッションと許可待ちの情報を削除します。
失効処理が失敗した場合は警告に従い、Webで取り消します。保存済みの接続先設定と価格データは残ります。
`IRIS_API_TOKEN` は削除されないので、使うのをやめる場合は別途解除してください。
価格同期は別の接続先・ユーザーに対応付けられた保存先を拒否します。対応付けを消して混在させず、新しいプロファイル用フォルダーを使います。

ローカルMCPはホストのプロセスに指定した認証情報と環境変数を使います。Bookの設定やVM側シェルの変数では切り替わりません。
ホストのMCP登録で対象プロファイルを指定してサーバーを再起動し、`auth_status` で認証情報の出所、接続先、検証結果を確認します。
同じプロファイルを使うCLIとMCPはログインを共有します。Book・顧客ごとのアクセス分離と権限確認も必要です。

#### 保存済みの旧本番接続を切り替える

古いプロファイルでは `irisbooks.jp` が選ばれている場合があります。
ログインは認可前にapp/API、完了後にAPIの接続先を表示します。
CLIの更新だけでは、サーバー側セッションやBookのクラウド識別子は移行されません。
新しい専用プロファイルで対象サービスを承認し、`whoami` と `iris api books list` で、実際のアカウントと帳簿を確認します。
古いトークンを別サービスへコピーしたり、同じメールアドレス・Book IDだからアクセスできると判断したりしないでください。
古いプロファイルとローカルファイルのバックアップを残します。
アクセスできる既存のクラウドBookは、未作成・空のフォルダーへcloneして比較する方法を優先します。
既存のローカルBookを使う場合は、[接続の条件](cli-reference.md#iris-api-books)に従って新規作成と既存への接続を明示的に選び、
接続変更後に保持された状態、競合、同期結果を確認します。
開発・betaのプロファイルを書き換えたり、別アカウントのデータを上書きして移行済みに見せたりしないでください。
認証情報やBookが自動コピーされる手順ではありません。

### iris api books

クラウド帳簿の一覧・作成、またはローカル帳簿のリンク。

```bash
iris api books list [--json]
iris api books new [flags]
iris api books link [--force] <book-id> [path]
```

クラウド ID をまだ持たないローカル帳簿の中で `new` を実行すると、作成した帳簿が
そのフォルダに自動で link されます。`books link` と同じ効果なので、続けて
`iris sync` がそのまま動きます。クラウド帳簿はそのフォルダの `config/book.yaml`
（帳簿名、会計年度、地域、通貨、会計年度の開始月）から作られる
ため、フラグは不要です。ファイルと食い違うフラグを指定すると拒否します。作成時点の
クラウド帳簿は空で、最初の同期でフォルダ自身のファイルが push されます。
`--no-link` を付けると、これらをすべて行いません。すでに link 済みの
帳簿の中で `new` を実行した場合は拒否します。そこに2つ目のクラウド帳簿を作っても、
`iris sync` は最初の帳簿に push し続けるため、空のまま残るだけだからです。

帳簿フォルダの外で作成する場合は、少なくとも `--name` と `--fy` を指定します。

```bash
iris api books new --name "Acme Design" --fy 2026 --region JP
```

ほかに `--currency`・`--scale`・`--no-link`・`--idempotency-key` が使えます。作成時に表示される再試行キーを保存してください。
成功したか分からない場合は、同じ `--idempotency-key <key>` で再試行すると、帳簿の
重複作成を防げます。ローカル帳簿の中では、安定したローカル ID から既定のキーを
作るため、同じ帳簿での再試行には同じキーが使われます。

`books link` にはリンク先の Owner 権限が必要です。PAT を使う場合は
`role:full` スコープも必要です。リンクできるのは、未変更の初期帳簿、または
ファイル履歴がないクラウド帳簿です。会計年度・地域・通貨・小数桁数・年度開始月を
照合し、ローカルの `config/book.yaml`（単位定義を含む）、勘定科目表、`AGENTS.md` を一つの
トランザクションで反映します。ローカル ID はサーバーの成功応答後に変更します。
使用済み・編集済み・締め済み、または確認後に更新されたリンク先は拒否されます。
別フォルダへ clone して比較し、残す内容を決めてください。`--force` でも、この
確認は省略しません。応答が失われた場合は、同じ内容で再試行できます。
対応する attachment エンドポイントがない旧サーバーではローカルのリンクを変更しません。

同期状態は `.iris/sync/binding.json` に記録した API 接続先とクラウド帳簿 ID の組で
管理します。どちらかの変更時や、接続先を確認できない旧形式の状態を開く際には、
旧 `.iris/sync/` 全体を `.iris/sync-before-link-<suffix>/` に保存して新しく始めます。
保存先にはキュー・受領情報・カーソル・要確認記録・スナップショット・設定と締めの
オフライン情報が含まれます。復旧時は内容を確認し、別の接続先へ旧受領情報を
コピーしないでください。ID の書き込みに失敗した場合は旧状態を復元します。
同じ接続先と ID では状態を保持します。同期・リンク処理中は帳簿をロックするため、
ほかの処理が終了してから再試行してください。ローカル ID と帳簿ファイルは保持します。
オフラインの差分・確認処理は現在の接続先に一致する状態だけを参照します。
接続先を変えた後は `iris sync` で新しい基準を作ってください。
クラウド帳簿の会計年度は固定です。別の年度には別の帳簿を使います。

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

ユーザー単位の設定を表示・変更します。集計通貨は複数帳簿のレポートに使います。
既定の単位と小数桁数は新規帳簿用のひな形で、ログイン済みの `iris init` が
取得できれば `config/book.yaml` に取り込みます。既存の帳簿には反映されません。
既定の単位がなければ、単位リストが空の帳簿を作成します。既知の通貨には
内蔵の小数桁数を使います。ひな形で数量の桁数を上書きしたり、独自単位を登録できます。
`--remove-unit` はひな形から単位を削除します。既存帳簿の単位は削除しません。
`iris init --no-user-defaults` でひな形の取り込みを省略できます。

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
iris api grants invite --role BOOKKEEPER --email EMAIL <book-id>
iris api grants role --role OWNER|BOOKKEEPER|REVIEWER <book-id> <user-id>
iris api grants revoke <book-id> <user-id>
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

会計年度を締めます（seal）。サーバーが年度内の仕訳と `config/`・`assets/`・
`filings/`・`compiled/` を**ロック**します。`raw/` と `notes/` は引き続き変更できます。
ローカルのファイル自体は編集できますが、ロック対象の変更は同期できません。
年度のファイルは作業ツリーにそのまま残ります。締め済み年度を修正するには
`iris reopen <fy>` を実行します — 再オープン中のロック対象の変更は監査証跡（`iris api
history`）にフラグ付きで記録されます — 修正が終わったらこのコマンドを再実行して
年度を再度締めます（新しい締めが古い締めを引き継ぎます）。`--dry-run` は、
締めでロックされるファイルの一覧を表示するだけで、何も締めません。
年度内に `draft` の下書きが残っている場合、締めは**拒否**されます —
締めた年度は完全に整理されていなければなりません。年度に属する仕訳なら先に
記帳し、不要なら削除し、翌期のものなら日付を開いている年度へ変更してください。
`--dry-run` がブロックしているドラフトを一覧表示します。

同期して締める前に、ローカルで `iris validate` を実行してください。
Overlay のルール検証と保存済みレシピの再計算は、帳簿内に保持した定義を使って
ローカルで行います。クラウドはこれらを実行せず、検証済みであるとも保証しません。
`config/balance-assertions.yaml` がある場合、`--dry-run` は同期済みデータに対する
共通処理の結果として、帳簿残高・確認残高・差額、対象範囲、証拠ファイルの確認状況を
表示します。残高や証拠の不一致が残ると締められません。元の記録や残高確認の設定を
ローカルで修正し、証拠を確認してから同期し、プレビューをやり直してください。
未同期の変更は対象外です。同期後も元文書の参照データの不足・古さを報告する場合は、
サーバー側での再構築が必要です。[Discordコミュニティ](https://discord.gg/wZDsv9gyb9)で相談してください。

```bash
iris api seal --period YYYY [--type yearly] [--dry-run] <book-id>
```

### iris api balance / holdings / history

```bash
iris api balance [--as-of YYYY-MM-DD] <book-id>              # サーバー側試算表（JSON 出力）
iris api holdings [--as-of YYYY-MM-DD] [--json] <book-id>    # 単位ごとの純ポジション
iris api history [--path PATH] [--from D] [--to D] [--all] [--limit N] [--json] <book-id> # 訂正・削除の履歴
```

**出力形:**

```text
balance   [ { account, debits, credits, type?, net } ]
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

`books list --json` は `bookId`・`fiscalYear`・`role`・`name`・`region`・`currency`
を持つ一覧を出力します。他のクラウドコマンドの `--json`（`grants list`・`token list`・
`inbox show`・`inbox quarantine`）は、サーバーのレスポンスをそのまま通します。

### iris api export

```bash
iris api export [--out DIR] [--year YYYY] [--as-of YYYY-MM-DD] <book-id>  # CSV 群
```

`--year` を指定すると、その会計年度に属する仕訳のみがエクスポートされます。
締め済み年度もファイルはライブツリーに残っているため、他の年度と同じように
エクスポートされます。

### iris api price / networth

```bash
iris api price add --unit BTC --price 9850000 [--date YYYY-MM-DD] [--source S] [--revision N]
iris api price list [--unit BTC] [--currency JPY] [--year 2026] [--page] [--limit 500] [--cursor C] [--json]
iris api networth --book-id <book-id> [--as-of YYYY-MM-DD] [--json]
```

`iris api price list` は既定で全ページを取得します。`--page` は
`{ items, nextCursor, syncCursor, hasMore, userId }` を返します。
同じ条件で `--cursor` に `nextCursor` を渡して続きを取得します。
ページ件数は 1〜1000 です。各価格には `revision` が含まれます。
新規登録は revision 0、既存価格の訂正は表示された revision を
`add --revision N` に渡します。古い revision からの異なる訂正は競合になり、
価格と出典が一致する再送は確定済みの値を返します。

`iris api networth` は指定したクラウド帳簿 1 冊だけを評価します。
帳簿横断の合計・推移・変動要因・集計対象設定は CLI から削除しました。
横断集計にはローカルの `iris networth` または Web アプリを使います。
Web とリモート MCP のクラウド横断集計は、ユーザーごとに UTC 日付あたり
最大1回自動生成する共通スナップショットを使います。日付や帳簿の選択を変えても、
再生成はしません。同期済みの変更を今すぐ反映するには、Web アプリのダッシュボード
または純資産で「**集計を実行**」を選びます。集計時点と次回の自動更新時刻が応答に含まれます。

## 環境変数

| 変数 | 用途 |
| --- | --- |
| `IRIS_API_TOKEN` | パーソナルアクセストークン。キャッシュ済みログイントークンより優先 |
| `IRISBOOKS_TOKEN_FILE` | トークンの保存先。アカウントと環境の組合せごとに専用フォルダーを使う（既定: `~/.config/irisbooks/token.json`） |
| `IRIS_BOOK` | クラウドコマンドの既定帳簿 ID（位置引数があればそちらが優先） |
| `IRIS_API_ENDPOINT` | API エンドポイントの上書き。以下のすべてより優先 |
| `IRISBOOKS_APP_BASE` | アプリのベース URL（既定 `https://irisbooks.io`） |
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
