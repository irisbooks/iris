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
- `clone`・`sync`・`seal`・`reopen` は通信します。`post` は記帳後に連携済みの帳簿全体を
  同期し、`--local` を付けると同期を省略します。連携済み帳簿の `yearend` は、
  `--local` を選ばない限り翌年度のクラウド帳簿を作成・同期します。
  `price sync`、パッケージのダウンロード、`update` も通信します。

コマンドのフラグと引数は、お使いのバージョンの `iris <command> --help` が基準です。
このリファレンスでは、動作、出力の形、複数のコマンドにまたがる手順を説明します。
`--full` を付けると、そのページと配下のページをまとめて表示します
（`iris report --help --full`。`iris --help --full` は全コマンド）。`--json` を付けると、
ページをデータとして返します（各ページの本文、フラグの名前と値を取るかどうか、サブコマンド）。
ヘルプは帳簿・ログイン・通信なしで動き、標準出力に表示して終了コード 0 を返します。
フラグは引数の前後どちらにも置けます。`--` 以降はフラグとして解釈しません。
真偽値を明示する場合は `--flag=true` または `--flag=false` と書きます。
`--json false` のように値を分けて書くと、この書き方を示してエラーになります。

計算・修復（`journal complete`・`organize`・`financial prepare`・`overlay recipe`、
`validate` の導出値）は、`--apply` を付けたときだけ書き込みます。レシピには
`--out PATH`、計算結果の保存には確認済みの `--revision` も必要です。
`post`・`yearend`・`overlay select`・`overlay upgrade`・`seal` は指定した操作を
実行し、`--dry-run` を付けると変更せずに確認できます。`yearend` は翌年度の帳簿に
残高を繰り越します。今年度のロックは別途 `seal` で行い、修正時は `reopen` で
解除します。

コマンドは結果をテキストで表示します。多くのコマンドは `--json` を付けると、同じ結果を
1つの JSON として出力します。テキストはその JSON から作るので、両者は同じ値を同じ名前で
持ちます。値は `名前: 値`、レコードの一覧は金額を右にそろえた表、入れ子のレコードは
字下げで表します。`allocation --schema` は入力の JSON Schema を出力します。
結果は標準出力、エラーは標準エラー出力に出します。終了コードは成功が 0、
処理・検証の失敗が 1、引数・設定の誤りが 2、同期の切断が 3 です。

コマンド名は `journal complete`・`references`・`sync issues` に統一し、旧名の
`autocomplete`・`show`・`attention` は削除しました。フォルダ指定には
`--book-path` を使い、曖昧だった `--book` は削除しました。締めの確認は
`seal --dry-run`、計算結果の書き込みは `validate --apply`・
`financial prepare --apply`・`overlay recipe --out PATH --apply` を使います。

`--json` で出力する結果には共通の約束があります。日付は `YYYY-MM-DD` の文字列、
出力は2スペースインデントで整形されます。**金額は帳簿通貨の10進数の文字列**で、
仕訳ファイルと同じ書き方です（`"54.99"`、¥1,200 なら `"1200"`）。結果から写した
数字は、そのまま仕訳やコマンドの引数に戻せます。金額を含む結果は `currency` と
`currencyScale`（帳簿の小数点以下の桁数）を併記します。数量はその単位の桁数の
10進数（ビットコイン半分なら `"0.5"`）、価格は1単位あたりの10進数
（`"9850000"`）です。行を足し合わせたくなる結果には、合計が最初から入っています。
以下の出力形はキーの骨組みで書いてあり、`?` は値が空のとき省略されるキーです。

CLIとローカルMCPのJSON結果は、**lowerCamelCase** に統一しています。
例は `fiscalYear`、`commonCompletions`、`referenceData`、`newPath`、`localSha`、
`detectedAt`、`versionId`、`sizeBytes` です。以前のsnake_caseの結果キーは
置き換えたため、スクリプトも新しい名前に更新してください。

辞書のキー、パッケージの項目、レシピのパラメーター、元資料、JSON入力スキーマは、
定義された名前を使います。たとえば按分結果は `grossAmount` と `inputSha` を使い、
結果内の `input` は再計算できるように、入力形式の `schema_version` と
`gross_amount` を保ちます。CLIフラグ、MCPの入力引数、保存済み帳簿ファイル、
RESTとリモートMCPの通信形式も、それぞれ記載された名前を使います。

## 帳簿と会計年度

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
| `--region` | 地域コード（ISO 3166-1 alpha-2）。対応する地域は `iris init --help` に表示されます。必須で、既定値はありません |
| `--preset` | 用途: `personal`（家計の勘定科目）/ `business`（事業用。既定）。法人・個人事業の区分や税務上の取扱いは別に設定 |
| `--language` | 言語（ISO 639-1） |
| `--chart` | 勘定科目テンプレートの種類（地域に複数ある場合。`iris init --help` に表示されます）。専用の勘定科目表が無い地域では、特定の国に依存しない最小構成の勘定科目表になります |
| `--currency` | 通貨（ISO 4217）。省略時は地域の通貨 |
| `--fiscal-start-month` | 会計年度開始月 1〜12（既定は 1 月。4 月に始まる年度なら `4`） |
| `--fiscal-year` | この帳簿が扱う会計年度（YYYY。既定は今日を含む年度）— 前年度の申告をこれから済ませる場合は前年度など |
| `--sample` | 事業用の勘定科目に対応するデモ仕訳を約40件追加。personal では利用不可 |
| `--posting` | AGENTS.md に書き込む記帳ポリシー: `approve`(既定 — あなたが確認して記帳)/ `auto`(検証を通った仕訳をアシスタントが自動記帳) |
| `--book-id` | 既存のサーバー帳簿に事前リンク（上級） |
| `--no-user-defaults` | アカウントの既定の単位を新しい帳簿に反映しない（オフライン・再現可能な作成） |

対話形式の初期設定、親フォルダの MCP `create_book`、Web・API の明示的な新規作成は、
同じ作成処理を使います。personal は共通パッケージと家計の勘定科目、business は共通・
地域パッケージと事業用の勘定科目を選びます。選んだパッケージは、まず固定バージョンのコピーを帳簿に保存し、そのあとで選択内容を
帳簿設定に書き込みます。設定内の `creation` は作成時のプリセットと版の記録です。
編集・複製・年度更新では帳簿の実際のファイルを使い、プリセットを適用し直しません。
税務上の適用条件、証拠資料、勘定科目の対応は、初期設定の案内に従って別に判断します。
初期化後は、選択したパッケージと解決できた出典、最大3件のタスクへのリンクも表示します。
タスクへのリンクは `iris context` と同じ処理で取得します。古い版のパッケージにタスクの
情報がない場合は、案内が限られることを表示します。新しい版にしかないタスクを、古い版の
ものとして表示することはありません。

新しいクラウド帳簿にも、`iris api books new --preset personal --name "家計" --fy 2026 --region JP`
で同じ設定を使えます。新規作成時は `--chart` と `--language`
も指定できます。既存のローカル帳簿をクラウドに接続する場合は、ローカル帳簿の実際の設定・勘定科目表・
記帳方針をそのまま使います。プリセットで上書きする指定は拒否します。クラウドでの作成を
再試行した場合も、サーバーは最初に保存した初期ファイルとそのハッシュを使い続けます。
接続のときは、サーバー側の初期ファイルとその変更履歴を確認してから、クラウド側の設定・
勘定科目表・記帳方針をローカル帳簿のものに置き換えます。

### iris clone

クラウドの帳簿をこのパソコンにダウンロードします。`iris init` が帳簿を新しく作るのに対し、
`iris clone` はすでにクラウドにある帳簿を手元に取得します。サインインが
必要です。Web アプリや、帳簿フォルダの外で実行した `iris api books new` で
作ったばかりの帳簿でもすぐに使えます。これらの帳簿には、最初から
`config/book.yaml`、ひな形の勘定科目表、`AGENTS.md` が入っています（ローカル帳簿の中で作った
クラウド帳簿は空の状態で作られ、最初の `iris sync` でそのフォルダのファイルが
入ります）。同期済みの `AGENTS.md` と記帳ポリシーはそのまま取得します。
古い帳簿でガイドが不足する場合は、クローンの完了前に追加します。ローカルの
`CLAUDE.md` と `README.md` も不足していれば追加し、既存の内容は上書きしません。

```bash
iris clone [--force] [--json] <book-id> [dest]
```

`dest` を省略すると、帳簿名と会計年度からフォルダ名を付けます（`Acme-2026`、
`サンプル商店-2026`）。`iris yearend` が引き継ぐのと同じ名前です。ダウンロードの
進み具合は2秒ごとに標準エラー出力に出し、完了時の要約には帳簿名・会計年度・
取得先のフォルダが出ます。クローンは帳簿の締めと設定も読み込むので、最初の同期の
前から、締め済みの年度は編集を受け付けず、`iris status` にも締めが表示されます。

**出力形**（`--json`）:

```text
{ status, bookId, name?, fiscalYear?, path?, files, bytes, guidesAdded[],
  error?, errorDetail?{ kind, status?, retryable, phase?, elapsedMs? } }
```

`status` は `ok` か `error` です。`--json` を付けても、拒否や失敗のときの終了コードは変わりません。このとき JSON には、
[`iris sync`](#iris-sync) と同じく `error` が入ります。リクエストが失敗した場合は
`errorDetail` も入ります。`path` は絶対パスです。

### iris status

帳簿の識別情報、会計年度開始、アーカイブのフラグと、`draft` 下書きの件数を表示します。

```bash
iris status [--json] [path]
```

**出力形**（`--json`）:

```text
{ name, bookId, region, language, currency, fiscalStartMonth,
  archived, archive?{ sourceBookId, fiscalYear },
  draftCount?, remoteDeleted?, packageContext?,
  sealStatus{ fiscalYear, state, source, checkedAt?, sealId?, sealedAt?, supersedesSealId?, reason? } }
```

`archive` はアーカイブフォルダのときだけ、`draftCount` は下書きを数えられたとき
だけ、`remoteDeleted` はサーバー側で帳簿が消えていると報告されたときだけ現れます。

`sealStatus` は、この年度について最後に確認できた締めの状態です。`iris status` は
通信もログインもしないので、表示するのは手元に保存した情報です。最新の状態にするには
`iris sync` を実行してください。

- `closed`（締め済み）と `reopened`（再オープン済み）には、分かる範囲で締めの ID、
  締め日時、引き継いだ締めの ID が入ります。古い形式の締め済み情報には、ID や
  確認日時がない場合があります。
- `unsealed` は、最後に一覧を取得した時点で締めがなかったことを表します。
- `unknown` は、情報が不足しているか壊れている、または接続先が一致しないことを
  表します。`reason` に理由と更新方法が入ります。
- `checkedAt` は、サーバーからの取得、締め、再オープンに成功したときの確認日時です。
  更新に失敗しても、前回の確認日時を保持します。
- `local-only` は、クラウドの締めがないローカル帳簿です。
- `archive` は手元のアーカイブの記録で、現在のクラウドがまだ締め済みかどうかは
  示しません。

クローンは完了前に締めを読み込みます。未同期のファイルは、締めの対象になったデータと
異なる場合があります。

通常の帳簿では、選択したパッケージと解決できた出典、最大3件のタスクへのリンク、
コンテキストの診断件数も表示します。JSON では `packageContext` に含めます。
`iris context` と同じ取得処理を使うオフラインの読み取りで、検証や適用可否の判定では
ありません。定義のコピーがなければ診断を示し、インストールはしません。
アーカイブではこの取得を省略します。タスクの全一覧、出典・会計ビューのエラー、
メタデータの制約は `iris context` で確認してください。

### iris yearend

翌年度の帳簿を作り、期首残高を繰り越します。今年度はロックされません。
締めるときは別途 `iris seal` を実行します。1つの帳簿は1会計年度分
なので、`iris yearend` は翌年度の帳簿を独立したコピーとして、この帳簿と同じ
階層の新しいフォルダに作ります（`acme-2025` → `acme-2026`。フォルダは `--to` で
指定できます）。新しい帳簿には次のものが入ります。

- `config/` — `fiscal_year` を翌年度に進め、独自の帳簿 ID を持つ `book.yaml`、
  勘定科目表、`rules.yaml`、`config/overlays/`
- ガイド（`README.md`・`AGENTS.md`・`CLAUDE.md`）と方針のノート
  （`decisions.md`・`workflow.md`・`todos.md`・`open-questions.md`）
- 新年度の開始時点でまだ保有している固定資産
- 期首残高の仕訳。`journals/<YYYY-MM>/0000-opening-balances.md` に、新年度の
  初日の日付で `opening-balance` タグを付けて作られます。貸借対照表の科目は、期末残高をそのまま繰り越します。外貨や暗号資産など数量を管理
している保有資産は、数量も繰り越します。収益と費用はゼロに戻します。当期純利益は、
`config/chart-of-accounts.yaml` で `retained_earnings: true` を付けた資本科目に
振り替えます。どの科目にも付いていない場合は、勘定科目表にある唯一の資本科目に
振り替えます。
  事業主の科目（`owner: true`）も新年度はゼロから始まり、その残高は同じ資本科目へ
  折り込まれます。事業主の資本は、利益と持ち込みの分だけ増え、引き出しの分だけ減ります。
  資本科目が複数あってどれにも付いていない場合は、いずれか 1つに付けるよう
  求めて止まります。
- `config/prior-year.yaml`。前期の科目ごとの数字（期首残高と各月の記帳済の合計）で、
  新しい帳簿の損益計算書と貸借対照表は、これだけで前期と比較できます
  （`--compare prior-year`）。新しい帳簿で `iris validate` を実行すると、このファイルと
  期首残高の仕訳が一致するかを確かめます。資産・負債の各科目は、前期末の残高が期首残高の仕訳の金額と一致する必要があります。
純資産は、前期の利益を含めた合計が、期首残高の仕訳の純資産の合計と一致する必要があります。
  一致しない場合（どちらかを編集した、前期を修正したなど）は警告になります。前期の
  帳簿で `iris yearend` を実行し直すと、両方が書き直されます。

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
そのまま残ります。新年度を締めたあとは、期首残高の仕訳はその時点の内容のまま固定されます。再実行して
結果が食い違った場合は、対処方法とともに不一致を報告し、仕訳を黙って書き換えることは
ありません。前年度の日付の下書きが残っている場合は警告します。下書きは繰越に
含まれません。

`<fiscal-year>` は省略できます。既定は帳簿の `fiscal_year` で、それ以外の年度を
指定すると拒否されます。

```bash
iris yearend [<fiscal-year>] [--to PATH] [--carry notes,raw] [--yes] [--local | --link-existing BOOK_ID] [--dry-run] [path]
```

`--link-existing BOOK_ID` を付けると、翌年度のクラウド帳簿を新しく作らず、作成したまま
手を加えていない既存のクラウド帳簿を使います。あなたがオーナーである帳簿に限ります。
移動前にリンク先を確認し、設定と勘定科目表の反映が成功してから仕訳を移動します。
リンク先の権限と受信アドレスは保持し、プレビューの `copyGrants` と
`transferInbox` は false です。クラウド帳簿の新規作成は行いません。
`--local` とは併用できません。同じクラウド帳簿を指定して再実行した場合は、そのクラウド側の設定と締めを確認してから
更新します。同期は新年度の帳簿が先で、成功してから旧年度の帳簿を同期します。
親フォルダの MCP `yearend` でも `link_existing="<book-id>"` を使えます。

`--dry-run` は、期首残高の仕訳、移動する仕訳、クラウド操作のプレビューと、繰越から
除外される下書きの件数を表示します（`--dry-run --json` なら JSON）。ファイルやクラウドには書き込みません。

### iris seal

連携済み帳簿のクラウド上の会計年度を締めます（seal）。サーバーは、日付がその年度内か、それより前の仕訳を**ロック**します。年度より前の日付の
仕訳もロックするのは、その年度の貸借対照表を変えてしまうためです。`config/`・`assets/`・
`filings/`・`compiled/` もロックします。`raw/` と `notes/` は
引き続き変更できます。ローカルのファイル自体は編集できますが、ロック対象の変更は
同期できません。年度のファイルは作業ツリーにそのまま残ります。締め済み年度を修正するには、まず `iris reopen <fiscal-year>` を実行します。再オープン中に
ロック対象を変更すると、その変更は訂正・削除の履歴（`iris api history`）に印付きで
記録されます。修正が終わったら、もう一度 `iris seal` を実行して年度を締めます。
新しい締めが古い締めに代わり、古い締めも履歴に残ります。
`--dry-run` は、締めでロックされるファイルの一覧を表示するだけで、何も締めません。
年度内に下書きが残っている場合、締めは**拒否**されます — 締めた年度は完全に
整理されていなければなりません。年度に属する仕訳なら先に記帳し、不要なら削除し、
翌期のものなら日付を開いている年度へ変更してください。`--dry-run` が締めを妨げて
いる下書きを一覧表示します。

同期して締める前に、ローカルで `iris validate` を実行してください。
オーバーレイのルール検証と保存済みレシピの再計算は、帳簿内に保持した定義を使って
ローカルで行います。クラウドはこれらを実行せず、検証済みであるとも保証しません。
`config/balance-assertions.yaml` がある場合、`--dry-run` は同期済みのデータで残高を照合し、
帳簿上の残高、資料上の残高、差額、対象範囲、証拠ファイルの確認状況を表示します。残高や証拠の不一致が残ると締められません。元の記録や残高確認の設定を
ローカルで修正し、証拠を確認してから同期し、プレビューをやり直してください。
未同期の変更は対象外です。同期したあとも、サーバー側のデータが不足している、または古いと報告される場合は、
サーバー側でデータを再構築する必要があります。[Discordコミュニティ](https://discord.gg/wZDsv9gyb9)で相談してください。

```bash
iris seal [--dry-run] <fiscal-year> [book-path]
```

連携済み帳簿のフォルダで実行するか、`--book-path` を指定します。その帳簿の
クラウド側を締めます。ローカル MCP の `seal` ツールも、選んだ帳簿に同じ操作をします。

### iris reopen

締め済み会計年度のロックを解除して修正できるようにします。サーバー上で締めの
ロックが解除されます。対象は年度内の仕訳と `config/`・`assets/`・`filings/`・
`compiled/` で、再オープン後の対象ファイルの変更は締め後の編集として恒久的に
記録されます。`raw/` と `notes/` は締めたままでも変更できます。締めは年度をロックするだけで、ファイルを取り除きません。年度のファイルは作業ツリーに
残っているので、復元の作業は不要です。そのまま編集し、
`iris sync` で編集を push し、`iris seal <fiscal-year>` で年度を再度締めてください。

```bash
iris reopen <fiscal-year> [path]
```

## 記帳と会計ルール

### iris validate

帳簿の構造とエントリを検証します。YAML、貸借一致、科目の存在、日付の整合、
ステータスの値、帳簿で選択したオーバーレイのルール。

```bash
iris validate [--v] [--json] [--apply] [path]
```

`--v` は走査した全ファイルを表示、`--json` は問題と件数を出力しエラー時に 1 で終了。
`--apply` は選択したオーバーレイが導いた値（ヒントとして報告されるもの。たとえば
パッケージが明細ごとに計算する税額）をファイルに記録してから、もう一度検証します。

オーバーレイの入力・計算量・出力の上限は帳簿全体で共有します。上限に達すると
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

既存の仕訳を、下書き・記帳済を問わず、帳簿が選択したパッケージの補完で補い、結果を
プレビューします。計算したい金額は `null` にします。各パッケージが何を補完するかは
[オーバーレイのドキュメント](https://irisbooks.io/docs/ja/overlays/)で確認できます。

```bash
iris journal complete [--book-path PATH] [--view NAME] [--completion ID] [--apply] [--revision HASH] <journal>
iris journal complete journals/2026-10/2026-10-21-sale.md
iris journal complete --apply --revision <preview-revision> journals/2026-10/2026-10-21-sale.md
iris journal complete --completion <completion-id> journals/2026-10/2026-10-21-sale.md
```

パスは帳簿からの相対パスです。`--book-path` の省略時は現在の帳簿を探し、
`--view` の省略時は既定のビューを使います。ビューを指定すると、そのビューの
行だけを更新し、共通の行と他のビューを保持します。

結果には次のキーが入ります（`--json` なら JSON）。

- `proposal` — 提案する仕訳の Markdown 全文
- `allocations` — 数量、原価（仕訳と同じ10進数）、ロット、適用方法
- `balanced` — 貸借を一致させる金額を入れた行
- `name`・`description` — 補完ルール自身の短い名前と、計算内容の説明
- `overlayName` — 帳簿独自のレイヤーの名前
- `policy` — 適用した在庫の方針とその説明
- `reasons` — 提案がその金額にした理由（行ごと）
- `revision` — 入力と提案を識別する値

仕訳を変えない補完ルールは、仕訳を変える
ルールと競合しません。
プレビューでは書き込みません。`--apply` は書き込む前に再計算し、指定した
リビジョンが古ければ拒否します。仕訳の状態は変えず、同期も行いません。
アーカイブ帳簿と、締め済みと確認できる年度には適用できません。記帳承認が
オンの帳簿では、記帳済の仕訳にも適用できません。

提案できないときは終了コード1で、`refusal.reason` と `refusal.message` を
含む拒否の内容を出力します。理由（`refusal.reason`）は次のいずれかです。

- `completeSeveral` — `null` の金額が複数ある
- `completeQuantity` — 数量のある行には金額が必要
- `completeUnbalanced` — `null` がなく貸借が一致しない
- `completeZero` — 未記入の金額が0になる
- `completeSide` — `null` の金額が貸借の反対側にある
- `completeAccount` — 勘定科目表にない科目がある
- `year` — 日付が会計年度外
- `completeNone` — 適用できる補完ルールがない
- `completeConflict`、`completeNotChosen` — 後述
- `completeOther` — エンジンの理由を `message` に含む

`completeConflict` は
帳簿の補完ルール同士で結果が異なる場合で、`choices` にそれぞれの完全な
プレビューを返します。`--completion ID` でどれかを選ぶと、プレビューと
`--apply` の両方でその提案を使います。提案が1つしかないときに `--completion` を指定する場合は、その提案を出したルールの ID を
指定します。別のルールを指定すると `completeNotChosen` になります。
選択を自動で行うことはありません。

パッケージが対応していれば（Bindings v5 の定義があるパッケージ）、金額の補完の前に、
未記入の追加フィールドも埋められます。分類、計算の順に処理します。埋められるのは値が
1つのフィールドだけで、元の仕訳の貸借が一致している必要があります。
結果の `preparationPlan` と `preparationTrace` に、計算元の固定バージョン、
使った入力、提案した値を返します。適用時はフィールドごとの計算情報を
`preparation_source` に保存し、`iris validate` で帳簿内の定義から再計算できます。
記入済みの値は保持します。同じプレビューとリビジョンによる適用確認を、
ローカル MCP の `complete_journal` でも使えます。

補完は、帳簿が選択したパッケージからのみ提供されます。それぞれ帳簿の
`config/overlay-packages/` にある固定バージョンのコピーが必要で、新規帳簿は共通の
パッケージを選択します。空の選択ではどれも動作せず、同梱版やキャッシュを代替には
使いません。専門パッケージや信頼済みの帳簿独自の補完は、同じ ID の共通補完を
置き換えられます。

`iris overlay list --json` とローカル MCP の `describe_overlay` で補完ルールを
確認できます。信頼済みの帳簿ローカル定義や選択済み公開パッケージの
`completions/*.yaml` から、組み込み計算の `balance` または `inventory` を呼べます。
同じ ID の定義は組み込みルールを置き換えます。有効な提案同士が食い違う場合は
処理を止めます。選択したポリシーが取得できない場合や未信頼の場合は、先に修正が必要です。

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
ブラウザでの通常の記録の作成・編集・削除・復元はできません。修正は、オーナーが
定めた記帳方針に従ってローカルクライアントで行います。
事前に各ファイルが空でない・貸借一致であることを検証します。日付が締め済み
会計年度に入っている仕訳は拒否されます（*"FY \<n\> is sealed (closed period) —
run `iris reopen <n>` to amend it, then re-seal"*）。

```bash
iris post [--dry-run] [--local] <file>...
iris post [--dry-run] [--local] --all
```

`--all` はファイルを指名する代わりに、帳簿内のすべての `draft` 下書きを
記帳します。ほかの共同作業者が書いた仕訳や、自動生成の減価償却も対象です。
検証に失敗した下書きは報告のうえ下書きの
まま残ります。記帳ポリシー `auto` の帳簿での定型操作です。

記帳時は元の文書の `status` を変更し、ほかのフィールド・添付・数量・注記・
Markdown 本文を残します。YAML の字下げは変わることがあるため、スクリプトでは
文字列の書式に依存せず YAML を解析してください。仕訳の旧フィールド `source` と
`source.ref` は書き込み前に拒否します。代わりに `attachments` に
`path: raw/bank/x.csv`、`type: bank_statement`、`locator: L2` を指定すると、
1行のヘッダーに続く最初のデータレコードを指します。CSV の `L` はヘッダーや
引用符内の改行も含めた物理行の番号です。不明な単位も仕訳を変更せず拒否します。
単位は `config/book.yaml` に宣言してください。

### iris reconcile

`config/balance-assertions.yaml` に記録した残高（通帳の期末残高、現金の実査額など）を、
帳簿とオフラインで照合します。

```bash
iris reconcile [--json] [path]
```

結果には、`config/balance-assertions.yaml` に記録した残高の1件ごとに、帳簿上の残高、
資料上の残高、差額、元資料のファイルが記録時と同じかどうかが入ります。不一致、資料の不足・変更、入力エラーがあれば終了コードは1です。
ファイルがない場合や一覧が空の場合は、照合するものはありません。書き換えや記帳は行わず、
`iris validate` でも同じ失敗を報告します。クラウドで年度を締めるときも、同期済みのデータで同じ照合を行います。一致しない残高が
残っていると締めを拒否されるので、締める前に同期してください。
[書式と一連の例](book-format-reference.md#残高照合)を参照してください。

### iris allocation

費用の全額を、事業分と家事分に分けて計算します。帳簿もログインも不要で、証拠ファイルを
読むことも、何かを書き込むこともありません。正確な入力形式は `--schema` で確認できます。
金額は文字列で渡し、小数の桁数と丸め方は入力で明示します。費用の対象期間は、割合の
根拠が有効な1つの期間の中に全体が収まっている必要があります。結果には、計算の
バージョンと入力を識別する情報が入ります。証拠は確認していないので「未確認」と
表示します。元資料と、事業用・個人用それぞれの帳簿に記録する対応する仕訳は、別途
確認してください。

```bash
iris allocation --schema
iris allocation --input raw/allocation-jan.json
iris allocation --input -     # 標準入力から一つのJSONオブジェクトを読む
```

入力の上限は8192バイトです。入力の不備は終了コード1、使い方の誤りは2を返します。
取得価額の按分や記帳は行いません。
[費用の按分の例](book-format-reference.md#費用の事業分と家事分を分ける)も参照してください。

### iris asset

固定資産の減価償却とレポート。

```bash
iris asset schedule [--year YYYY] [path]    # 各資産の償却スケジュール
iris asset depreciate --month YYYY-MM [path]  # その月の仕訳を生成（status: draft）
iris asset depreciate --year YYYY [path]      # 年度合計の仕訳を期末日付で資産ごとに生成
```

方式は会計年度ごとにどちらか一方を選びます。すでに月次仕訳がある年度への年次
実行（およびその逆）は拒否されます — 混在すると二重計上になるためです。
仕訳の作成中は作業ツリーをロックします。締め済みと分かっている年度への作成は
拒否します。帳簿が扱う会計年度と異なる年度を指定した場合も拒否します。締めの情報は
手元に保存した写しです。そのため、手元に締めの記録がなくても、クラウドではすでに
締められている可能性があります。兼用資産では全額の償却仕訳を一度残し、
家事分を別に振り替える[確認済みの例](book-format-reference.md#兼用資産の取得価額を保って費用を分ける)を参照してください。

資産の計算量には上限があります。不正な償却表や上限を超えた入力はエラーになります。
[償却表の上限](book-format-reference.md#schedule-計算させるか表を記録するか)を参照してください。

### iris financial

名前付きの会計ビューを計算し、その結果を帳簿に保存して承認するためのコマンドです。
まず `prepare` で、何も書き込まずに計算します。出力された結果の集計額と識別子を
確認してから、`--apply` を付けてその計算結果を保存します。

```sh
iris financial prepare --view management ./my-book
iris financial prepare --view management --apply --revision GENERATION_ID ./my-book
iris financial accept --generation GENERATION_ID ./my-book
iris report pl --view management --from 2026-01-01 --to 2026-12-31 ./my-book
```

`prepare` のビュー省略時は既定のビューを使います。計算結果は `calculations/financial/` に保存します。保存するのは、元文書、`raw/` の
証憑への参照（種類付き）とそのハッシュ、計算後の仕訳、標準計算エンジンの版と状態です。
承認は、この計算結果の識別子に対して行います。元の仕訳を記帳することとは別の操作です。元文書は変更しません。ファイルの追加・削除、内容、ビュー定義、証憑が変わると、現在の入力に対する承認は無効になります。過去の計算結果は標準計算の再現に使えます。

人による記帳承認が必要な帳簿では、下書きの計算結果を保持・同期し、Web の**帳簿設定 → 会計ビューの承認**で確認します。オーナーか記帳担当が、現在のブラウザセッションで承認できます。ローカル承認はローカル操作を記録するもので、認証済みの承認者を示しません。ローカル MCP は `preview_financial_ledger`、`retain_financial_ledger`（確認した `revision`）、`accept_financial_ledger`（`generation`）を提供し、親フォルダモードでは `book` も指定します。

承認済みレポートは1つの承認済みビューを選びます。複数ビューの合成はローカルの未承認比較用です。出力にはビュー名、計算結果の識別子、入力の最終日、未記帳の元取引数を残します。純資産・分析は各帳簿の承認済みの既定ビューを使います。年度を締めるときは、宣言されたすべてのビューが同じ入力の版で確定していることを確認し、
承認済みのクラウド版を固定します。年度のアーカイブ（SQLite、スキーマ 2）には、各ビューと
その元の計算結果を別々に保存し、通常の表には既定ビューの金額を入れます。再開後の訂正でも、作成済みアーカイブは変わりません。

対象は標準の在庫原価計算と当年度取得資産の減価償却です。地域別オーバーレイレシピや申告要件の適否は評価しません。ビュー別の期首・翌年度繰越、例外取引、期別原価配分、勘定科目表・ルールの差分は未対応です。上限は次のとおりで、超えた場合は切り詰めずに拒否します。

| 対象 | 上限 |
| --- | --- |
| 入力・参照のパス | 1,024 |
| 元文書 | 512 KiB |
| 資産 | 64件 |
| 計算後の明細 | 8,192行 |
| 証憑 | 1件あたり 16 MiB、合計 128 MiB |
| 計算結果 | 1 MiB |
| 履歴 | 1,024件、64 MiB |

### iris context

帳簿が選択している会計パッケージの情報を表示します。会計パッケージは、帳簿で使う
フィールド・チェック・計算・ガイドをまとめたものです。引数なしで実行すると短いタスク
一覧を返すので、そこから必要なタスクとレコードだけを指定して詳細を取得します。

```bash
iris context [path]
iris context --task <task-id> --record journals/2026-10/entry.md [path]
```

テキストで表示し、`--json` を付けると JSON で出力します。繰り返し指定
できる `--view` や帳簿フォルダを指定する `--book-path` を含め、対応する全フラグは
`--help` で確認できます。

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
ガイドを読むには、パッケージの出典を正確に指定します。例を読むには、その例を定義している
タスクも指定します。
パッケージや `book:<hash>` の式はコンパイルしません。互換性・適用可否・必須条件・
会計ビューの解決・実行計画・検証・再現計算は未評価です。税の設定がなければ未設定のまま扱い、
未同期のローカル変更は含めません。参照情報を取得できても、操作が許可されたことにはなりません。読み込みのたびに、サーバーが
その時点の帳簿アクセス権とトークンの範囲を確認します。

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

帳簿フォルダ内で `iris diff config/book.yaml` を実行すると、最後に同期した状態からの
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
組み合わせ、循環があれば適用できません。その場合は、互換性のある組み合わせ全体を明示して指定してください。iris が依存先を
自動でダウンロードしたり、有効にしたりすることはありません。

`affectedResults` は、記録された出典が無効になる資産の償却表、申告記録、準備済みの
仕訳項目を列挙します。各行にはファイル、仕訳行番号（0 始まり。記録全体は `-1`）、
項目、保存された `sourceView` 宣言が含まれます。出典の一覧であり、会計ビューを
解決した結果や再計算結果ではありません。`retained` は出典の内容を確認できたこと、
`will-retain` は現在の帳簿独自の定義と元の親バージョンを適用時に保存することを表します。
ただし、内容が保存されていること、このマシンで信頼されていること、再計算が成功する
ことは、それぞれ別の話です。過去の出典が不足していれば
警告しますが、選択操作で補修はしません。帳簿の集計や過去のレシピ再計算は行わず、
記録された金額や項目も書き換えません。

#### ローカル MCP で適用する

ローカル MCP では、組み合わせ全体の `pins` 配列（無効化は `[]`）を
`select_overlays` に渡すと、1 回で検証・適用し、変更内容を返します。
親フォルダモードでは `book` も必須です。有効な組み合わせ全体を置き換えるため、
引き続き使う既存の固定バージョンもすべて含めます。プレビューとリビジョンは任意です。

事前に確認したい場合は `preview_overlay_selection` を呼び、同じ配列と返された
`revision` を `select_overlays` に渡します。CLI でも `--revision` を付ければ、
確認後の変更を検出して拒否します。適用時は同期ロックを取り、設定・定義・信頼状態・記録の追加削除・
出典を再確認します。アーカイブや、既知の締め済み設定は変更できません。締めの情報は
キャッシュなので、ローカルで変更できても最新のクラウド権限や締め状態の証明には
なりません。プレビューは実行用ファイルやキャッシュを作らず、外部にも接続しません。

現在の書き込み処理は、未解決の設定ビューや、ほかの設定を変えてしまう YAML の別名参照・
マージを拒否します。確認漏れを防ぐため、次の上限があります。超えた場合は、部分的な結果を返さずに拒否します。

| 対象 | 上限 |
| --- | --- |
| 選択するパッケージ | 16 |
| 依存ファイル | 1,024件、64 MiB |
| 確認対象全体 | 10,000ファイル、128 MiB |
| 出典 | 2,048件 |
| 影響を受ける出典 | 64種類 |
| 結果の JSON | 2 MiB |

更新操作にも同じ上限と変更前後の確認を使います。
空の選択から地域を推測して更新することはありません。

#### 選択中のバージョンを更新する

```bash
iris overlay upgrade --to id@version --dry-run --json ./books/example
iris overlay upgrade --to id@version --revision REVISION_FROM_PREVIEW ./books/example
```

`--to` は選択中のパッケージを 1つ置き換えます。省略すると、選択中のパッケージの
公開済み最新版を確認します。依存先は互換性のあるバージョンを明示して選択する必要があり、
勝手に追加しません。指定した正確なバージョンが帳簿内にあり、内容を確認できれば
オフラインで使えます。不足時はプレビューでも署名を検証して配布キャッシュに保存する
場合がありますが、帳簿のファイルは変更しません。

プレビューには保存予定の `copies`、パッケージ自身の検証例 `goldenTests`、依存関係・
記録済みの結果への影響と、変更前後の `local_source` / `local_source_after`・信頼状態が
含まれます。検証例の成功は、利用者の帳簿の集計や記録済みの結果の再計算が成功したことを
意味しません。`config/book.yaml` の選択の書き方（1つだけ書く形式か、複数並べる形式か）と、ほかの設定は
変えません。帳簿独自の層がもとにしているパッケージ（親）を更新する場合は、その前に、
層の元の内容と親のバージョンを保存します。有効で信頼済みの層は、プレビューで確認した
親の変更だけであれば、信頼済みのまま引き継がれます。未信頼の層を勝手に有効にはしません。

ローカル MCP は `preview_overlay_upgrade(to?)` で確認し、同じ `to` と必須の `revision` を
`upgrade_overlays` に渡して適用します。親モードでは `book` も指定します。CLI も
`--revision` で確認後の変更を拒否できます。書き込みに失敗した場合は、この更新が書き込んだ内容のうち、その後だれも変更していない
部分だけを元に戻します。途中でほかの人が加えた編集はそのまま残します。なお、確認済みの
出典のコピーは、失敗の前にすでに保存されていることがあります。中断によって信頼済みの層と親の選択が食い違った場合は、
公開パッケージの方針で代用せず実行を止めます。状態を確認し、改めて更新内容を確認してから
続けてください。

実行と過去のレシピ再計算には、帳簿内の定義だけを使います。コピーの不足・改変・
非互換・同一 ID の競合は診断として返し、地域・同梱版・キャッシュで代用しません。
`upgrade` はテストと設定を確認し、新しい定義を保存してから選択を更新します。
旧版と、元の親バージョンを含む帳簿独自の層も保持します。無効化しても既存の
フィールドや計算結果は削除しません。コピーは clone・sync で帳簿とともに移り、
参照操作が不足分を勝手にインストールすることはありません。クラウドは定義と
結果をデータとして保存し、基本の整合性・権限チェックを行います。オーバーレイの
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
[ { family, code, path, newPath?, delete?, reason } ]
```

`family` は `--fix` のカテゴリ。移動なら `newPath`、削除なら `delete: true` が
付きます。

## レポートと証憑

### iris view

このパソコンのウィンドウで帳簿を開き、レポートや仕訳を見るほか、下書きの記帳と
編集、新しい仕訳の作成、記帳済の仕訳の訂正ができます。詳しくは
[このパソコンで帳簿を開く](iris-view.md)を参照してください。

```bash
iris view [book-path | --books-dir PATH] [--tab] [--currency CODE]
iris view --choose
iris view [book-path | --books-dir PATH] --stop | --status [--json]
iris view [book-path | --books-dir PATH] --add-launcher [--tab]
iris view --remove-launcher
```

フォルダを指定しないと、現在のフォルダかその上にある最も近い帳簿を開きます。
どの帳簿の中でもないときは `--choose` と同じで、前回使ったフォルダを開くか、
どのフォルダを開くかを尋ねます。画面は Chrome か Edge の専用ウィンドウで、
拡張機能をオフにして開きます。どちらもなければいつものブラウザで開き、`--tab`
を付けると最初からいつものブラウザを使います。`127.0.0.1` で表示し、オフラインで
動き、コマンドはすぐに終わります。`--currency` は、帳簿ごとに通貨が違うフォルダの
表示通貨を決めます。[フォルダの設定](#帳簿フォルダの価格と設定)の
`reporting_currency` と同じ役割です。

`--add-launcher` は、Dock・スタートメニュー・アプリメニュー用の IrisBooks
ランチャーを1つ追加します。ランチャーはフォルダを持ちません。一緒に指定した
フォルダは最初に開くだけで、`--currency` は指定できません。`--status` は
画面を表示している `iris` のバージョンも示します。`--status --json` は
`running`・`folder`・`books` を、動いている間は `version` も出力します。
画面を表示しているのがこの `iris` より古いものなら `binaryVersion` も加わり、
次の `iris view` で置き換わります。これを含め、どの出力にもサインイン用の
リンクは含まれません。

### iris balance

基準日時点の試算表（既定では記帳済のみ）。

```bash
iris balance [--as-of YYYY-MM-DD] [path]
```

出力は `iris report tb` と同じ試算表のドキュメントです（下記）。

### iris report

財務諸表。サブコマンド:

```bash
iris report tb [--from D] [--as-of YYYY-MM-DD] [path]    # 試算表（--from で期間の試算表）
iris report pl [--from D] [--to D] [--compare prior-year] [path]  # 損益計算書
iris report bs [--as-of YYYY-MM-DD] [--compare prior-year] [path]  # 貸借対照表
iris report trend [--from D] [--to D] [path]             # 月次推移表
iris report cf [--from D] [--to D] [path]                # キャッシュ・フロー計算書
iris report ledger --account PATH [--from D] [--as-of D] [path] # 科目別元帳
iris report sum --by KEY[,KEY...] [--from D] [--to D] [--year YYYY] [path]
                                                         # 仕訳明細のグループ別集計
```

すべてのレポートコマンドと `iris balance` は、`--include-drafts` を付けると下書きも含めて
集計します（例: `iris report pl --include-drafts`）。付けなければ下書きは除外します。
`--include-drafts` を付けて `--mode` を省略した場合は、読み取り専用の比較モードに
なります。結果には、実際に使ったモードと、下書きを含めたかどうかが入ります。
`--mode approved --include-drafts` の併用はできません。比較モードでは在庫原価と
減価償却もファイルを変更せずに計算します。名前付きビューの承認済みレポートは、
現在の入力に対して承認された計算結果を使います。

レポートはテキストで表示します。計算書の数字を順に並べ、行は金額を右にそろえた表にし、
日本語の勘定科目名でも列がそろいます。`--json` を付けると JSON（金額は帳簿通貨の
10進数の文字列）で出力します。数字を処理するときはこちらを読みます。クラウドの
レスポンスには、リビジョンや鮮度などの追加情報が含まれる場合があります。

`report sum` は、記帳済の仕訳明細を指定したキーでグループ化し、グループごとの借方・貸方・
純額と明細数を返します（例: `--by sales.channel,month --year 2026`）。キーには `account`、
`unit`、`payee`、`month` のほか、`sales.channel` のようなドット記法の明細項目を指定
できます。明細項目は、オーバーレイや帳簿独自のレイヤーが定義するものです。キーを持たない明細は空キーの
グループとして明示されるため、未分類の明細が黙って消えることはありません。
`--year` は会計年度（開始年ベース）、`--from/--to` は任意の日付範囲（両端含む）です。

**日付の既定値**。省略した日付は、帳簿の会計年度（`fiscal_year`。帳簿は1年に
1冊）から補います。残高（`balance`・`tb`・`bs`・`ledger`）は今日時点、その年度が
終わっていれば年度末時点で出します。「今日」は帳簿の地域のタイムゾーンでの
日付です。`pl` と `sum` は、年度の初日からその日（今日、または年度が終わっていれば年度末）までを
集計します。たとえば、前年度の帳簿を年が明けてから申告のために開くと、前年度の1年分が
表示されます。
`--to` だけを指定すると、その日が属する会計年度の
初日から集計します。`--from` だけなら今日までです。今日より後の日付の仕訳は、
その日が来るまで含みません。JSON には使った日付が必ず入り、Web アプリ・MCP ツール・
リモートコネクタも同じ既定値を使います。申告に使う数字は、期間（`--year` または
`--from`/`--to`）を指定して出してください。

**出力形**。各レポートは1つの行型の上に組み立てられています。

```text
Balance = { account, code?, contra?, section?, debits, credits, type?, net, prior? }

tb      { asOf?, rows[Balance], totalDebit, totalCredit, balanced }
tb --from { from, to, rows[{ account, code?, type?, opening, debits, credits, closing }],
          totalOpeningDebit, totalOpeningCredit, totalDebit, totalCredit,
          totalClosingDebit, totalClosingCredit, balanced }
pl      { from?, to?, income[Balance], expenses[Balance],
          totalIncome, totalExpense, net,
          prior?{ from, to, totalIncome, totalExpense, net },
          lines?[StatementLine], contraNets?[ContraNet] }
bs      { asOf?, assets[Balance], liabilities[Balance], equity[Balance],
          totalAssets, totalLiabilities, totalEquity,
          currentEarnings, balanced,
          prior?{ asOf, totalAssets, totalLiabilities, totalEquity, currentEarnings },
          lines?{ assets[StatementLine], liabilities[StatementLine] },
          contraNets?[ContraNet] }
StatementLine = { kind, id, label?{ en, ja }, type?, accounts?[], amount, prior? }
ContraNet = { account, gross, deduction, net, prior? }
ledger  { account, from?, to, openingBalance, openingBalanceSide?,
          entries[{ date, filePath, account, payee, status, memo?, summary?,
                    counter{ kind, account? }, opposite?[EntryLine], sameSide?[EntryLine],
                    debit, credit, balance, balanceSide? }],
          months[{ month, debit, credit, cumulativeDebit, cumulativeCredit,
                   balance, balanceSide? }],
          totalDebit, totalCredit, closingBalance, closingBalanceSide? }
EntryLine = { account, amount, memo? }
trend   { from, to, months[],
          income[TrendRow], totalIncome, expenses[TrendRow], totalExpenses, netIncome,
          assets[TrendRow], totalAssets, liabilities[TrendRow], totalLiabilities,
          equity[TrendRow], totalEquity, currentEarnings, balanced,
          lines?{ profitAndLoss[TrendLayoutLine], assets[TrendLayoutLine], liabilities[TrendLayoutLine] } }
TrendRow = { account, code?, contra?, type, values[], total }
TrendLayoutLine = { kind, id, label?, type?, accounts?[], values[], total }
cf      { from?, to?, cashAccounts[], openingCash,
          operating{ rows[CashFlowRow], total }, investing{ … }, financing{ … },
          flows?{ rows[CashFlowRow], total },
          unclassified[{ date, filePath, account?, amount }], unclassifiedTotal,
          netChange, closingCash, balanced }
CashFlowRow = { account, code?, inflow, outflow, net }
TrendLine = { values[], total }   # totalIncome … currentEarnings
sum     { groupBy[], from?, to?,
          rows[{ keys[], debit, credit, net, lines }],
          totalDebit, totalCredit, totalNet, totalLines }
```

`tb`・`pl`・`bs` の行は勘定科目表の順に並び、`code` は勘定科目表にその科目のコードが
あるときのコードです（[勘定科目表](book-format-reference.md#勘定科目表-configchart-of-accountsyaml)を参照）。
`net` は必ず数値で返します。残高がゼロになった科目でも `0` を省略しません。行に `type` が
あれば、`net` は科目の通常残高の向きで表した額です。`type` のない未分類の行では
`debits - credits` です。古いサーバーが `net` を省略していても、現在の CLI が補ってから
JSON を出します。ただし、絞り込みによって残高ゼロの行そのものが出力されないことは
あります。

`ledger` は紙の総勘定元帳と同じ読み方をし、ここでも MCP サーバーでもウェブアプリの API
でも同じ形です。`filePath` は各行の元の仕訳ファイルなので、元帳のどの行からも元の仕訳へ
たどれます。`memo` は明細行のメモ、`summary` は仕訳の説明
本文の1行目で、行の摘要はメモ、メモがなければ `summary` です。`counter` は行の相手勘定で、
仕訳の反対側が1科目なら `account`（科目は `counter.account`）、2科目以上なら `various`
（諸口）、帳簿の期首残高の仕訳（`opening-balance` タグの仕訳）なら `opening`（前期繰越）、
反対側の行がなければ `none` です。`opposite` は反対側の明細行を記録どおりに、`sameSide`
は同じ側のほかの明細行を並べます。後者は、行の金額が反対側の合計と違う理由を示します
（現金 1,100 に対して売上 1,000 と送料 100 など）。どちらも、`counter` だけでは分からない情報があるときにだけ付きます。反対側が1行だけで、
その行を `counter.account` が示している場合、`opposite` は省きます。このとき反対側の
行の金額は、この行の金額に `sameSide` の金額を足した額です。この行と同じ側にほかの
行がない場合、`sameSide` は省きます。`balance` はその行を反映した**後**の
残高で、負になりません。`balanceSide`（`debit` か `credit`、ゼロなら省略）が借方・貸方の
どちらに立つ残高かを示します。売上は貸方に立ち、現金が貸方に立てば何かがおかしいという
合図です。`months` は月ごとの月計（`debit`・`credit`）、帳簿の年度の初めからの累計
（`--from` より前の月も含む）、月末の残高です。期首残高の仕訳は前期繰越で、その月の
動きではないので、どちらにも数えません。`closingBalance` は最後の行の後の残高で、
`closingBalanceSide` に立ちます。

`--account` には親のパスも指定できます。たとえば勘定科目表に `資産:普通預金:銀行A` と
`資産:普通預金:銀行B` があれば `資産:普通預金` の元帳はその下の科目をまとめ、各行の
`account` がどの補助科目の行かを示します。補助科目どうしの振替は両方の行に出て、
それぞれもう一方が相手勘定です。`--from` を付けると、その日より前の行は
`openingBalance`（負にならず、`openingBalanceSide` に立つ残高）として繰り越し、
一覧はその日から始まります。

勘定科目表で科目に `section` を指定すると（[勘定科目表](book-format-reference.md#勘定科目表-configchart-of-accountsyaml)を参照）、
`pl` と `bs` に `lines` が加わります。決算書の並びに組み替えた明細です。このとき、科目ごとの各行（`Balance`）にも `section` が付きます。`lines` のうち `kind` が
`section` の行は、1つ以上の区分をまとめた行です。その区分に属する科目を `accounts` に、
合計を `amount` に持ちます。合計は科目の通常残高の向き（`type`）で表します。収益と費用の両方を含む行の
合計は、収益から費用を引いた額です。`subtotal` の行はそこまでの利益です。売上高から
売上原価を引いた売上総利益、続いて営業利益、税引前当期純利益、当期純利益と並びます。
区分のない科目は、最後の小計の直前の `unclassified` の行に入ります。当期純利益には
含まれますが、ほかの小計には含まれません。貸借対照表では、資産と負債をそれぞれ流動と
固定に分け、その後に区分のない科目、最後に区分を付けていない事業主の科目（`owner: true`）
の `owner` の行を置きます。`label` は各行の英語と日本語の名前です。
区分のない勘定科目表では `lines` は付かず、そのほかの出力は変わりません。

`contra` のある行は評価勘定で、指定した科目または親のパスから差し引きます。
`contraNets` は差し引く相手ごとの金額です。`gross`（その科目、または親のパスの下の科目の
合計。その評価勘定は除く）、差し引く額 `deduction`、差し引いた後の `net` を、相手の科目の
向きで返します。`--compare prior-year` では、`prior` が前年の `net` です。評価勘定のない
計算書には `contraNets` は付きません。

`--compare prior-year` は、帳簿の `config/prior-year.yaml`（[`iris yearend`](#iris-yearend)
を参照）から前期の数字を加えます。`pl` は1年前の同じ暦月、`bs` は1年前の同じ月の
月末残高です。各行に `prior`（科目の通常残高の向き。前期に数字がない科目は `0`）、
レポートに前期の日付と合計を持つ `prior` が付きます。前期にしかない科目は当期 `0`
で現れます。比較は月単位です（ファイルは月ごとの合計を持つため）。このファイルの
ない帳簿では `prior` が付かず、標準エラーに注記が出ます。

`iris report trend` は `--from` の月から `--to` の月までを月ごとに並べた月次推移表です。
`values` は `months` の各月に1つずつで、科目の通常残高の向きです。収益・費用の科目は
各月の動き（`total` は期間の合計、`netIncome` は各月の当期純利益）、資産・負債・
純資産の科目は各月末の残高（期首残高の仕訳を含み、`total` は期末残高）です。区分ごとに
行と同じ `{ values, total }` 形の合計があります。`currentEarnings` は年度の初めから
各月末までの当期純利益で、貸借対照表では純資産と並べます。各月の資産は負債・純資産・
当期純利益の合計と一致し、すべての月で一致すれば `balanced` が true です。勘定科目表で
科目に区分を付けると、`lines` が `pl` と `bs` の `lines` と同じ並びを月ごとに返します。
損益の行と小計、続いて資産と負債の区分です。

`iris report cf` は期間のキャッシュ・フロー計算書です。勘定科目表で `cash: true` を
付けた科目とその下の科目（`cashAccounts`）を対象とし、`--from` より前の残高（期首残高の仕訳を含む）を
`openingCash` とします。現金の動きは、その仕訳の相手側で分類します。現金以外の科目の行は、貸方から借方を引いた額だけ現金が動いたものとみなします。
営業（`operating`）・投資（`investing`）・財務（`financing`）のどれに入れるかは、その
科目の区分で決めます。科目に `cash_flow` の指定があればそちらを優先し、事業主の科目は
財務に入れます。区分ごとに、相手の科目と収入 `inflow`・支出 `outflow`・
`net` を並べます。行ごとに分けるのは、正確に分けられるときだけです。相手側の行がすべて
同じ区分のとき、または現金の行だけが片側にあるときです。それ以外は仕訳全体を
`unclassified` に入れ、按分はしません。区分のない科目の行も `unclassified` に入ります。
現金の科目どうしの移動は計上しません。`netChange` は各区分と `unclassified` の合計で、
期首の現金と `netChange` の合計が `closingCash` と一致すれば `balanced` が true です。
区分を使わない勘定科目表では、区分のない計算書になります。各区分は空のままで、`flows` に
現金が動いた相手の科目を収入・支出・`net` とともに並べるので、`unclassified` は出ません。
現金の科目がない勘定科目表では、各区分は空になり、標準エラー出力にその旨を表示します。

`iris report tb --from D` は `D` から `--as-of` までの期間の試算表です。科目ごとに
期首の残高 `opening`、期間の借方 `debits`・貸方 `credits`、期末の残高 `closing` を
返します。`opening` と `closing` は `net` と同じく科目の通常残高の向きです。期首残高の
仕訳は日付にかかわらず `opening` に入ります。`balanced` が true なら、期首の借方残高と
貸方残高、期間の借方と貸方、期末の借方残高と貸方残高がそれぞれ一致します。
`sum.rows[].keys` は位置対応で、`--by` に渡したキーと同じ順に1つずつ並びます。

### iris search

任意のフィルタの組み合わせ（AND）で仕訳を探します。決定論的・オフライン。

```bash
iris search [--from D] [--to D] [--min AMOUNT] [--max AMOUNT] [--payee S] \
  [--status draft,posted,closed] [--account S] [--tag S] [--json] [path]
```

ステータス列には**実効**ステータスが表示されます。日付が締め済み会計年度に
入っている仕訳は、ファイルの記載にかかわらず `closed` と表示され、
`--status closed` はまさにそれらを絞り込みます。

**出力形**（`--json`）:

```text
{ currency, currencyScale, count, total,
  journals[{ path, date, payee, status, amount, lines }] }
```

`amount` はその仕訳の借方合計で、帳簿通貨の10進数の文字列（`"54.99"`）です。
`lines` は明細行数です。`count` と `total` は一致した件数と金額の合計なので、
行を足し合わせずに `total` を使ってください。`--min` と `--max` も同じ書き方で
金額を指定します。`--min 98` なら $98.00 以上の仕訳に一致します。

### iris references

指定したパスの参照関係を表示します。資料を指定すると、それを引用している仕訳を表示します。
仕訳を指定すると、その仕訳が引用している資料と、同じ資料を引用しているほかの仕訳を
表示します。

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

各 `ledger-<科目>.csv` は紙の元帳の並びです。`date`、`file`、`description`（摘要）、
`counter_account`（相手勘定。科目、または帳簿の言語で「諸口」「前期繰越」）、`payee`
（取引先）、`debit`、`credit`、`balance_side`（借・貸）、`balance`（負にならない残高）、
続いて相手勘定の内訳 `opposite` と `same_side`（`科目 金額; 科目 金額`）です。月ごとに
月計の行と累計の行が続きます。

資産の CSV には、資産ファイルにある追加の項目（オーバーレイが定義する項目など）が
1 項目につき 1 列ずつ加わります。列名はドット区切りのパス
（例: `location.room`）で、標準の列の後に名前順で並びます。その項目が
ない資産のセルは空欄です。

### iris hash

単一ファイルの正規コンテンツハッシュを表示します（ローカルのバイト列とサーバーが
受理した内容を比較するときに便利）。

```bash
iris hash [--raw] <file>
```

## 同期と復旧

### iris sync

同期を1回、明示的に実行します。ローカルの変更を push し、リモートの変更を pull して、
ファイルごとの受理・拒否を報告します。帳簿がクラウドにリンクされ、サインイン済みである必要が
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
クラウドでの変更には オーナー権限が必要です。

同期は毎回、結果と件数を示す1行の要約で終わります。例えば
`Sync complete: 0 pushed, 0 pulled, 0 server deletions, 0 conflicts.` と出るので、
`--json` なしでも「何も変わらなかった」ことが読み取れます。その下に、失敗、
キューに残ったファイル、未解決のコンフリクト、ローカルに反映できなかった変更、
拒否が続きます。`--json` のドキュメントと同じ内容です。

終了コードは次のとおりです。`0` は問題なく完了、`1` は拒否・コンフリクト・入出力エラー、
`2` は使い方または設定の誤りです。`3` は同期を続けられない切断で、帳簿の削除、
アクセス権の取り消し、セッションの失効のいずれかを表します。

1回の sync で帳簿のクラウドファイルの大半を削除しようとすると、サーバーは
安全装置としてその削除を拒否します（`BULK_DELETE_REFUSED`）。大量削除が本当に
意図したものであれば、`--allow-bulk-delete` を付けて再実行してください。

**出力形**（`--json`）— 上記すべてを1つのドキュメントに置き換えたもので、AI が
編集のたびに読むのはこれです。

```text
{ status, counts{ pushed, pulled, deleted, conflicts }, queueLeft,
  disconnected, disconnectReason?,
  newRejections[], allRejections[], applyErrors[], blockedByConflicts[],
  error?, errorDetail?{ kind, status?, retryable, phase?, elapsedMs? },
  notice?{ message, files[] } }
```

- `status` — `ok` | `rejected` | `conflicts` | `disconnected` | `error`
- `disconnectReason` — `deleted` | `forbidden` | `auth_expired`
- `errorDetail` — サーバーへのリクエストが失敗したとき、`error` と一緒に返り
  ます。`kind` は `status`（サーバーが HTTP `status` で応答した）、`timeout`、
  `connect`、`dns`、`tls`、`proxy`、`canceled`、`other` のいずれかで、
  `retryable` は sync を再実行すれば成功しうるかを表します。
  応答がなかったときは、`phase` がリクエストの到達段階（`dns`、`connect`、`tls`、
  `send`、`wait`）を、`elapsedMs` が失敗までの時間を表します。
  [トラブルシューティング](troubleshooting.md#クラウドのコマンドがネットワークエラーを報告する)を参照してください。
- `notice` — 帳簿の初回アップロードか、`raw/` の証憑を送る同期のときに入ります。
  内容は、IrisBooks に送るデータに公的機関が発行する個人識別番号を含めないよう求める
注意です。その同期で送る証憑ファイルが `files` に入ります。それ以外のパスでは省略されます。
- `newRejections` / `allRejections` — 要対応レコード。`iris sync issues list
  --json` と同じ形です
- `blockedByConflicts` — 未解決の `.conflicted` サイドカーがある正規パス。
  **空でなければ、その回の同期全体が no-op** です。push も pull も起きていないので、
  先にマージするか解決してください
- `applyErrors` — リモートの変更をローカルに反映できなかったもの。作業ツリーが
  不完全な可能性があるため、いまのファイルを信用せず再実行してください

編集 → 同期 → 読み取り のループで2回目の呼び出しが要らないのはこのためです。
ファイルごとの受理**と**拒否が、この1つのレスポンスに両方入っています。

### iris diff

push される内容 — ローカル変更と最後の同期スナップショットの差 — を表示します。
ローカルだけの帳簿でもオフラインで使え、一度も同期していない場合はファイルを追加として
表示します。同期済みの過去の変更は、ファイル履歴で確認してください。

```bash
iris diff                # 保留中の全変更を一覧
iris diff <relpath>      # 1ファイルの行単位差分
iris diff --paths        # 名前と種別のみ
```

### iris conflicts

同期のコンフリクトを一覧し、解決します。push がコンフリクト（409）すると、元のパスの
ファイルはサーバーの版になり、あなたの版は `.conflicted` の付いた別ファイル（サイドカー）
として残ります。

```bash
iris conflicts list [--json] [path]
iris conflicts resolve <path> --keep mine|cloud [path]
```

通常は手動マージで解決します（正規ファイルを編集し、サイドカーを削除し、
`iris sync`）。[トラブルシューティング](troubleshooting.md) を参照。

### iris sync issues

サーバーに拒否されたファイルの記録（このパソコンに保存されます）を表示し、もう一度
送れるようにします。

```bash
iris sync issues list [--json] [path]              # パス + コード + 問題を表示
iris sync issues retry [path]             # 抑制を外す。次の `iris sync` で再 push
iris sync issues retry --path <relpath> [path]   # 1ファイルのみ
```

**出力形**（`list --json`）:

```text
{ records[ { path, localFs, localSha, code?,
             issues[{ field, message, rule? }], detectedAt, reason? } ] }
```

`code` はそのファイルを拒否したサーバー側の不変条件です
（`UNBALANCED_JOURNAL`、`UNKNOWN_ACCOUNT`、`PERIOD_SEALED`、
`BULK_DELETE_REFUSED` など）。`OVERLAY_RULE` は地域オーバーレイのルール
（公開オーバーレイのもの、または `config/overlays/` にある帳簿独自のもの）が
拒否したことを表し、各 issue の `rule` がそのルールを示します。ルールは
`iris overlay list` で確認できます。

## 資産管理と価格

### iris networth

```bash
iris networth --books-dir ~/IrisBooks --as-of 2026-10-06
iris networth --currency JPY ~/IrisBooks/business-2026 ~/IrisBooks/personal-2026
iris networth history --books-dir ~/IrisBooks --months 12
iris networth movers --books-dir ~/IrisBooks --compare 2026-09-30
```

複数の帳簿をまとめて、純資産を計算します。ローカルの記帳済の仕訳と価格記録だけを使い、
通信はしません。
親フォルダ直下の帳簿、または明示的なフォルダ一覧を選びます。
通貨が異なる場合は `--currency` が必要です。年度間のリンクを明示した帳簿は、
期首残高を照合して一続きの履歴として扱います。翌年度の期首残高が前年度の残高と一致することを確かめたうえで、前年度の残高の代わりに
翌年度の期首残高を使うので、二重には加算しません。翌年度がない場合も最後の保有残高を引き継ぎます。
下書きは除外します。価格がない保有は簿価を使い、`unpriced` に示します。
帳簿のコピーを二重に数えないよう、重複するフォルダ・帳簿 ID は拒否します。
テキストで表示し、`--json` を付けると JSON で出力します。クラウドの集計対象設定は使いません。

### iris price

10,000口当たりの基準価額、実際の口数、現金の照合と更新時点は、[投資信託の例](book-format-reference.md#投資信託の口数一部売却時点別の評価を確認する)を参照してください。

単位あたりの価格をオフラインで記録・一覧し、サーバーへ同期します。価格はユーザーごとに
保存され、帳簿には入りません。

```bash
iris price add --unit BTC --price 9850000 [--currency JPY] [--date YYYY-MM-DD] [--books-dir PARENT] [--source S]
iris price list [--unit BTC] [--currency JPY] [--year 2026] [--books-dir PARENT] [--json]
iris price sync [--json]
iris price conflicts [--json]
iris price resolve --unit BTC --currency JPY --date 2026-10-07 --choose local --revision 43 --edit <edit-id>
```

**出力形**。`list --json`:

```text
[ { unit, currency, date, price, source?, origin, recordedAt,
    revision?, baseRevision?, editId?, conflict?, pending? } ]
```

`price` は**1単位あたり**の値を `--price` と同じ10進数の文字列で表します
（¥9,850,000 のビットコインは `"9850000"`）。`origin` は `local`（この端末で記録）か `server`。
`sync --json` は `{ pushed, pulled, conflicts }` を返します。
競合が残る場合は、他の価格の同期を進めたうえで終了コード 1 を返します。

価格は観測日の暦年ごとに `~/.config/irisbooks/prices/YYYY.jsonl` に保存します。
従来の `prices.jsonl` は初回利用時に移行し、元のファイルも残します。
同期は前回取得したページ以降の変更を取得します。過年度の価格訂正も対象です。

同じ単位・通貨・日付への編集は、価格と出典が一致すれば自動で合流します。
異なる場合は両方の候補を残します。競合が判明した価格は、ローカル集計でも
サーバーの確定値を使い、影響する保有を `priceConflicts` に示します。
`networth history` では該当する時点に、`networth movers` では比較する2つの日付の両方に、
その情報が付きます。
他の価格や記帳レポートの利用は続けられます。
`price conflicts --json` で確認し、表示されたサーバーの revision とローカル編集 ID
を指定して解決します。`--choose local` は次の同期で送る訂正を残し、
`--choose server` はその編集を破棄します。別の値に直す場合は local を選んでから
価格を再記録して同期します。候補が変わった後の古い解決指定は拒否されます。

#### 帳簿フォルダの価格と設定

親フォルダは `<フォルダ>/.irisbooks/` に独自の価格と設定を持てます。構成は
`~/.config/irisbooks/` と同じです。フォルダと一緒に移動し、`iris price`・`iris networth`・
`iris analytics export`・`iris view` に `--books-dir` を指定したときに使われます。

```bash
iris price add --books-dir ~/Clients/acme --unit USD --price 155 --currency JPY
iris price list --books-dir ~/Clients/acme --json
```

フォルダに価格がある単位は、その単位と通貨についてフォルダの履歴だけを使います。個人の
価格に新しい日付があっても使いません。フォルダに価格がない単位は、個人の価格を使います。
`--books-dir` を付けた `list --json` は、各行に `level: folder` または `level: user` を
追加します。フォルダの価格は同期しません。`iris price sync` の対象は個人の価格だけです。

`settings.yaml` は `<フォルダ>/.irisbooks/settings.yaml` と
`~/.config/irisbooks/settings.yaml` で同じ形式で、フォルダの値が優先されます。

```yaml
reporting_currency: USD
color: teal
```

レポート通貨は、指定した `--currency`、フォルダの設定、個人の設定、帳簿に共通の通貨の順に
決まります。

`color` は `iris view` でフォルダを示す帯の色です：`malachite`（緑）、`azurite`（青）、
`teal`（青緑）、`tyrian`（紫）、`sienna`（赤茶）、`umber`（茶）、`ochre`（黄土）、
`charcoal`（墨）。複数の帳簿が入ったフォルダで画面から色を選ぶと、そのフォルダの
ファイルに書き込まれます。個人のファイルでは、色を決めていないフォルダの色になります。
これ以外の値は無視されます。

### iris analytics

```bash
iris analytics export --books-dir ~/IrisBooks --out portfolio.duckdb --currency JPY
duckdb -readonly portfolio.duckdb
```

`export` は未同期の編集を含むローカルの記帳済の仕訳と価格記録から、分析用ファイルを
作ります。DuckDB CLI をインストールするか、`--duckdb /path/to/duckdb` で指定して
ください。`--books-dir` または帳簿フォルダの一覧を指定します。出力先に既存のファイルは
使えません。価格の競合がある場合は、解消してから実行してください。

ファイルには出典、仕訳の増減、保有残高の履歴、価格、不足情報と、時点評価用の
`portfolio_at` マクロが入ります。SQL やピボットで分析できます。

```sql
SELECT account, unit, valuation, cost, inventory_method FROM portfolio_at('2026-10-19', 'JPY', 0);
PIVOT journal_lines ON unit USING sum(debit-credit) GROUP BY book_id, account;
```

コマンドの結果と違い、このファイルはエンジンの整数をそのまま保存します。金額の列は
その通貨の最小単位（小数2桁の通貨ならセント）、数量はその単位の最小単位です。
数字を示す前に、10 の scale 乗で割ってください。

`iris yearend` は完全な期首ロットと取得原価を翌年度の帳簿に引き継ぎます。
各年度の帳簿は単独で使え、その会計年度の期間だけ集計に含まれます。
過去の期間を見る場合は過年度の帳簿も選びます。帳簿のない年度は空白です。
帳簿間の関係は保存せず、リンクも不要です。

取得額は現在保有する分の取得原価です。簿価、累計入金額、実現損益とは別の値です。
原価の計算方法は FIFO が既定です。帳簿の設定に、その保有に当てはまる計算方法の指定が
あれば、それを優先します。指定がなければ、期首の在庫に記録されている方法を引き継ぎます。個別法・移動平均にも対応し、
個別法の売却ではロットを選ぶ必要があります。取得履歴や期首の取得原価が
不明なら、不明のまま表示します。`inventory_method` で保有残高ごとの方法を
確認できます。
会計ビューを使う帳簿では、現在の入力に対して承認済みの既定ビューの計算結果を使い、
出力ファイルにはビュー名と計算結果の識別子も記録します。計算結果が未承認の場合や、
承認後に入力が変わっている場合は、出力を拒否します。

## AI アシスタント連携

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

`--status` は各クライアントの登録状態を報告します。登録されている iris の実行ファイルが
まだ存在するかどうかも確認します。存在しない場合は登録が古くなっているので、
`iris onboard` を実行し直すと直ります。
`--json` で機械可読な出力になります。`iris onboard` の再実行は常に安全です。
登録はその場で更新され、重複しません。

### iris offboard

`iris onboard` で行った登録を取り消します。すべてのクライアント設定から `irisbooks` の
MCP 登録を削除し、Claude Code スキルも削除します。すでにアンインストールした
クライアントに残っている登録も対象です。帳簿のデータやサインイン状態には触れません。何度実行しても結果は同じなので、入れ直す前に実行しても安全です。

```bash
iris offboard [--book-path PATH] [--keep-skill] [--remove-path] [--dry-run]
```

| フラグ | 意味 |
| ---- | ------- |
| `--keep-skill` | Claude Code スキルを残す（他の帳簿がまだ使っている場合） |
| `--remove-path` | `onboard --install-path` で入れたバイナリも削除し、PATH 追加を戻す |
| `--dry-run` | 削除される内容の表示のみで、何も削除しない |

### iris mcp

1つの帳簿、または帳簿をまとめた親フォルダに対してローカル MCP サーバーを実行します。

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

`--book-path` は既存の単一帳簿を扱い、各操作の帳簿指定は不要です。先に `iris init` で
作成してください（新しい帳簿には地域の明示が必要なため、未作成または空の指定先は拒否します）。
2つのフォルダ指定は併用できません。ホストと AI に見えるパスは
異なる場合があり、ファイルへのアクセス権とツールへの接続は別に必要です。

#### ローカル帳簿を作る

空の親フォルダでも利用できます。新規作成には
`create_book(book="freelance-2026", name="Acme", region="JP", fiscal_start_month=1,
fiscal_year=2026)` を使います。地域は必須です。推測せず利用者に確認してください。通貨は省略すると地域の通貨になります。既存の帳簿や空でないフォルダは上書きせず、親自体も
帳簿にしません。既存のクラウド帳簿を使う場合は、先に作成せず、後述の clone を使います。

#### 記録を作成して検証する

`AGENTS.md` を読み、元資料の確認や下書き・ノートの編集には通常のファイルツールを
使います。MCP は計算、検証、専用の更新処理に使います。`validate`・`balance`・
`report`・`status`・`diff`・`complete_journal` は対象帳簿に対する操作です。
complete_journal はプレビュー後、版を確認して下書きへ適用します。`post` には、記帳する仕訳のパスを渡すか、すべての下書きを記帳することを明示して
指定します。記帳ポリシーとサーバーの承認条件に従います。
`dry_run=true` でプレビューできます。`local=true` は認証や同期をせずローカルで記帳します。
`local` を省略すると、接続済みの帳簿では記帳後に帳簿全体を自動で同期します。このとき、
対象の仕訳以外の未同期の変更も送られます。

選択中のオーバーレイは `describe_overlay` で確認します。`list_recipes` と `run_recipe` は、単一帳簿モードと親フォルダモードのどちらでも使えます。一覧は CLI と同じレシピ ID と入力形式を返します。
`run_recipe(recipe=一覧のID, params={...})` で結果を確認し、
保存時は `apply=true, out="assets/2026/equipment.md"` を追加します。申告用の計算補助資料は
`filings/` 内を指定します。`out` を指定しただけでは保存されず、プレビューになります。`apply` と `out` は `params` の
中ではなく、外に指定します。
親モードでは両ツールに `book` も指定します。償却の計算ツール、`check_update`、
`read_docs` には帳簿の指定が不要です。費用の按分計算 `allocation` も帳簿を指定せずに使えます。`read_docs` は既定でトピックや節の一覧を返し、
節を指定すると本文を読みます。不明な引数や型の誤りは実行前にエラーとなり、文字列の `"true"` は真偽値として扱いません。参照関係の確認には
ファイルツールまたは CLI の `iris references` を使います。
`open_view` は、サーバーを動かしているパソコンで、対象の帳簿を [`iris view`](#iris-view)
で開きます。両モードで使え、サインイン用のリンクは返しません。

#### クラウドの利用を承認する

最初に `auth_status` を呼び、`signed_in` ならその認証を使います。それ以外は `login` を
呼び、ホストのブラウザでユーザーが許可した後、`auth_status` の
`status="signed_in"` を確認します。`login` は `authorizationUrl` と 5 分後の有効期限を
返し、許可待ちの再呼び出しでは同じ URL を返します。`auth_status` の
`validate=false` は認証情報の有無だけを調べます。

`login`・`auth_status`・`logout`・`list_cloud_books` に帳簿の指定は不要です。
認証情報はホスト内で CLI とローカル MCP の間で共有し、ツール結果には出しません。
`logout` は保存したセッションを失効し、許可待ちも取り消します。環境変数
`IRIS_API_TOKEN` があればそちらを優先します。そのトークンの権限のまま使うこともできます。ブラウザでの認証に切り替える場合は、
ホストの設定からこの変数を外して再起動してください。現在のサービスの認証手順は
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
既存のクラウド帳簿に接続するには、次の3つがそろっている必要があります。

- 接続先のオーナー権限がある
- 会計年度・地域・通貨などの設定がローカル帳簿と一致している
- 接続先が、作成したまま手を加えていない帳簿か、ファイル履歴のない帳簿である

接続のときは、ローカル帳簿の設定・勘定科目表・`AGENTS.md` をまとめてクラウド側に反映し、
それが済んでからローカルの接続先を書き換えます。すでに記録がある、編集されている、
締め済みである、または確認中に変更された接続先は拒否します。その場合は別のフォルダへ
clone して比較してください。この条件は、強制の指定でも省略できません。アーカイブの
帳簿と、すでに接続済みの帳簿は、クラウド帳簿の新規作成も接続もできません。同期の拒否やエラーは別途確認します。

#### 既存のクラウド帳簿を clone する

認証後に `list_cloud_books` で対象を確認し、未作成または空の子フォルダへ
`clone_book(book="freelance-2026", cloud_book_id="bk_...")` を実行します。
先に `create_book` は呼びません。clone は、同期済みのファイルと記帳ポリシーをそのまま取得し、不足しているローカルの
ガイドを追加します。同期状態とスナップショットの準備まで済ませてから、フォルダを使える
状態にします。そのため、clone した直後は通常、未同期の差分がありません。ただし、古い
帳簿に `AGENTS.md` がなければ追加するので、そのファイルだけは最初の同期で送る変更として
残ります。

結果にはホスト側のパスと帳簿情報が含まれ、再起動せず `list_books` から見つけられます。
既存の内容、シンボリックリンク、アーカイブ、既存の `<book>.partial` は拒否します。
強制上書きはできません。clone は `--books-dir` の場合に利用できます。

#### 競合の解決と翌年度の作成

`list_conflicts` と `resolve_conflict` で競合を確認・解決します。mine を残すと直後に同期し、
cloud を残すとサイドカーを削除します。`list_conflicts` は JSON `{conflicts: [{path, local}]}`、
`list_sync_issues` は拒否の詳細を含む JSON `{records: [...]}` を返します。`retry_sync_issues` は、拒否されたファイルを再び同期の対象に戻します。再送するには、
そのあとで `sync` を呼びます。削除のように取り消しにくい変更は、先にプレビューで確認し、
帳簿の方針に従って行います。

`asset_depreciate` は下書きを作ります。クラウド接続済み帳簿の `fiscal_years`・`history`・
`seal`・`reopen` には認証と対応するサーバー権限が必要です。
`seal(period="2026", dry_run=true)` は締めずに確認し、`dry_run` の省略または false は締めを実行します。親モードの
`yearend(book=..., next_book=...)` は既定でプレビューし、`dry_run=false` で実行、
`local=true` でクラウド処理を省略します。仕訳の移動、権限のコピー、受信先の移管が発生する
場合がありますが、旧年度は締めません。`link_existing` は未編集で設定の一致する翌年度帳簿だけに
接続し、既存の権限と受信先を保持します。詳しくは [年度更新](cli-reference.md#iris-yearend) を参照してください。

#### 純資産と価格

`get_networth` はローカルの記帳済の記録を未同期の編集も含めて集計し、通信や認証は不要です。
設定ルート内の `books_dir="."` または `books=["business-2026", "personal-2026"]` を指定します。
単一帳簿モードでは兄弟フォルダを選べません。`as_of`・`currency`・
`mode="current"|"history"|"movers"`・`months`・`compare` で参照を指定し、通貨が異なる場合は
`currency` が必要です。`get_holdings` は代わりに接続済みクラウド帳簿を読みます。

`list_prices` は CLI の `iris price list` と同じく、既定でローカルのオフライン価格を読みます。
認証済みのクラウドの価格は `source="cloud"` で読みます（CLI の `iris api price list` に相当）。
`record_price` は小数点以下 6 桁以内の文字列で価格を記録し、`sync_prices` は帳簿とは別に
価格を送受信します。`record_price` とローカルの `list_prices` は `books_dir` を指定すると
[フォルダの価格](#帳簿フォルダの価格と設定)を使います。価格は税務用帳簿ではなくユーザー設定に保存します。クラウド一覧は
1 ページを返すので、同じ条件で `nextCursor` を渡して続きを読みます。`list_price_conflicts` で候補を
確認し、ユーザーが選んだ場合にだけ、表示された版と編集 ID で `resolve_price_conflict` を実行して
同期します。価格と出典が同じ編集は自動で合流します。`get_holdings` 以外にはローカルの帳簿指定は不要です。

#### ローカル HTTP 接続

`--http` は stdio の代わりに localhost で待ち受け、`Authorization: Bearer <トークン>` を要求します。
トークンは初回に `~/.config/irisbooks/mcp-http.token` に作成し、所有者だけが読めます。
再起動しても同じ値なのでクライアントのヘッダーは一度設定すれば使えます。ファイルを削除すると
次回起動で新しい値になり、ヘッダーの更新が必要です。

## クラウド管理（`iris api …`）

アカウントとクラウド帳簿を管理するコマンドで、認証（`iris api login` または
`IRIS_API_TOKEN`）が必要です。アカウント単位の操作（`login`・`whoami`・`logout`・
`books`・`token`・`config`・`price`）は帳簿の指定が不要です。帳簿単位の操作
（`grants`・`inbox`・`balance`・`holdings`・`history`・`export`・`networth`）には
**帳簿 ID** を `--book-id ID`、位置引数、`IRIS_BOOK` のいずれかで渡します。

### iris api login

ブラウザ補助のサインイン。このデバイス専用の CLI セッションが発行されます。
Web アプリからサインアウトしても CLI には影響せず、90 日間使用がなければ
自動失効します（使うたびに延長）。取り消しは Web アプリの「あなたの設定
（アバターメニュー） → API トークン」から行えます。

```bash
iris api login
iris api whoami     # 認証情報を確かめ、その出どころとアカウントを表示
iris api logout     # このデバイスのセッションを取り消してトークンを削除
```

サーバーや AI アシスタントの VM など、ブラウザのない環境では、自分のスマートフォンで
承認できます。

```bash
iris api login --device
# 表示された IrisBooks の URL をスマートフォンで開き、サインインしてリクエスト番号を入力し、承認します。
iris api login --device-complete
iris api whoami
```

パスキー、またはパスワードと認証アプリのコードは、自分のブラウザにだけ入力し、
アシスタントには渡さないでください。番号を入力するだけではアクセスは許可されません。
アカウント・権限・注意書きを確認してから承認してください。リクエストは開始から
10 分で失効します。`--device-complete` が `Authorized` を表示し、`whoami` が成功して
から先に進みます。

ブラウザのダウンロード先を CLI から読み取れる場合は、認可結果をファイルで
受け取る方法も使えます。

```bash
iris api login --handoff-file
# 表示された URL を開いてサインインし、アクセスを許可すると iris-login.json がダウンロードされます。
iris api login --complete /path/to/downloads/iris-login.json
iris api whoami
```

ファイルに入るのは一度だけ使える認可コードで、セッショントークンではありません。
許可から 5 分で失効します。完了後はダウンロードしたファイルを削除してください。

### アカウントと環境を分ける

**アカウントと環境の組合せごとに専用の非公開フォルダ**を使い、帳簿の外に置きます。
ログイン前に `IRISBOOKS_TOKEN_FILE` でその中のトークン保存先を指定し、完了操作と後続のCLIでも同じパスを使います。
接続先の設定、許可待ちの情報、ユーザー単位の価格データも同じフォルダに保存されるため、
同じフォルダで `personal.json` と `business.json` に名前を分けるだけでは分離できません。
帳簿のフォルダを変えても、ログインするアカウントは切り替わりません。

POSIXシェルで、個人用のプロファイルを選ぶ例です。

```bash
export IRISBOOKS_TOKEN_FILE="$HOME/.config/irisbooks/profiles/personal-prod/token.json"
iris api login --device
# Approve on your own device, then keep the same IRISBOOKS_TOKEN_FILE:
iris api login --device-complete
iris api whoami
iris api books list
```

PowerShellでも、専用フォルダを指定します。

```powershell
$env:IRISBOOKS_TOKEN_FILE = Join-Path $HOME '.config/irisbooks/profiles/personal-prod/token.json'
iris api login --device
# Approve on your own device, then keep the same IRISBOOKS_TOKEN_FILE:
iris api login --device-complete
iris api whoami
iris api books list
```

別のアカウントは `.../profiles/business-prod/token.json` など別のフォルダを選んで
そのアカウントでサインインします。元のアカウントへ戻るときは、元のパスを指定します。
認証情報や認可ファイルを `raw/`、メモ、チャット、同期対象の帳簿ファイルに入れないでください。

認可を開始しただけでは、既存のセッションは置き換わりません。完了時に選択中のローカル認証情報が置き換わります。
以前のサーバー側セッションは自動で失効しないため、不要ならWebの「設定 → APIトークン」で取り消してください。
`iris api logout` はサーバー側の失効を試み、選択中のローカルセッションと許可待ちの情報を削除します。
失効処理が失敗した場合は警告に従い、Webで取り消します。保存済みの接続先設定と価格データは残ります。
`IRIS_API_TOKEN` は削除されないので、使うのをやめる場合は別途解除してください。

#### 保存済みの旧本番接続を切り替える

古いプロファイルでは `irisbooks.jp` が選ばれている場合があります。
ログインは認可前にapp/API、完了後にAPIの接続先を表示します。
CLIの更新だけでは、サーバー側セッションや帳簿のクラウド識別子は移行されません。
新しい専用プロファイルで、接続先を明示して対象サービスを承認します。

```bash
export IRISBOOKS_TOKEN_FILE="$HOME/.config/irisbooks/profiles/personal-io/token.json"
unset IRIS_API_TOKEN IRIS_API_ENDPOINT
IRISBOOKS_APP_BASE=https://irisbooks.io IRISBOOKS_API_BASE=https://irisbooks.io/api iris api login --device
```

PowerShellでは、`iris api login --device` の前に `$env:IRISBOOKS_APP_BASE = 'https://irisbooks.io'` と
`$env:IRISBOOKS_API_BASE = 'https://irisbooks.io/api'` を設定します。ログインが成功すると、
その接続先がプロファイルに保存されます。`whoami` と `iris api books list` で、実際のアカウントと帳簿を確認します。
古いトークンを別サービスへコピーしたり、同じメールアドレス・帳簿 IDだからアクセスできると判断したりしないでください。
古いプロファイルとローカルファイルのバックアップを残します。
アクセスできる既存のクラウド帳簿は、未作成・空のフォルダへcloneして比較する方法を優先します。
既存のローカル帳簿を使う場合は、[接続の条件](cli-reference.md#iris-api-books)に従って新規作成と既存への接続を明示的に選び、
接続変更後に保持された状態、競合、同期結果を確認します。
開発・betaのプロファイルを書き換えたり、別アカウントのデータを上書きして移行済みに見せたりしないでください。
認証情報や帳簿が自動コピーされる手順ではありません。

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

帳簿フォルダの外で作成する場合は、`--name`・`--fy`・`--region` を指定します
（地域に既定値はありません。通貨は `--currency` を省略すると地域の通貨になります）。

```bash
iris api books new --name "Acme Design" --fy 2026 --region JP
```

ほかに `--currency`・`--scale`・`--no-link`・`--idempotency-key` が使えます。作成時に表示される再試行キーを保存してください。
成功したか分からない場合は、同じ `--idempotency-key <key>` で再試行すると、帳簿の
重複作成を防げます。ローカル帳簿の中では、安定したローカル ID から既定のキーを
作るため、同じ帳簿での再試行には同じキーが使われます。

`books link` にはリンク先の オーナー権限が必要です。PAT を使う場合は
`role:full` スコープも必要です。リンクできるのは、未変更の初期帳簿、または
ファイル履歴がないクラウド帳簿です。会計年度・地域・通貨・小数桁数・年度開始月を
照合し、ローカルの `config/book.yaml`（単位定義を含む）、勘定科目表、`AGENTS.md` を一つの
トランザクションで反映します。ローカル ID はサーバーの成功応答後に変更します。
使用済み・編集済み・締め済み、または確認後に更新されたリンク先は拒否されます。
別フォルダへ clone して比較し、残す内容を決めてください。`--force` でも、この
確認は省略しません。応答が失われた場合は、同じ内容で再試行できます。
この接続に対応していない古いサーバーでは、接続を拒否し、ローカルのリンクは変更しません。

同期状態は `.iris/sync/binding.json` に記録した API 接続先とクラウド帳簿 ID の組で
管理します。接続先かクラウド帳簿 ID のどちらかが変わったとき、または接続先を確認できない古い形式の
同期状態を開いたときは、それまでの `.iris/sync/` 全体を
`.iris/sync-before-link-<suffix>/` に退避し、同期状態を新しく作り直します。
保存先にはキュー・受領情報・カーソル・要確認記録・スナップショット・設定と締めの
オフライン情報が含まれます。復旧時は内容を確認し、別の接続先へ旧受領情報を
コピーしないでください。ID の書き込みに失敗した場合は旧状態を復元します。
接続先も ID も同じであれば、同期状態はそのまま使います。同期・リンク処理中は帳簿をロックするため、
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

### iris api grants

帳簿のアクセス権を管理します（オーナーのみ。ただし、メンバーは自分のアクセス権を
取り消して帳簿から抜けられます）。

```bash
iris api grants list [--json] <book-id>
iris api grants invite --role BOOKKEEPER --email EMAIL <book-id>
iris api grants role --role OWNER|BOOKKEEPER|REVIEWER <book-id> <user-id>
iris api grants revoke <book-id> <user-id>
```

`invite` が作るのは招待で、アクセス権ではありません。招待された人は、Web アプリで
承認したあとに帳簿を開けます。`list` は各行の状態（`member` または `invited`。
`--json` では `"status": "active"|"pending"`）を表示し、招待中のユーザーに
`revoke` を実行すると招待を取り消します。すでにメンバーの人を招待すると、役割の
変更になります。招待を承認する CLI コマンドはありません。

### iris api inbox

帳簿の受信メール管理: 受信アドレスの表示、送信者許可リストの管理、隔離
メールの確認。「メールで書類を取り込む」を参照してください。

```bash
iris api inbox show [--json] <book-id>
iris api inbox allow <pattern> <book-id>       # user@host または *@host
iris api inbox disallow <pattern> <book-id>
iris api inbox quarantine [--json] <book-id>
```

### iris api balance / holdings / history

```bash
iris api balance [--as-of YYYY-MM-DD] [--json] <book-id>     # サーバー側試算表
iris api holdings [--as-of YYYY-MM-DD] [--json] <book-id>    # 単位ごとの純ポジション
iris api history [--path PATH] [--from D] [--to D] [--all] [--limit N] [--json] <book-id> # 訂正・削除の履歴
```

**出力形:**

```text
balance   { currency, currencyScale, totalDebit, totalCredit,
            rows[{ account, code?, debits, credits, type?, net }] }
holdings  [ { account, unit, unitScale, quantity } ]
history   [ { id, path, op, sha?, versionId?, sizeBytes,
              actor, actorDisplay?, source?, reason?,
              postSealPeriod?, movedFromPath?, ts } ]
```

金額は帳簿通貨の10進数、`quantity` はその単位の桁数（`unitScale`）の10進数で、
仕訳ファイルと同じ書き方です。`holdings` は単位が付いた行だけを数え、
正味ゼロのポジションはサーバー側で除かれます。

`history`（訂正・削除の恒久的な記録）の `actor` は安定したアカウント識別子
（監査上の身元）で、`actorDisplay` はそれをサーバーが読み取り時に名前や
メールへ解決した人間向けの表示です。`postSealPeriod` は、その会計年度を
締めた**後**に着地した変更に付きます — 監査人が探すのはこの印です。
`movedFromPath` は削除+作成ではなく改名であったことを記録します。

`history` は、絞り込まなければ新しい順に 100 件を返します。

- `--path` — 1つのファイルの履歴。
- `--all` — すべてのイベント。帳簿は1会計年度なので、これがその年度の記録の
  すべてで、締め後に行った訂正も含みます。
- `--from` / `--to` — 2つの日付の間に行われた変更。日付は帳簿のタイムゾーン
  （帳簿の地域のタイムゾーン）で解釈します。

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
新しく登録する価格の revision は 0 です。既存の価格を訂正するときは、一覧に表示された
revision を `add --revision N` に渡します。古い revision を指定して別の値に訂正しようと
すると、競合になります。価格と出典が登録済みの値と同じであれば、再送しても競合に
ならず、登録済みの値が返ります。

`iris api networth` は指定したクラウド帳簿 1 冊だけを評価します。
帳簿横断の合計・推移・変動要因・集計対象設定は CLI から削除しました。
横断集計にはローカルの `iris networth` または Web アプリを使います。
Web とリモート MCP のクラウド横断集計は、ユーザーごとに UTC 日付あたり
最大1回自動生成する共通スナップショットを使います。日付や帳簿の選択を変えても、
再生成はしません。同期済みの変更を今すぐ反映するには、Web アプリのダッシュボード
または純資産で「**集計を実行**」を選びます。集計時点と次回の自動更新時刻が応答に含まれます。

## インストールとリファレンス

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

マニュアルは地域に依存しない内容です。地域ごとのルールは、この実行ファイルに
同梱されたオーバーレイのカタログが説明し、章の後に別のグループとして並びます。
`region/<cc>` は地域ガイド（その地域のどのパッケージを選ぶか、パッケージに
含まれない作業は何か）、`overlay/<id>` はパッケージの README と英語のガイドです。
これらのトピックは冒頭でオーバーレイのトピックであることを示し、パッケージの
正確な版を記載します。帳簿で使われるのはその帳簿が固定した版で、異なる場合が
あります。その版は `iris overlay guide` で読めます。

フラグはトピックの前後に置けます。トピックを指定すると、既定で節の一覧を返します。
`--list` でも同じ一覧を明示的に指定できます。`--section` は指定した節と下位の節、
`--full` は章の全文を読みます。これらの指定は併用できません。一覧には語数も含みます。
JSON には `version`・`source: "bundled"`・`language: "en"`・`words` と、指定に応じて
`topics`・`sections`・`markdown` が含まれます。各トピックには `kind`（`manual` または
`overlay`）があり、オーバーレイのトピックには `region`、パッケージにはさらに `pin` が
付きます。存在しない指定は終了コード 2 で
確認方法を案内し、全マニュアルへ切り替えることはありません。
実行方法は `iris <command> --help`、クラウドの利用条件や認証手順は現在の
オンライン情報も確認してください。資料の参照は操作の許可にはなりません。
ローカル MCP の `read_docs(topic?, section?, outline?, full?)` も同じ内容を返し、
帳簿の指定は不要です。トピックだけなら節の一覧、`full=true` なら章の全文です。
オフライン資料の参照先には `iris docs` コマンドを示し、MCP でも同じ topic と section を使えます。

### iris --version

```bash
iris --version          # iris 0.3.31
iris --version --json   # {"version": "0.3.31"}
```

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

帳簿の操作中に自動で通信することはありません。`iris view` の **設定 → このアプリについて**
も、求められたとき（または自動確認にチェックを入れた場合は1日1回）に同じ確認と更新を行います。`IRIS_DL_BASE` でダウンロード元を
指定できます（既定は `https://irisbooks.io/dl`）。既定のダウンロード元が置くのは最新の
リリースだけで、そこにないファイル（古いバージョンなど）はリリース用リポジトリ
`https://github.com/irisbooks/iris/releases` から取得します。インストーラーも同じです。
`IRIS_DL_BASE` で指定したダウンロード元には、この切り替えはありません。どちらの場合も、
署名は組み込みの公開鍵で必ず検証し、
`minisign` のインストールは不要です。検証に失敗した場合、古い実行ファイルは残ります。
開発版の置き換えや、古いバージョンへの更新は自動では行いません。

`.mcpb` の場合、確認結果に対応するバンドルの URL が表示されます。クライアントの
拡張設定から入れ直してください。CLI の更新後は帳簿のフォルダで `iris onboard` を
再実行し、MCP を再起動します。`check_update` で AI が使うバージョンを確認してください。
Windows で使用中のファイルを置き換えられない場合は、MCP サーバーを停止して再実行します。
このコマンドがない古い版は、まずインストーラーで更新します。

### iris uninstall

iris そのものをこのマシンから削除します。削除するのは次のものです。

- iris がインストールした場所の iris バイナリと、実行中の iris
- サインイン情報とローカル設定（`~/.config/irisbooks`）。CLI セッションは、削除の前に
  サーバー側で失効させます
- Claude Code スキル
- マシン全体の MCP 登録（Claude Desktop・Codex CLI）
- `iris onboard --install-path` が追加した PATH 設定
- [`iris view --add-launcher`](#iris-view) が追加した IrisBooks ランチャー
動いている `iris view` は先に終了します。実行前に、このマシンで見つかった削除対象の
正確な一覧を必ず表示し、確認を求めます。パッケージマネージャーで入れたものなど、
iris がインストールしたものではない `PATH` 上の `iris` は、名前を表示するだけで削除しません。

帳簿には一切触れません。帳簿はあなたのファイルであり、iris を削除してもそのまま残ります。フォルダ独自の
`.irisbooks/` も残ります。帳簿内の
エージェント設定（帳簿内の `.mcp.json`）もそのまま残ります。それも消したい
場合は、先に `iris offboard --book-path PATH` を実行してください。

```bash
iris uninstall [--yes] [--dry-run]
```

| フラグ | 意味 |
| ---- | ------- |
| `--yes` | 確認プロンプトを省略する |
| `--dry-run` | 削除計画の表示のみで、何も削除しない |

## 環境変数

| 変数 | 用途 |
| --- | --- |
| `IRIS_API_TOKEN` | パーソナルアクセストークン。キャッシュ済みログイントークンより優先 |
| `IRISBOOKS_TOKEN_FILE` | トークンの保存先。アカウントと環境の組合せごとに専用フォルダを使う（既定: `~/.config/irisbooks/token.json`） |
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
| `3` | 同期を続けられない切断（帳簿の削除、アクセス権の取り消し、セッションの失効）。同期コマンドのみ |
