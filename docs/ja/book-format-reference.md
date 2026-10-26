# 帳簿ファイル形式リファレンス

帳簿はプレーンな Markdown と YAML のフォルダです。このページはその中身の
リファレンスです。これらを手書きする場面はほとんどありません（AI が書き、
`iris validate` がチェックします）が、形を理解しておくと役立ちます。

## フォルダ構成

```text
your-book/
├── config/
│   ├── book.yaml                 # 識別情報・地域・会計年度・通貨
│   ├── chart-of-accounts.yaml    # 勘定科目
│   ├── rules.yaml                # 任意の分類ヒント（空でも可）
│   ├── balance-assertions.yaml   # 任意: 資料に基づく科目別残高
│   └── overlays/                 # 任意: この帳簿独自のオーバーレイ層（ルール・レシピ）
├── raw/                          # 元資料。構造は自由、種類は中身から判別
├── journals/
│   └── YYYY-MM/
│       └── YYYY-MM-DD-<取引先>-NN.md
├── assets/
│   └── YYYY/<asset-name>.md       # 固定資産（取得年別）
├── filings/
│   └── <recipe>.md           # 申告用の集計値の記録（オーバーレイのレシピが書く）
├── notes/
│   ├── workflow.md  decisions.md  open-questions.md  todos.md
│   └── raw/<raw/ のミラー>.md      # パースキャッシュ
├── compiled/                      # AI 生成レポート（再生成可能）
├── README.md  AGENTS.md  CLAUDE.md   # 人間・AI 向けガイド
└── .iris/                         # 実行時状態 — 手で編集しない
```

補足:

- 1つの帳簿は1会計年度分です（`book.yaml` の `fiscal_year`）。
  `journals/YYYY-MM/` のフォルダ名は、仕訳の会計日付（`date:`）の年と月、
  つまり日付の先頭7文字です: `2026-07-15` → `journals/2026-07/`。
  会計年度の開始月にかかわらず同じで、4月始まりの帳簿でも `2027-02-15` は
  `journals/2027-02/` に置きます。フォルダは常に会計日付を反映し、
  仕訳が対象とする期間ではありません。
- フォルダはファイル**内**の日付のキャッシュにすぎず、ファイルが正です。
  別のレイアウトでも壊れることはありません（レポート・シール・
  エクスポートはフォルダではなく日付を読みます）。`iris organize` が
  置き場所のずれた仕訳を正規レイアウトに戻します。
- ファイル名は仕訳の恒久的な識別子です。あなたや AI が書くファイルは
  `YYYY-MM-DD-<取引先>-NN.md`、過去にサーバーで作られた仕訳は
  `YYYY-MM-DD-<取引先>-jNNN.md` です（取引先は元の表記のまま）。
  どちらも正しい形で、連番が別なので衝突しません。現在の Web アプリとリモート
  コネクタでは仕訳を作成できません。変更はローカルで作成して同期します。
- `.iris/` はローカルの帳簿 ID と同期状態を保持します。マシン固有で同期されません。

## `config/book.yaml`

```yaml
schema_version: 1
book_id: lb_...                 # init 時はローカル ID。クラウド連携時に置き換わる
name: "Acme Design"
region: JP                      # ISO 3166-1。税・ロケールのルールを選択
overlays:
  - journal-balance@2026.10.1
  - inventory-disposal@2026.10.1
  - jp-tax-classification@2026.10.1
  - jp-tax-amount@2026.10.1
  - jp-tax-filing@2026.10.1
  - jp-small-asset-deduction@2026.10.1
  - jp-declining-balance@2026.10.1
language: ja                    # ISO 639-1。勘定科目の言語はこれに従う
currency: JPY                   # ISO 4217
scale: 0                        # 補助単位の指数 — 不変（JPY 0, USD 2, BHD 3）
fiscal_start_month: 4           # 1〜12
fiscal_year: 2026               # この帳簿が扱う会計年度（この例では 2026-04-01〜2027-03-31）
created_at: "2026-06-20T12:34:56Z"

# 任意:
strict_accounts: false          # false = 勘定科目表に無い科目を許容（既定は厳格）

units:                          # 非通貨単位（外貨・暗号資産・貴金属・株式）
  - symbol: BTC
    scale: 8
    name: "Bitcoin"

consumption_tax:                # JP のみ — 日本の税務ページ参照
  status: taxable
  accounting: tax_included
  method: general
  business_class: 5
```

`units` は任意で、新しい帳簿では空です。既知の通貨の数量には内蔵の小数桁数を
使います（JPYは0、USD・EURは2、KWDは3）。このリストへの登録は不要です。
`units` に明示した設定は内蔵値より優先されます。BTCや株式などの独自単位は
登録が必要です。未知の単位は `scale` を必ず明示してください。整数のみの単位も
`scale: 0` が必要です。省略や `null` は、ローカル読み込み・帳簿同期・アカウントの
単位設定APIで拒否されます。たとえば `- {symbol: USD, scale: 4}` を登録すると、USDの
`quantity` に小数点以下4桁を使えます。
仕訳の金額は別で、帳簿のトップレベルの `scale` を使います。省略時は `currency`
に対応する内蔵値を使います。USDでも `scale: 0` と明示すれば0のままです。
クラウドで使う帳簿の金額は小数点以下0〜6桁、登録単位の数量は0〜18桁に対応します。
ログイン済みの `iris init` は取得できたアカウントの単位設定を取り込みます。
`--no-user-defaults` で省略できます。アカウント設定の変更は既存帳簿に反映されません。
上のBTCは記述例で、自動登録される単位ではありません。

`scale` は通貨が使う小数桁数で、**不変**です。JPY は `0`（円単位、小数なし）、
USD/EUR は `2`、湾岸ディナールは `3`。`consumption_tax` のような地域固有ブロックは
不透明に同伴します。普遍エンジンは無視し、JP オーバーレイが読み取ります。

`fiscal_year` はこの帳簿が扱う会計年度で、年度が始まる年で表します。`iris init` は
今日を含む年度を設定し（`--fiscal-year` で別の年度を選べます）、
[`iris yearend`](cli-reference.md#iris-yearend) は作成する帳簿に翌年度を
設定します。必須の項目です。`iris validate` とクラウドはこの行の無い `book.yaml` を
拒否し、クラウドはこの値の変更も拒否します。翌年度は新しい帳簿で、この帳簿の
書き換えではありません。

`overlay` は機能の固定バージョンを一つ指定します。`overlays` では複数の
固定バージョンを選択できます。ローカルクライアントは帳簿内の
`config/overlay-packages/` にある定義だけを実行します。ここは、信頼済みの
帳簿独自の層 `config/overlays/` や、実行時状態の `.iris/` とは別の保存場所です。

検証済みコピーが帳簿内にあれば「利用可能」、固定バージョンを選べば「有効」、
定義の条件に合う記録では「適用対象」です。保存しただけでは有効になりません。
指定の省略・空リストでは追加パッケージは動作しません。共通補完にも明示的な
`journal-balance@<version>` や `inventory-disposal@<version>` のコピーと選択が必要です。基本の構造・会計チェックは常に
動作します。地域から暗黙に選ぶことはなく、コピーの不足や改変は代用せず診断します。
不足分は `iris overlay install` で明示的にコピーします。クラウドはファイルと
設定を保存しますが、Overlay の定義は評価しません。

同梱版からコピーしたパッケージは、信頼済みのリリース照合値を使って全ファイルの
内容を確認します。実行時に、そのバイナリが古い定義本体を持っている必要はありません。
ダウンロードしたコピーはリリース署名で確認します。帳簿に保存したバンドルの
ハッシュでも、実際のバイト列を確認します。照合値や署名だけで不足する定義を
補ったり、パッケージを有効にしたりすることはありません。

Bindings v4 では、仕訳のワークフロー状態と承認・締めの情報を Overlay の入力から
除きます。入れ子の記録も対象です。`journal.status` を読む定義や、これらの情報を
書き換える定義は、互換性エラーになります。`consumption_tax.status` などの業務上の
事実は引き続き使えます。下書きだけを補完する制約、記帳権限、締め、集計対象の
状態は、アプリケーション側で管理します。

Bindings v5 では、仕訳の補完前に追加フィールドを計算できます。
パッケージの `points.yaml` に、名前空間付きの ID、インターフェースのバージョン、
`classify` または `calculate` の段階、出力先の明細フィールド、入力項目を宣言します。
入力・出力は単一の値に限ります。計算する側は `derive/*.yaml` の `point` と
`point_version` で対応する定義を指定し、`inputs` と型付きの `params` だけを読みます。
補助関数はパッケージごとに独立しています。フィールドの型は定義元のものを使い、
別パッケージが計算する場合は、対応する定義元のバージョンも宣言します。
1つの定義に対して計算する側は1つです。必須の計算がない、互換性がない、複数の
計算が競合する、出力先が重複する、依存が循環する場合は有効化できません。
任意の定義では、記録済みの値を使う `fallback: recorded` を明記します。
適用条件に合う場合は、型定義で `required` とされた入力をすべて記入する必要があります。
計算の適用対象は、計算定義自体の条件で決まります。

この計算は、貸借が一致した下書きで未記入の追加フィールドだけを埋めます。
記録済みの値、基本の仕訳金額、ワークフロー状態は変更しません。
分類から計算への依存を `after` に宣言し、各段階を一度だけ実行します。
上限は定義が16個、明細が64行、文字列が4,096バイト、1回の入力とパラメーターが
計64 KiBです。実行記録は256件・計64 KiBまでです。式と呼び出す補助関数は
展開後の構文木で4,096ノードまでとし、内包表記は使えません。
式の計算コストは1回100,000、全体1,000,000までで、補助関数と文字列の生成も含めます。
計算後の候補は、通常の検証でも確認します。

埋めた値には、定義元・計算元の固定バージョンと入力・パラメーターを保存します。
保存先は明細の `preparation_source` で、対象フィールドと同じ階層に対応します。
この情報はアプリケーションが記録し、計算の入力・出力には指定できません。
帳簿独自の `book:<hash>` を参照する場合は、仕訳を書き込む前に定義を保存します。
`iris validate` は無効化後も帳簿内の同じ定義で再計算します。
元の記録や結果が変わればエラーになり、定義がなければ検証できない旨を警告します。
現在の帳簿設定を保存済みの入力の代わりに使うことはありません。
検証がこの計算を実行して記録を修正することもありません。

ローカルの Overlay 検証では、フィールドの条件、補助関数、帳簿集計、値の提案、
保存済みの結果の再計算に共通の上限を設けています。CLI は帳簿全体で上限を共有し、
補完とタスク情報の取得も、それぞれ1回の処理全体で計算量を数えます。
上限は計算コストが50,000,000、式の評価が1,000,000回、処理する入力が512 MiB、
問題の出力が10,000件・計1 MiBです。通常の式は1回のコストが5,000,000、
展開後の構文木が32,768ノードまでです。追加フィールドの計算には、前述のより厳しい
上限が適用されます。償却表と集計グループは4,096行、集計元は100,000明細、
過去の定義の参照は64種類までです。計算結果のデータ化は256 KiB・16段・4,096値、
表示するメッセージは16 KiBまでに制限します。入力の展開や償却表の生成で大量の
メモリーを確保する前に、上限を確認します。
上限に達すると `overlay.checks-incomplete` エラーになり、`iris validate --apply` は
先に得た提案も書き込みません。型や式の通常の警告とは区別し、貸借一致などの
基本の検証は続けます。

分析ファイルのスキーマ v5 は、帳簿設定・固定資産・仕訳明細の追加フィールドを固定の
`record_fields` 表に保存します。元の帳簿・パス・明細番号を保持し、大きな整数、
`null`、配列も JSON の値として扱います。追加フィールドのオブジェクトは1つあたり
256 KiB、入れ子は16段、値は4,096個までです。極端に小さい数や桁数の多い数が
取り出し時に丸められないよう、フィールドのパスごとに元の JSON 表記も保存します。
この索引はエスケープ前で1オブジェクトあたり4 MiB、索引を含む全体では64 MiBまでです。
アプリケーションが用意したクエリで、件数を制限した読み取り、値の一致による
絞り込み、型を区別したグループ化、整数の `SUM`・`COUNT` を使えます。
整数は38桁の十進数で正確に合計します。小数の合計は、誤差を補正する浮動小数点計算を
使った近似値で、`≈` を付けます。値や合計が計算できる範囲を外れた場合は、合計を
表示しません。数に見える文字列は数値に変換しません。合計できない値も元の表記で
確認できます。絞り込みとグループ化では保存した JSON の表記を比較するため、
同じ数でも表記が異なれば別のグループになります。追加フィールドに引用符なしで
書いた JSON 形式の数が YAML の標準の数値型に収まらない場合も、数値の表記を
保持します。引用符で囲んだ数は、ローカルで書き直しても文字列のままです。
会計金額には従来どおり整数の規則を使います。配列やオブジェクトは元の1件の
まま扱うため、会計金額が配列の要素数だけ重複することはありません。
固定資産は元の記録1件につき1行で、`kind = 'asset'`、`line_index = -1` となります。
クラウドは受理済みの参照用データから値を取り出し、Overlay の定義は実行しません。

## 複数の公開オーバーレイを固定する

`overlays` には、使いたいオーバーレイの**固定バージョンを複数指定**できます。
`overlay` と同時には書けません。地域共通のパッケージと専門分野のパッケージを
組み合わせる場合は、次のように書きます。

```yaml
# 設定例です。jp-rsu は、公開されてから指定できます。
overlays:
  - jp-tax-classification@2026.10.1
  - jp-rsu@2026.10.1
```

すべての固定バージョンに、検証済みの帳簿内コピーが必要です。
`iris overlay install` で明示的にコピーします。キャッシュを更新する `fetch` だけでは
帳簿の動作は変わりません。1 つでも不足すればローカル検証はエラーになり、
どちらの指定形式でも別のバージョンに置き換わることはありません。
同じパッケージの重複、地域・依存関係の不一致、公開ルールの ID やフィールド定義の
衝突もエラーです。列挙する順序で優先順位は変わりません。各パッケージの CEL 関数は
その内部で使い、レシピの出典には、そのレシピを持つパッケージのバージョンを記録します。

パッケージの `overlay.yaml` には `region: JP` や、対応する依存バージョン
`requires_overlays: {jp-tax-classification: ['2026.10.1']}` を宣言できます。新しい科目選択や
パラメーターの仕組みを使う場合は `requires_bindings: 2` を指定します。
`iris overlay upgrade --dry-run` で、更新後の組み合わせ、テスト、帳簿独自の層、
設定値を確認できます。`--to jp-rsu@<version>` ならそのパッケージだけを更新し、
`--to` を省略すると、固定している各パッケージの最新版をまとめて確認します。

初期カタログは、個別に選べる七つの機能で構成します。いずれも `2026.10.1` の
公開候補で、bindings 5 が必要です。

| カタログの分類 | 個別に選べる Overlay ID |
| --- | --- |
| 共通補完 | `journal-balance`、`inventory-disposal` |
| 日本の消費税 | `jp-tax-classification`、`jp-tax-amount`、`jp-tax-filing` |
| 日本の固定資産 | `jp-small-asset-deduction`、`jp-declining-balance` |

分類は発見・配布のためのまとまりで、切り替え単位ではありません。
新規の日本向け事業用帳簿には七つをコピーして選択します。個人用と日本以外の事業用は
共通補完の二つを選択します。既存帳簿の固定バージョン、無効設定、保持済みの過去の
定義は変更しません。署名付きの公開は未実施です。

`jp-tax-amount` と `jp-tax-filing` は、それぞれ
`jp-tax-classification@2026.10.1` の明示的な選択を必要とし、互いには依存しません。
税設定の定義と参照用タスクは区分検証が所有します。税区分の検証を残して税額補完や
申告計算だけを止められます。貸借補完と売却原価計算、少額資産特例の検証と定率法計算も
個別に選べます。依存関係が不足した選択は拒否し、自動取得・自動解除は行いません。

各機能には必要な検証、項目、タスク、ガイド、実行可能な例をまとめます。
Iris 本体の構造・貸借検証は常に動作し、レシピは明示的に呼び出します。
課税状況、届出、適用要件は確認して記録します。一括償却資産と期中取得の定率法計算は
対応範囲外です。従来の統合版 `default`・`jp` と大分類単位の旧候補は廃止しました。

バイナリにはオフライン導入用のカタログを同梱し、その他の版は署名付き GitHub
リリースから取得して明示的に導入します。実行と過去の再現は帳簿内の正確なコピーを
読みます。機能を無効にしても記録済みの結果と出典は保持します。将来のバイナリが
過去の定義本体を同梱しなくなっても、信頼用のハッシュは残します。

## フィールドの候補値と手順を調べる

`iris overlay list --json` で、固定バージョン、ルールの `when`・`assert`、
パラメーターの定義、フィールドの候補値、手順書の ID を確認できます。ローカル MCP
では `describe_overlay` が同じ情報を返します。親フォルダーを使うサーバーでは
`book` も指定します。確認できるのは、その帳簿で実際に使うバージョンの定義です。

公開パッケージは、必要に応じて `fields.yaml` を持てます。

```yaml
fields:
  line.sales.channel:               # 対象.関心分野.フィールド名
    type: string
    description: {en: Sales channel, ja: 販売チャネル}
    enum:
      - {value: online, label: {en: Online, ja: オンライン}}
      - {value: store, label: {en: Store, ja: 店舗}}
```

この例で帳簿に保存する値は `online` と `store` です。ラベルは表示に使います。
`required: true` がなければ、省略できます。CEL の `when` で適用条件を指定することも
できます。値を記録した場合は、型と候補値が検証されます。フィールド定義を持たない
既存のパッケージでは、まずルールの `assert` に書かれた候補値を確認してください。
構造化した定義を追加するには、新しい公開バージョンか、帳簿独自のフィールド定義が
必要です。

パッケージの `guides/*.md` には、その処理の手順を書けます。表示された ID を使って
`iris overlay guide <id> [path]`、またはローカル MCP の `read_overlay_guide`
（引数 `guide`）で読みます。手順書は固定したパッケージの参考資料として扱います。
それを読むだけで、編集や提出の許可が与えられることはありません。

Web とリモート MCP は、ローカルの評価エンジンを使わずに保存された定義や文章を読みます。
`required`・`when` の定義が返っても、クラウドが適用可否を判定したことにはなりません。
同期済み帳簿のリビジョンを示し、未同期の変更は含めません。
帳簿独自の `config/overlays/guides/` に置いた Markdown は、1ファイル64 KiBまでの
データとして同期します。保存されているだけでは、信頼済み・有効とは扱いません。

## 帳簿ごとにルールとレシピの入力を設定する

ルールは、`when` に当てはまる記録を `assert` で検証します。条件に一致しただけで
帳票が作られるわけではありません。派生はフィールドの値を提案し、レシピは償却表や
集計値を計算します。いずれも `params` に名前・型を宣言し、既定値や `enum` の
候補値を付けられます。ルールと派生の式は `params.<name>`、レシピの式は
入力名をそのまま使います。

科目を選んでメモを必須にするルールなら、次のように書けます。

```yaml
rules:
  - id: sales.memo-required
    target: line
    params:
      - {name: accounts, type: account_selector, default: {exact: ['収益:Sales']}}
    when: account_matches(line.account, params.accounts)
    assert: line.memo != ''
    message: {en: A selected sales line needs a memo., ja: 対象の売上明細にはメモが必要です}
```

帳簿固有の入力は `config/book.yaml` の `overlay_settings` に保存します。
パッケージ ID、`rules`・`derivations`・`recipes` の種類、項目 ID の順に指定します。

```yaml
# 以下の項目を持つパッケージを使う場合の設定例です。
overlay_settings:
  jp-sales-demo:
    rules:
      sales.memo-required:
        params:
          accounts: {contains: うりあげ}  # 大文字・小文字を区別する部分一致
    derivations:
      sales.channel:
        params: {channel: store}         # 宣言された候補値から選ぶ
    recipes:
      monthly-sales:
        params:
          accounts: {exact: ['収益:Sales']}
          from: '2026-09-01'
          to: '2026-09-30'
```

科目の選び方を表す `account_selector` には、`exact`（科目参照のリスト）、
`subtree`（科目パスと、コロンで区切られた配下の科目）、`contains`（部分一致）の
うち 1 つだけを指定します。空のリストや空の文字列は使えません。`うりあげ`・`売上`・
`Sales` を同じ意味だと推測する処理はありません。CEL の `account_matches` は
1 つの科目を判定し、`select_accounts(journals, selector)` は対象の明細を
`sums` に渡します。

設定値の日付・日時は `cutoff: '2026-09-01'` のように引用符で囲みます。
map や list の中でも同じです。引用符のない YAML の日付は同期前にエラーになります。
map・list の中の整数値は、ローカルでもサーバーでも整数として計算します。
小数部分がある値は double です。単独の入力に `double` 型を宣言した場合は、
その型を保ちます。

存在しない設定名、ルールの必須入力の不足、型の誤り、候補にない値はエラーです。
レシピの実行時に指定した値は、帳簿の既定値より優先されます。名前で選ぶ場合は、
実行前に仕訳から科目参照を確定し、並べ替えて出典に保存します。該当科目がなければ
エラーです。あとから帳簿の既定値を変えても、再検証は保存した入力を使います。
一方、仕訳の金額が変われば、保存済みの集計との不一致が検出されます。
月別売上の計算は、この仕組みを使う例であり、法定の申告書そのものではありません。

## 仕訳ファイル — `journals/YYYY-MM/*.md`

YAML フロントマター、続いて自由記述の Markdown 本文。

```markdown
---
schema_version: 1
date: 2026-05-04
payee: EXAMPLE.COM
status: draft                 # draft | posted
tags: [sales, withholding]
attachments:
  - path: raw/2026-05-example-com-invoice.pdf
    type: invoice               # invoice | receipt | bank_statement（因果的な出所）
    locator: "page=1"           # 任意の断片ポインタ（"L47", "p3"）
lines:
  - account: 資産:売掛金
    debit: 89790
  - account: 資産:事業主貸
    debit: 10210
  - account: 収益:売上
    credit: 100000
---

この取引が起きた理由（明細の再掲ではなく）。
```

| フィールド | 必須 | 補足 |
| --- | --- | --- |
| `date` | はい | `YYYY-MM-DD`。ファイル名の接頭辞と一致（生成された `0000-opening-balances.md` は例外） |
| `payee` | いいえ（推奨） | 母語表記可。ファイル名のスラッグはこれから導出 |
| `status` | はい | `draft` / `posted` |
| `tags` | いいえ | 小文字・自由形式、グルーピング用 |
| `attachments` | いいえ | `{path, type?, locator?}`。`type` 付きは因果的な出所 |
| `lines` | はい | 2〜999行。各行に `account` + `debit`/`credit` のどちらか一方 |
| `lines[].memo` | いいえ | 行ごとのメモ |
| `lines[].quantity` + `unit` | いいえ | `book.yaml` の `units` の単位の数量（常に正。向きは借方/貸方から） |
| `lines[].tax` | いいえ | 日本の消費税 — 下記参照 |
| 本文 | いいえ | 閉じ `---` の後の自由 Markdown |

**明細行数**。1つの仕訳は最大 **999行**です。200行から警告が出ます。給与や
減価償却の仕訳が数百行になるのは正常ですが、4桁は何かが誤って生成した数です。
本当にそれ以上必要な場合は仕訳を分割してください。日付とタグを揃えた複数の
仕訳は、1つの長い仕訳と同じように集計されます。

**金額**は通貨の自然な表記で、`scale` の桁数まで書きます。`scale: 0`（JPY）なら
円単位（`1000` = ¥1000、小数不可）、`scale: 2` なら ドルとセント（`12.34` = $12.34、
裸の `12` は $12.00 で $0.12 ではない）。内部はすべて整数の補助単位です。

**検証:** 借方=貸方、各科目が勘定科目表に存在（またはエイリアス一致）、日付が
ファイル名と一致、ステータスが正当、YAML が解析できる。レポートに載るのは
**記帳済み**の仕訳だけ。

**行ごとの `tax`（日本の課税事業者のみ）:**

```yaml
tax:
  category: taxable_purchase   # taxable_sale | taxable_purchase | exempt_sale |
                               # exempt_purchase | export_sale | out_of_scope | securities_sale
  rate: "10"                   # 10 | 8r | 8o | 5 | 3 | 0
  invoice: true                # 適格請求書を保有（仕入側）
  business_class: 5            # 簡易課税 事業区分 1..6（帳簿既定を上書き）
```

[日本の税務・コンプライアンス](japan-tax-and-compliance.md) を参照。

## 省略できる項目と自動で決まる値

共通の設定は `config/book.yaml` にまとめます。通常の仕訳には日付、ステータス、
科目と金額を記録し、必要に応じて取引先、証憑、メモを添えます。
次の値は、明細行ごとに繰り返す必要がありません。

| 値 | IrisBooks が使う値 | 指定する場所 |
| --- | --- | --- |
| 金額の通貨 | 帳簿の `currency` | `config/book.yaml` に一度指定 |
| 金額の小数桁数 | 帳簿の `scale`。省略時は通貨に組み込まれた桁数 | 帳簿作成時に指定。作成後は変更不可 |
| 数量の小数桁数 | `units` の指定を優先。指定がなければ既知の通貨の桁数 | 独自の単位は `config/book.yaml` に一度定義。整数単位も `scale: 0` を明記 |
| 数量の向き | `debit` または `credit` のキー | 各行にどちらか一方を指定。`quantity` は常に正の数 |
| 仕訳の識別子 | ファイル名 | 仕訳 ID のフィールドは不要 |

金額だけを記録する行では、`quantity` と `unit` を両方省略します。
株式などの数量を管理する場合は、その数量が動く行に両方を加えます。
たとえば JPY の帳簿で、`FUND` を `scale: 0` で定義し、次の2科目を
勘定科目表に登録してあれば、`journals/2026-10/2026-10-20-fund-01.md`
にこの仕訳を書けます。

```markdown
---
schema_version: 1
date: 2026-10-20
status: draft
lines:
  - account: Assets:Investments
    debit: 100000
    quantity: 10
    unit: FUND
  - account: Assets:Bank
    credit: 100000
---
```

10単位を10万円で購入した仕訳です。通貨、数量の向き、単位の小数桁数を
仕訳の属性として追加する必要はありません。日付とステータスは明記します。
`draft` の間は、通常のレポートに載りません。

[ポートフォリオ分析](cli-reference.md#iris-analytics)では、購入行から取得分を
識別できるため、単純な購入に `lot` のラベルは不要です。売却時の原価配分は、
**先に取得した分から使う先入先出法（FIFO）が既定**です。
科目と単位の組み合わせごとに、独立して計算します。対象に一致する
`inventory.params.method` の明示指定を優先し、指定がなければ分析では
期首在庫に保存された方法を引き継ぎます。どちらもなければ FIFO を使います。
対応する値は `fifo`、`specific`、`moving-average` です。
個別法（`specific`）では、売却ごとにロットを選びます。
取得履歴や期首の取得原価が不明なら、取得原価は不明のままです。

ローカルの比較レポートでは、仕訳を編集・記帳せずに売却原価と損益を計算します。
原価の調整が必要な場合は、損益の計上先を `config/book.yaml` に一度指定します。

```yaml
inventory:
  params:
    gain_account: Income:Gain
```

科目の存在を厳密に検証する帳簿では、この科目を勘定科目表に登録してください。
FIFO なら方法の指定は不要です。移動平均に変える場合は、帳簿または選択する
ビューに `method: moving-average` を指定します。`accounts.exact` の省略時は、
数量を持つ資産科目が対象です。科目を絞る場合はこの項目を、単位を絞る場合は
`commodity` を指定します。
計算結果は `iris report pl --mode comparison` で確認できます。
比較レポートの JSON は `selection.inventoryMethods`、分析用 SQL は
`inventory_method` に方法を表示します。純資産画面でも、数量を持つ科目の横に
方法を表示します。通常の検証と承認済みレポートは記録済みの仕訳を使い、
比較で計算した仕訳は未承認のままです。

売却の下書きを補完するには、入金額と数量を記録し、原価を `credit: null` に
します。上の損益科目を設定し、購入仕訳を記帳済みにしたうえで、次を
`journals/2026-10/2026-10-21-sale.md` に保存します。

```markdown
---
schema_version: 1
date: 2026-10-21
status: draft
lines:
  - account: Assets:Bank
    debit: 70000
  - account: Assets:Investments
    credit: null
    quantity: 5
    unit: FUND
---
```

`iris journal complete journals/2026-10/2026-10-21-sale.md` を実行すると、
保有科目の貸方5万円と、利益の貸方2万円をプレビューします。
`--apply` とプレビューの `--revision` で適用できます。
帳簿内の `inventory-disposal` Overlayを明示的に選択していれば、仕訳の属性を追加せずに
在庫の補完を使えます。`iris context` で選択を確認してください。無効・未配置の
パッケージが暗黙に使われることはありません。
手数料があれば、費用の行に明記してください。`journal-balance` を選択した通常の仕訳は、
貸借を合わせる1行を `debit: null` または `credit: null` にできます。
補完後も下書きのままで、検証は記録された金額を確認します。
操作は [iris journal complete](cli-reference.md#iris-journal-complete) を参照してください。

## 投資信託の口数・一部売却・時点別の評価を確認する

この管理用の架空帳簿では、100,000口を100,000円で購入し、20,000口を26,000円で
売却します。残る80,000口の取得原価は80,000円です。新しいサンプル用フォルダで
試してください。以下の銀行・証券会社・価格の資料はすべて架空です。商品や税制の
適用を選ぶ例ではありません。

`config/book.yaml` と `config/chart-of-accounts.yaml` を次の内容で保存します。
口数の `scale` は1口の小数点以下の桁数で、基準価額が10,000口当たりで表示される
こととは別です。この例は管理上の計算方法として `moving-average` を明示します。
購入が1回なので対応する汎用の方法では取得原価が一致しますが、税務上の計算方法を
決めるものではありません。

```yaml
schema_version: 1
book_id: fund-2026
name: Synthetic fund management example
region: JP
language: en
currency: JPY
fiscal_year: 2026
fiscal_start_month: 1
overlays: []
units:
  - {symbol: SYNTHFUND, name: Synthetic fund (one whole unit), scale: 0}
inventory:
  params: {method: moving-average, gain_account: Income:FundGain}
```

```yaml
schema_version: 1
accounts:
  - {path: Assets:Bank, type: asset}
  - {path: Assets:Fund, type: asset}
  - {path: Equity:Opening, type: equity}
  - {path: Income:FundGain, type: income}
```

次のフロントマターを、それぞれのMarkdownファイルの `---` の間に保存します。
例は確認済みの記帳後の状態です。実際の帳簿では下書きを確認し、帳簿の権限に従って
記帳してください。記帳時にYAMLの引用符が整えられることはありますが、金額・口数・
単位・資料参照・追加項目・本文は保持されます。クラウド接続済みの帳簿では、記帳の
コマンドが同期も行う場合があります。

`journals/2026-01/2026-01-01-opening.md`:

```yaml
schema_version: 1
date: 2026-01-01
status: posted
tags: [opening-balance]
lines:
  - {account: Assets:Bank, debit: 1000000}
  - {account: Equity:Opening, credit: 1000000}
attachments:
  - {path: raw/bank.csv, locator: L2}
```

`journals/2026-06/2026-06-01-fund-purchase.md`:

```yaml
schema_version: 1
date: 2026-06-01
status: posted
payee: Synthetic broker
lines:
  - {account: Assets:Fund, debit: 100000, quantity: 100000, unit: SYNTHFUND}
  - {account: Assets:Bank, credit: 100000}
attachments:
  - {path: raw/trades.csv, locator: L2}
  - {path: raw/bank.csv, locator: L3}
```

`journals/2026-08/2026-08-01-fund-sale.md`:

```yaml
schema_version: 1
date: 2026-08-01
status: posted
payee: Synthetic broker
lines:
  - {account: Assets:Bank, debit: 26000}
  - {account: Assets:Fund, credit: 20000, quantity: 20000, unit: SYNTHFUND}
  - {account: Income:FundGain, credit: 6000}
attachments:
  - {path: raw/trades.csv, locator: L3}
  - {path: raw/bank.csv, locator: L5}
```

独立した照合資料として、次の架空データを保存します。売却資料では売却した分の
取得原価20,000円と利益6,000円を確認し、銀行には売却代金26,000円全額が入ります。
この例には手数料・源泉徴収・為替換算・分配金・権利処理はありません。

`raw/trades.csv`:

```csv
id,date,side,units,cash_jpy,disposed_cost_jpy,realized_gain_jpy
BUY-1,2026-06-01,buy,100000,100000,0,0
SELL-1,2026-08-01,sell,20000,26000,20000,6000
```

`raw/bank.csv`:

```csv
date,balance_jpy
2026-01-01,1000000
2026-06-01,900000
2026-06-30,900000
2026-08-01,926000
2026-08-31,926000
```

`raw/holdings.csv`:

```csv
date,unit,units,carrying_cost_jpy
2026-06-30,SYNTHFUND,100000,100000
2026-08-31,SYNTHFUND,80000,80000
```

`raw/nav.csv`:

```csv
date,unit,quoted_nav_jpy,quoted_units
2026-06-30,SYNTHFUND,12345,10000
2026-08-31,SYNTHFUND,15000,10000
```

価格の資料は10,000口当たりです。12,345円÷10,000口は**1口当たり1.2345円**、
15,000円÷10,000口は1口当たり1.5円です。価格には小数点以下6桁まで記録できます。
`valueMicro` は1口当たりの価格を1,000,000倍した整数なので、それぞれ1,234,500、
1,500,000になります。仕訳の実際の口数100,000・80,000は保持してください。
価格表示の分母を単位の `scale` にしたり、仕訳の口数を減らしたりはしません。

架空の価格を試すときは、空の一時ディレクトリ内のトークンファイルを指定して、
利用者の価格ログを分けます。以降のコマンドでも同じ設定を使ってください。
サンプル帳簿のフォルダ内で実行します。

```bash
export IRISBOOKS_TOKEN_FILE="$(mktemp -d)/token.json"
iris price add --unit SYNTHFUND --currency JPY --date 2026-06-30 --price 1.2345 --source "Synthetic raw/nav.csv L2"
iris price add --unit SYNTHFUND --currency JPY --date 2026-08-31 --price 1.5 --source "Synthetic raw/nav.csv L3"
iris price list --unit SYNTHFUND --currency JPY --year 2026 --json
iris networth --as-of 2026-07-31 .
iris networth --as-of 2026-08-31 .
```

価格は帳簿の外で利用者単位に保存します。価格を記録しても単位や保有口数は追加されず、
仕訳の記帳や取得原価の変更も行いません。ローカルCLIとローカルMCPの `get_networth` は、
未同期の価格もすぐに使います。単一帳簿のMCPでは `books: ["."]`、親フォルダモードでは
対象の子フォルダを指定します。どちらも指定したローカル帳簿の記帳済み仕訳を読みます。

評価額を見る前に、現金と口数を別々に照合します。次を
`config/balance-assertions.yaml` に保存してください。ハッシュは上のCSVのバイト列に
対応し、`L` はヘッダーを含む物理行を指します。

```yaml
schema_version: 1
assertions:
  - id: bank-june
    date: 2026-06-30
    account: Assets:Bank
    measure: amount
    unit: JPY
    scope: posted
    expected: 900000
    evidence: {path: raw/bank.csv, sha: sha256:5668d77fe567be6f02992a4f7a6074acc1f51826e93ecbc2e634b3b9fba6aad9, locator: L4}
  - id: units-june
    date: 2026-06-30
    account: Assets:Fund
    measure: quantity
    unit: SYNTHFUND
    scope: posted
    expected: 100000
    evidence: {path: raw/holdings.csv, sha: sha256:c46a0507db7a04982d2724d1aacb0127b28df3c66a79f36ac24ca98c5a0d37c7, locator: L2}
  - id: cost-june
    date: 2026-06-30
    account: Assets:Fund
    measure: amount
    unit: JPY
    scope: posted
    expected: 100000
    evidence: {path: raw/holdings.csv, sha: sha256:c46a0507db7a04982d2724d1aacb0127b28df3c66a79f36ac24ca98c5a0d37c7, locator: L2}
  - id: bank-august
    date: 2026-08-31
    account: Assets:Bank
    measure: amount
    unit: JPY
    scope: posted
    expected: 926000
    evidence: {path: raw/bank.csv, sha: sha256:5668d77fe567be6f02992a4f7a6074acc1f51826e93ecbc2e634b3b9fba6aad9, locator: L6}
  - id: units-august
    date: 2026-08-31
    account: Assets:Fund
    measure: quantity
    unit: SYNTHFUND
    scope: posted
    expected: 80000
    evidence: {path: raw/holdings.csv, sha: sha256:c46a0507db7a04982d2724d1aacb0127b28df3c66a79f36ac24ca98c5a0d37c7, locator: L3}
  - id: cost-august
    date: 2026-08-31
    account: Assets:Fund
    measure: amount
    unit: JPY
    scope: posted
    expected: 80000
    evidence: {path: raw/holdings.csv, sha: sha256:c46a0507db7a04982d2724d1aacb0127b28df3c66a79f36ac24ca98c5a0d37c7, locator: L3}
```

```bash
iris validate
iris reconcile
iris report pl --mode comparison --from 2026-01-01 --to 2026-08-31
```

確認する結果は次のとおりです。

| 基準日 | 預金 | 口数 | 残る取得原価・帳簿価額 | 採用した価格の日付 | 投信の評価額 | 純資産評価額 |
| --- | ---: | ---: | ---: | --- | ---: | ---: |
| 2026-07-31 | 900,000 | 100,000 | 100,000 | 2026-06-30 | 123,450 | 1,023,450 |
| 2026-08-31 | 926,000 | 80,000 | 80,000 | 2026-08-31 | 120,000 | 1,046,000 |

この帳簿は在庫計算を選択しているため、ローカルの損益レポートでは
`--mode comparison` を指定します。計算結果は未承認の比較です。計算結果を保存して
承認する仕組みは未実装で、通常の承認済みレポートは拒否されます。

記帳済みの損益は収益・純利益6,000円、費用0円で、帳簿上の純資産は1,006,000円です。
残りの値上がり40,000円は管理上の評価差額です。収益の仕訳を重ねて追加しません。
7月末の評価には6月の価格を使い、未来の8月の価格は使いません。`asOf` は評価の基準日、
`priceDate` は実際に使った観測値の日付です。採用された価格が古いこともあります。

次の不足は、それぞれ処理が異なります。

| 不足する情報 | 結果と確認方法 |
| --- | --- |
| 市場価格 | 80,000口と取得原価は残ります。8月末は帳簿価額による1,006,000円に戻り、`SYNTHFUND` が `unpriced` になります。日付付きの1口当たり価格を記録します。 |
| 取引行の口数・単位 | 価格から口数は復元できません。貸借と預金残高が合っていても口数の照合は失敗します。証券会社の資料から口数を補います。 |
| 根拠のある期首取得原価 | 期首の口数と帳簿価額が分かっても、取得原価は不明なままです。市場評価はできる場合があります。現在価格から取得原価を推定せず、確認済みの期首在庫情報を引き継ぎます。 |

`iris yearend --local --to ../fund-2027` の確認済みの例では、80,000口と、別に保持した
取得原価80,000円を翌年度へ引き継ぎます。価格は利用者の保存領域に残ります。
8月の観測値を翌年1月にも使えても、観測日が新しくなるわけではありません。

実際の記録を同期する権限がある場合、帳簿の同期は仕訳・単位をクラウドへ送り、
`iris price sync` は別に保存した利用者の価格ログを照合します。価格の同期では
レポートを再生成しません。価格の送信が成功しても、帳簿の同期が受理された証明にはなりません。

| 表示先 | 入力と更新時点 |
| --- | --- |
| ローカルCLI・ローカルMCP | 現在の記帳済みファイルと有効なローカル価格を読みます。未同期の価格も含み、再実行すると読み直します。 |
| 単一帳簿の `iris api networth --book-id …` | クラウドで受理された帳簿の投影と利用者の価格を使います。未同期のローカル入力は含みません。 |
| Webの純資産・リモートMCP | 固定した分析データを使います。生成時の `generatedAt`、帳簿のリビジョン、各 `priceDate` を確認します。価格訂正の反映は、日次の自動生成か権限に従ったWebからの更新を待つ場合があります。再生成中も前回成功した結果が残ることがあります。 |

SQLの実行例では、8月の価格を1.6円に直しても、旧レポート1,046,000円はそのまま残ることを
確認しています。新しく生成すると1,054,000円になり、口数と取得原価は変わりません。

**税制の参照先（2026-10-24確認）：** 運用会社の
[基準価額の説明](https://direct.smd-am.co.jp/learn/guide/price/)で、10,000口当たりの
表示例を確認できます。[国税庁No.1464](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/1464.htm)
（法令等の基準日2026-04-01）は取得費と複数回購入した場合の計算方法を説明しています。
汎用のFIFO・移動平均という名前だけで、日本の税務処理が決まるわけではありません。
実際にNISA口座を使う場合は、証券会社が示す口座区分、
[金融庁の制度説明](https://www.fsa.go.jp/policy/nisa2/know/index.html)、
[最新の対象商品情報](https://www.fsa.go.jp/policy/nisa2/products/)を確認してください。
単位名やNISAと書いたメモ、検証の成功だけでは適用資格は分かりません。
申告書への転記と商品・税制の自動判定は、この管理用の例の対象外です。

## 残高照合

貸借が一致していても、預金残高が10円ずれていることはあります。資料で確認した
残高を記録し、`iris reconcile` でローカルの帳簿と照合してください。読み取り専用の
操作で、差額を埋める仕訳は作りません。任意ファイル
`config/balance-assertions.yaml` に観測残高を保存します。

たとえば、記帳済みの期首残高1,000円と支払10円なら、`Assets:Bank` の残高は990円です。
`raw/statement.csv` に次の資料があるとします。

```csv
date,description,closing_balance
2026-01-31,Month end,990
```

`iris hash raw/statement.csv` で元資料のハッシュを取得します。次のハッシュは、
この例のバイト列に対応する値です。確認した残高を次のように保存します。

```yaml
schema_version: 1
assertions:
  - id: bank-jan31
    date: 2026-01-31
    account: Assets:Bank
    measure: amount
    unit: JPY
    scope: posted
    expected: 990
    evidence:
      path: raw/statement.csv
      sha: sha256:47413ca394cff9cf18438ee55b45076994c84426b511e06fe5daafc3d05847bd
      locator: line 2 closing_balance
```

帳簿フォルダで `iris reconcile` を実行すると、記録上 `990`、資料上 `990`、差額 `0` と
表示します。支払の両側を誤って20円にすると、貸借は一致したままですが、照合結果は
`980`、`990`、`-10` になります。`iris validate` でも不一致を報告します。

- `date` はその日を含む基準日で、帳簿の会計年度内に指定します。期首残高も同じ年度に
  記録してください。対象に別年度の仕訳がある場合は、混ぜて集計せず拒否します。
- `account` は勘定科目表の完全なパスを1つ指定します。下位科目は自動合算しません。
  残高は科目の通常の向きで表し、資産・費用は借方を正、負債・純資産・収益は貸方を正とします。
- `measure: amount` は帳簿の通貨と金額の小数桁数を使います。外貨の数量や投資信託の口数は、
  `measure: quantity` と正確な `unit` を指定します。数量は借方・貸方の向きと単位の
  小数桁数で集計し、評価価格は使いません。数量の記録がなければ推測で補いません。
- `scope` の省略時は `posted`（記帳済み）です。下書きを含む未承認の確認には、
  `posted-and-drafts` を明示します。`expected` は指定の精度の自然な10進数、または
  引用符で囲んだ10進数文字列です。桁数を合わせるための丸めはしません。
- 元資料には、同期対象の `raw/` パス、`sha256:` のハッシュ、CSV の物理行や PDF のページ
  などの `locator` が必要です。金額が一致していても、資料がない場合や変更された場合は
  未確認のままです。ハッシュの一致はファイルの同一性を示すもので、金融機関による真正性や
  残高の転記が正しいことを証明するものではありません。

この任意ファイルには、重複しないIDで最大256件を記録できます。`assertions: []` なら
照合対象はありません。読み込みは仕訳10,000件・明細1,000,000行、元資料1ファイル16 MiB、
入力全体128 MiBまでです。出力の版は、取得した設定・科目表・照合記録・仕訳・参照資料に
対応します。クラウドでの受け入れを示すものではありません。同期・クローンで照合記録を
保持し、締めると設定とともにロックします。年度繰越では元の帳簿に残し、翌年度へ使い回しません。
クラウドへの保存だけでは照合を実行しません。年度締めのプレビューでは、受け入れ済みの
同期データを同じ共通処理で確認し、残高不一致や元資料の不足・変更があれば締めを拒否します。
受け入れ済みの版に対応する確認で、版を固定しない最新オブジェクトの取得や Overlay の
実行は行いません。同期後もプレビューに元データの不足・不一致が出る場合は、締める前に
サーバー側の集計用データを再構築する必要があります。財務用 ZIP に元資料が自動で
含まれるわけではありません。クラウドの年度締めでは、承認済みの各標準計算ビューを別々に照合します。ローカルの照合は、未解決のビューを引き続き拒否します。

## 費用の事業分と家事分を分ける

`iris allocation` は、費用の全額を、明示した事業割合で分けて計算します。
ファイルの変更や記帳は行いません。先に按分の根拠と会計上の扱いを確認してください。
勘定科目名から事業割合は判断できません。
[国税庁の必要経費の説明](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2210.htm)では、
家事関連費の事業分を取引記録などで区分する必要があります。
以下の1/4は所有者が確認したと仮定する架空の例で、推奨する割合ではありません。

次の入力を `raw/allocation-jan.json` に保存します。

```json
{
  "schema_version": 1,
  "gross_amount": "10001",
  "currency": "JPY",
  "scale": 0,
  "charge_kind": "expense",
  "period": {
    "from": "2026-01-01",
    "through": "2026-01-31"
  },
  "source": {
    "path": "raw/rent.csv",
    "sha": "sha256:e5a22bf56e640afc4880a0ef16dd353c3c56ead85111cd715d9b21dbe3652454",
    "locator": "L2"
  },
  "basis": {
    "id": "home-office-q1",
    "description": "One of four measured area units; synthetic owner-reviewed example",
    "numerator": 1,
    "denominator": 4,
    "period": {
      "from": "2026-01-01",
      "through": "2026-03-31"
    },
    "rounding": "floor",
    "evidence": {
      "path": "raw/area.csv",
      "sha": "sha256:b6303be8397f238136d4d6c925a41b20f5ffe70c0e737aeb3fb006876dc635de",
      "locator": "L2"
    }
  }
}
```

ハッシュは、次の架空のCSVファイルの内容に対応します。末尾の改行も含めてください。
`L2` はファイルの2行目を指します。両ファイルを `raw/` に保存します。

`raw/rent.csv`:

```csv
period_from,period_through,description,gross_amount,currency
2026-01-01,2026-01-31,January rent,10001,JPY
```

`raw/area.csv`:

```csv
id,effective_from,effective_through,business_area_units,total_area_units,rounding
home-office-q1,2026-01-01,2026-03-31,1,4,floor
```

```bash
iris allocation --schema
iris allocation --input raw/allocation-jan.json
```

結果は全額 `10001`、事業分 `2500`、家事分 `7501` 円です。金額と最小単位の値は
精度を保つ文字列で出力します。`evidenceVerification: unchecked` は証拠ファイルを
読み取っていないことを表します。元資料は別途確認し、入力、計算バージョン、
入力ハッシュ、結果を帳簿のノートに残してください。`inputSha` は解析した入力を
決まった項目順でハッシュ化した値なので、JSONの整形では変わりません。

日付は開始日・終了日とも含みます。費用の対象期間全体が、一つの根拠の有効期間に
収まる必要があります。途中で割合が変わる場合は、先に元の費用を明示的に分けます。
精度、分子・分母、丸め方は省略できません。事業分の最小単位未満を `floor` は切り捨て、
`half_up` は四捨五入、`ceil` は切り上げます。家事分には全額から事業分を引いた残りを
割り当てます。両方を別々に丸めたり、按分済みの金額にもう一度割合を掛けたりしないで
ください。分母は1〜1,000,000,000、分子は0〜分母です。割合や丸め方の既定値はありません。

同じ所有者が事業用・個人用の管理帳簿を分ける例です。支払った個人帳簿には、
次のように全額を記録します。勘定科目は実際の帳簿に合わせて選んでください。

```yaml
schema_version: 1
date: 2026-01-10
status: posted
allocation_ref: notes/allocation-january.md
counterpart_book: allocation-business
counterpart_journal: journals/2026-01/2026-01-10-rent.md
lines:
  - {account: Expenses:Rent, debit: 7501}
  - {account: Assets:BusinessClearing, debit: 2500}
  - {account: Assets:Bank, credit: 10001}
attachments:
  - {path: raw/rent.csv, type: receipt, locator: L2}
  - {path: raw/bank.csv, locator: L3}
  - {path: raw/area.csv, locator: L2}
```

事業帳簿には、対応する費用と精算用の負債を記録します。

```yaml
schema_version: 1
date: 2026-01-10
status: posted
allocation_ref: notes/allocation-january.md
counterpart_book: allocation-personal
counterpart_journal: journals/2026-01/2026-01-10-rent.md
lines:
  - {account: Expenses:Rent, debit: 2500}
  - {account: Liabilities:PersonalClearing, credit: 2500}
attachments:
  - {path: raw/rent.csv, type: receipt, locator: L2}
  - {path: raw/area.csv, locator: L2}
```

例の対応先帳簿の ID は、実際の `book_id` に置き換えてください。
`counterpart_*` と `allocation_ref` は参照情報です。他の帳簿への書き込みや記帳を
自動で行う機能はありません。支払った銀行口座からの出金は**10,001円全額**です。
後日、事業口座から2,500円を精算したら、事業帳簿では精算用の負債を借方、銀行を貸方に
記録します。個人帳簿では銀行を借方、精算用の債権を貸方に記録します。この例の精算では
収益や費用は増えません。別の5,000円の所有者資金移動は、両帳簿の資本科目で記録します。
科目を明示して対応付けてください。この管理上の精算から、法的な債権債務、親族間の
取引の税務、法人の会計処理が決まるわけではありません。

期首の個人・事業口座残高を100,000円・20,000円とした実行可能な例では、精算と
所有者資金移動の後は97,499円・12,500円になり、精算残高は両方ともゼロです。
合算費用は10,001円、合算収益はゼロです。費用の二重計上と精算の収益計上が重なると、
純利益だけは合う場合があります。収益・費用の合計も別々に確認し、各帳簿の
`iris reconcile` で銀行残高や精算残高を元資料と照合してください。

`charge_kind: depreciation` には、計算済みの減価償却費の**按分前の金額**を指定します。
取得時の支払額、元の取得価額、償却方法、償却後の帳簿価額は保持してください。
この計算は償却制度の選択、取得価額の按分、資産の所有帳簿の判断、兼用資産の自動記帳を
行いません。既存の資産タスクでも、この制限は変わりません。全額を取り消す場合は
元の按分結果を反対仕訳にし、一部返金には別途明示的な扱いを決めてください。
計算に成功しても、税務上の適用要件の充足や記帳・同期の権限を意味しません。

### 兼用資産の取得価額を保って費用を分ける

実行確認済みの手作業の例です。所有者の事業用の管理帳簿に資産全体を一つだけ記録し、
個人帳簿には家事分の費用を記録します。個人帳簿に同じ資産を重ねて計上しません。
償却方法、48か月の期間、残存価額1円、事業割合3/5は、この例の明示的な仮定です。
税務上の適用要件、法定耐用年数、償却方法の可否、法人の処理を判断するものではありません。

事業口座からの支払額は**240,049円全額**です。元の購入資料を参照し、
`Assets:Equipment` の借方240,049円、`Assets:Bank` の貸方240,049円で記録します。
元の取得価額を保持し、事業分の金額に置き換えないでください。資産の例は次のとおりです。

```yaml
schema_version: 1
name: Shared equipment
category: equipment
acquisition_date: 2026-05-01
acquisition_cost: 240049
salvage_value: 1
useful_life_months: 48
method: straight_line
asset_account: Assets:Equipment
depreciation_expense_account: Expenses:Depreciation
accumulated_depreciation_account: Assets:AccumulatedDepreciation
acquisition_journal: '[[2026-05-01-equipment]]'
```

共通エンジンの按分前の償却額を確認し、一つの記帳頻度を選びます。

```bash
iris asset schedule --year 2026
iris export assets --year 2026 --out raw/assets-2026.csv
iris asset depreciate --year 2026
```

5〜12月の8か月分は、月5,001円、償却額合計40,008円、期末帳簿価額200,041円です。
`depreciate` が作るのは下書きです。帳簿の権限に従って確認してから記帳します。
償却費を借方、減価償却累計額を貸方にした全額の仕訳は、一度だけ残してください。
再実行しても既存の提案は上書きしません。月次・年次の混在は拒否します。
締め済みと分かっている年度、別の書き込み処理が動いている帳簿、帳簿と異なる年度への
提案作成も拒否します。締め情報が手元にない場合、現在のクラウドの状態は確認できません。

この例の `raw/gross-depreciation.csv` は、共通エンジンの値と資産ファイルのハッシュを
保存した短い計算資料です。仕入先や銀行が発行した原本ではありません。テストでは実際の
計算・CSV出力と照合します。`raw/use.csv` は仮定した利用割合の根拠です。
次の架空のファイルの内容が、入力のハッシュに対応します。

`raw/gross-depreciation.csv`:

```csv
period_from,period_through,gross_depreciation,closing_book_value,asset_sha
2026-05-01,2026-12-31,40008,200041,sha256:b0b0c527112dd0b042442edc23fb30bd0485969cc5fa97cf7ae7b5b62a4be4c9
```

`raw/use.csv`:

```csv
id,effective_from,effective_through,business_use_units,total_use_units,rounding
equipment-2026,2026-05-01,2026-12-31,3,5,floor
```

次の入力を `raw/allocation-depreciation.json` に保存し、按分額を計算します。

```json
{
  "schema_version": 1,
  "gross_amount": "40008",
  "currency": "JPY",
  "scale": 0,
  "charge_kind": "depreciation",
  "period": {
    "from": "2026-05-01",
    "through": "2026-12-31"
  },
  "source": {
    "path": "raw/gross-depreciation.csv",
    "sha": "sha256:bb3d3bea2f8047617501c95b6328d76f2c98a5c29e9c0d389c9bf8cf2716172f",
    "locator": "L2"
  },
  "basis": {
    "id": "equipment-2026",
    "description": "Three of five recorded use units; synthetic owner-reviewed annual charge",
    "numerator": 3,
    "denominator": 5,
    "period": {
      "from": "2026-05-01",
      "through": "2026-12-31"
    },
    "rounding": "floor",
    "evidence": {
      "path": "raw/use.csv",
      "sha": "sha256:69bf6934a2e83cf7712fb7fc2d5afd90aad2809232f99b52c3502a5a10729c3a",
      "locator": "L2"
    }
  }
}
```

```bash
iris allocation --input raw/allocation-depreciation.json
```

結果は事業分 `24004` 円、家事分 `16004` 円です。**年額に対して一度だけ丸めた値**です。
月5,001円に割合を掛けて毎月切り捨てると、事業分の年額は24,000円になります。
どの期間の金額を丸めるかを記録し、年次から月次へ暗黙に変えないでください。
対象期間の途中で割合が変わる場合は、先に対象額を明示的に分けます。

全額の償却仕訳を一度だけ残したうえで、事業帳簿に次の振替仕訳を作成します。
勘定科目と対応先の帳簿 ID は実際のものに置き換えてください。

```yaml
schema_version: 1
date: 2026-12-31
status: posted
tags: [private-use-reclassification]
allocation_ref: notes/equipment-allocation.md
source_journal: journals/2026-12/auto/dep-annual-equipment.md
counterpart_book: equipment-personal
counterpart_journal: journals/2026-12/2026-12-31-equipment-use.md
lines:
  - {account: Equity:OwnerDrawings, debit: 16004}
  - {account: Expenses:Depreciation, credit: 16004}
attachments:
  - {path: raw/gross-depreciation.csv, locator: L2}
  - {path: raw/use.csv, locator: L2}
```

個人の管理帳簿には、対応する家事分の費用と資本の仕訳を記録します。

```yaml
schema_version: 1
date: 2026-12-31
status: posted
allocation_ref: notes/equipment-allocation.md
counterpart_book: equipment-business
counterpart_journal: journals/2026-12/2026-12-31-private-use.md
lines:
  - {account: Expenses:EquipmentUse, debit: 16004}
  - {account: Equity:BusinessUseContribution, credit: 16004}
attachments:
  - {path: raw/gross-depreciation.csv, locator: L2}
  - {path: raw/use.csv, locator: L2}
```

上の二つは、確認用データの記帳後の形です。作業では下書きを作り、帳簿の方針に従って
確認してから記帳してください。参照項目は情報として保持するだけです。計算ツールは
仕訳を作成せず、どちらの帳簿にも書き込みません。この家事分の認識では銀行残高を動かさず、
減価償却累計額を再び貸方に計上しません。

確認済みの期末値は次のとおりです。

| 項目 | 事業帳簿 | 個人帳簿 | 合計 |
| --- | ---: | ---: | ---: |
| 銀行残高 | 259,951 | 100,000 | 359,951 |
| 費用 | 24,004 | 16,004 | 40,008 |
| 収益 | 0 | 0 | 0 |
| 純資産 | 459,992 | 100,000 | 559,992 |

事業帳簿の資産は、取得価額240,049円から減価償却累計額40,008円を引いた200,041円です。
元の取得価額、銀行、資産残高、各帳簿と合算後の収益・費用を確認してください。
購入額を再度費用にしたり、家事分の振替を重ねたりしても、構造の検証や銀行残高の照合だけは
通る場合があります。この例の全体テストでは、それらを検出します。入力・結果・参照を残し、
元帳を確認して `iris validate` と `iris reconcile` を実行してから、許可された同期を行って
ください。税務申告への対応付けと兼用資産の自動記帳は未対応です。

### 自宅事務所の按分基準を適用日から変更する

前の1月分家賃の例に、別の元資料を持つ4月分を追加します。
1月の `raw/area.csv`、計算入力、メモ、預金の残高確認、仕訳はそのまま残します。
従来の1/4の基準は3月31日で終了します。新たに測定した1/3の基準は4月1日から適用し、
別の資料パス、hash、開始日と終了日を記録します。両端の日付を適用期間に含めます。

```csv
basis_id,effective_from,effective_through,business_units,total_units,rounding
home-office-april,2026-04-01,2026-12-31,1,3,floor
```

```csv
period_from,period_through,supplier,gross_amount,currency
2026-04-01,2026-04-30,Synthetic landlord,10001,JPY
```

両方のBookに、基準を明示した計算入力 `raw/allocation-april.json` を保存します。

```json
{
  "schema_version": 1,
  "gross_amount": "10001",
  "currency": "JPY",
  "scale": 0,
  "charge_kind": "expense",
  "period": {
    "from": "2026-04-01",
    "through": "2026-04-30"
  },
  "source": {
    "path": "raw/rent-april.csv",
    "sha": "sha256:b84be0483163d0b181009ef285f5b55d851ff53da0d728b8ba6cc2c9265c2636",
    "locator": "L2"
  },
  "basis": {
    "id": "home-office-april",
    "description": "One of three newly measured area units; effective April 1 only",
    "numerator": 1,
    "denominator": 3,
    "period": {
      "from": "2026-04-01",
      "through": "2026-12-31"
    },
    "rounding": "floor",
    "evidence": {
      "path": "raw/area-april.csv",
      "sha": "sha256:04f1cbc2994f0866b4db28bd52707223dbfa8e6ec41d7e1132ce38a700594d64",
      "locator": "L2"
    }
  }
}
```

同じ読取専用の計算コマンドで、総額10,001円、事業3,333円、私用6,668円を求めます。
結果の `evidenceVerification` は `unchecked` です。参照資料のバイト列と記載内容は別途確認し、
結果と入力hashを `notes/allocation-april.md` に残してください。4月10日に個人用の口座から全額10,001円を支払います。

```bash
iris allocation --input raw/allocation-april.json
```

`personal/journals/2026-04/2026-04-10-rent.md`:

```yaml
schema_version: 1
date: 2026-04-10
status: posted
allocation_ref: notes/allocation-april.md
counterpart_book: allocation-business
counterpart_journal: journals/2026-04/2026-04-10-rent.md
lines:
  - {account: Expenses:Rent, debit: 6668}
  - {account: Assets:BusinessClearing, debit: 3333}
  - {account: Assets:Bank, credit: 10001}
attachments:
  - {path: raw/rent-april.csv, locator: L2}
  - {path: raw/area-april.csv, locator: L2}
  - {path: raw/bank-april.csv, locator: L2}
```

`business/journals/2026-04/2026-04-10-rent.md`:

```yaml
schema_version: 1
date: 2026-04-10
status: posted
allocation_ref: notes/allocation-april.md
counterpart_book: allocation-personal
counterpart_journal: journals/2026-04/2026-04-10-rent.md
lines:
  - {account: Expenses:Rent, debit: 3333}
  - {account: Liabilities:PersonalClearing, credit: 3333}
attachments:
  - {path: raw/rent-april.csv, locator: L2}
  - {path: raw/area-april.csv, locator: L2}
  - {path: raw/bank-april.csv, locator: L2}
```

4月20日の精算では、事業用Bookで `Liabilities:PersonalClearing` を借方3,333円、
`Assets:Bank` を貸方3,333円に記録します。個人用Bookは `Assets:Bank` を借方3,333円、
`Assets:BusinessClearing` を貸方3,333円に記録します。精算時に収入・費用は増えません。
1月の事業主振替5,000円は従来どおり純資産の勘定に残します。

| 4月30日時点。家賃は1月分と4月分のみ | 事業用 | 個人用 | 合計 |
| --- | ---: | ---: | ---: |
| 預金 | 9,167 | 90,831 | 99,998 |
| 家賃費用 | 5,833 | 14,169 | 20,002 |
| 収入 | 0 | 0 | 0 |
| 精算勘定残高 | 0 | 0 | 0 |

```bash
iris validate --json /path/to/business
iris reconcile /path/to/business
iris report pl --from 2026-01-01 --to 2026-04-30 /path/to/business
iris validate --json /path/to/personal
iris reconcile /path/to/personal
iris report pl --from 2026-01-01 --to 2026-04-30 /path/to/personal
```

計算コマンドは、4月の基準を1月に使う入力、失効した1月の基準を4月に使う入力を拒否します。
3月15日〜4月15日をまたぐ請求全体も、どちらの基準でも拒否します。最新の割合の自動選択や日割り計算は行いません。
期間ごとの請求額を資料で確認してから計算してください。この例は必要経費の割合、法的な費用負担、申告書への対応を判断するものではありません。
所得税上の資料要件は[国税庁 No.2210](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2210.htm)を参照してください
（令和8年4月1日現在の法令等。2026年10月24日確認）。取消時は元の丸め済み金額を使います。過去資料の訂正は、元の識別情報を残して別途確認します。

実行確認用の例には、1月の元ファイル、4月の資料、各Bookの残高確認8件を含めています。
元ファイルが変わっていないこと、新しい基準の資料、計算結果、全額の預金移動、各Bookの費用合計を確認します。
1月を1/3へ遡って書き換える誤りは、貸借と預金残高が一致していても、精算勘定と費用の確認で検出します。

## 同居人の立替金と返還予定の敷金を記録する

同居人がそれぞれ管理する個人用Bookで、立替と精算を記録する例です。
架空の同居人AriとKeiは親族ではなく、当初の合意により、それぞれ40,000円と20,000円の敷金返還請求権を持つと仮定します。
実際の権利、支払者、精算条件を先に確認してください。支払った人や同居関係だけでは、権利や税務上の扱いは決まりません。
返還額や控除額に争いがある場合は、未解決の請求を残し、最終的な損失の計上前に専門家へ確認します。
この例は手動の管理記録であり、packageが双方のBookへ自動記帳する機能ではありません。

両方のBookに当初の合意書 `raw/agreement.csv` を保存します。

```csv
date,deposit_total,ari_claim,kei_claim,currency
2026-05-01,60000,40000,20000,JPY
```

5月1日にAriが60,000円全額を支払います。Ariは自分の敷金40,000円と、Keiへの立替金20,000円を資産として残します。
Keiは敷金20,000円と、Ariへの未払金20,000円を記録します。
次の例は記帳後の形式です。各Bookの方針に従ってdraftを作成・確認し、権限のある範囲でpostしてください。
`allocation_ref` と相手Book・仕訳への参照は補足情報です。アクセス権や書込権限は付与しません。

`ari/journals/2026-05/2026-05-01-deposit.md`:

```yaml
schema_version: 1
date: 2026-05-01
status: posted
allocation_ref: notes/deposit-settlement.md
counterpart_book: household-kei
counterpart_journal: journals/2026-05/2026-05-01-deposit.md
lines:
  - {account: Assets:RefundableDeposit, debit: 40000}
  - {account: Assets:KeiReceivable, debit: 20000}
  - {account: Assets:Bank, credit: 60000}
attachments:
  - {path: raw/agreement.csv, locator: L2}
  - {path: raw/bank.csv, locator: L3}
```

`kei/journals/2026-05/2026-05-01-deposit.md`:

```yaml
schema_version: 1
date: 2026-05-01
status: posted
allocation_ref: notes/deposit-settlement.md
counterpart_book: household-ari
counterpart_journal: journals/2026-05/2026-05-01-deposit.md
lines:
  - {account: Assets:RefundableDeposit, debit: 20000}
  - {account: Liabilities:AriPayable, credit: 20000}
attachments:
  - {path: raw/agreement.csv, locator: L2}
  - {path: raw/bank.csv, locator: L3}
```

各自の口座明細を `raw/bank.csv` に保存します。支払時はAriの口座から全額が出金されます。
Keiの口座が動くのは立替金を精算した日と返還金を受け取った日です。

`ari/raw/bank.csv`:

```csv
date,description,outflow,inflow,balance
2026-01-01,Opening,0,0,200000
2026-05-01,Landlord deposit,60000,0,140000
2026-05-03,Kei reimbursement,0,20000,160000
2026-12-28,Landlord refund,0,54000,214000
2026-12-30,Kei refund payout,18000,0,196000
```

`kei/raw/bank.csv`:

```csv
date,description,outflow,inflow,balance
2026-01-01,Opening,0,0,100000
2026-05-01,No bank payment,0,0,100000
2026-05-03,Ari reimbursement,20000,0,80000
2026-12-28,Refund held by Ari,0,0,80000
2026-12-30,Ari refund payout,0,18000,98000
```

12月28日の精算書で、実際の控除額6,000円、各自の負担4,000円・2,000円、Ariへの返還額54,000円が確定します。
支払先と行位置を含む元の精算書を、両方のBookに保存します。

```csv
date,original_deposit,actual_deduction,bank_refund,ari_refund,kei_refund,currency
2026-12-28,60000,6000,54000,36000,18000,JPY
```

敷金の資産残高を解消し、実際の控除分だけを費用にします。
Ariは12月30日に送金するまで、Keiに返す18,000円を未払金として残します。

`ari/journals/2026-12/2026-12-28-refund.md`:

```yaml
schema_version: 1
date: 2026-12-28
status: posted
allocation_ref: notes/deposit-settlement.md
counterpart_book: household-kei
counterpart_journal: journals/2026-12/2026-12-28-refund.md
lines:
  - {account: Assets:Bank, debit: 54000}
  - {account: Expenses:MoveOut, debit: 4000}
  - {account: Assets:RefundableDeposit, credit: 40000}
  - {account: Liabilities:KeiPayable, credit: 18000}
attachments:
  - {path: raw/settlement.csv, locator: L2}
  - {path: raw/bank.csv, locator: L5}
```

`kei/journals/2026-12/2026-12-28-refund.md`:

```yaml
schema_version: 1
date: 2026-12-28
status: posted
allocation_ref: notes/deposit-settlement.md
counterpart_book: household-ari
counterpart_journal: journals/2026-12/2026-12-28-refund.md
lines:
  - {account: Assets:AriReceivable, debit: 18000}
  - {account: Expenses:MoveOut, debit: 2000}
  - {account: Assets:RefundableDeposit, credit: 20000}
attachments:
  - {path: raw/settlement.csv, locator: L2}
  - {path: raw/bank.csv, locator: L5}
```

次の開始残高と精算仕訳も、各Bookに明示して記録します。

| 日付・取引 | Ari | Kei |
| --- | --- | --- |
| 1月1日 開始残高 | 借 Bank 200,000 / 貸 Opening equity 200,000 | 借 Bank 100,000 / 貸 Opening equity 100,000 |
| 5月3日 立替精算 | 借 Bank 20,000 / 貸 KeiReceivable 20,000 | 借 AriPayable 20,000 / 貸 Bank 20,000 |
| 12月30日 返還金の送金 | 借 KeiPayable 18,000 / 貸 Bank 18,000 | 借 Bank 18,000 / 貸 AriReceivable 18,000 |

勘定科目は `Assets:Bank`、`Assets:RefundableDeposit`、`Assets:<Name>Receivable` を資産、
`Liabilities:<Name>Payable` を負債、`Equity:Opening` を純資産、`Expenses:MoveOut` を費用として定義します。
`<Name>` には相手の名前を使います。立替金の精算と返還金の受取・送金による収入は発生しません。
控除額の確定前は敷金の請求権が資産として残るため、支払時に全額を費用にすると残高が合わなくなります。

| 確認日 | Ariの預金 | Keiの預金 | 敷金資産の合計 | 双方の債権・債務 |
| --- | ---: | ---: | ---: | ---: |
| 5月2日 立替精算前 | 140,000 | 100,000 | 60,000 | 20,000 |
| 5月4日 立替精算後 | 160,000 | 80,000 | 60,000 | 0 |
| 12月29日 返還金送金前 | 214,000 | 80,000 | 0 | 18,000 |
| 12月31日 返還金送金後 | 196,000 | 98,000 | 0 | 0 |

預金、敷金の請求権、双方の債権・債務を、それぞれ日付付きの残高確認で照合します。
元資料のhashと行位置を保存してください。預金だけが一致しても、敷金の分類や収入・費用の計上が正しいとは限りません。
記録と残高確認をそろえたら、次の読取専用コマンドで確認します。

```bash
iris validate --json /path/to/ari
iris reconcile /path/to/ari
iris report pl --from 2026-01-01 --to 2026-12-31 /path/to/ari
iris validate --json /path/to/kei
iris reconcile /path/to/kei
iris report pl --from 2026-01-01 --to 2026-12-31 /path/to/kei
```

各Bookの収入は0円、費用は4,000円・2,000円、敷金と精算勘定の残高はすべて0円になります。
預金の合計は294,000円で、開始残高300,000円から実際の控除6,000円を差し引いた金額です。
2つのBookの合計は手動で管理上の確認に使います。新しい連結コマンドはありません。
実行確認用の例には、各Bookの5仕訳と元資料付きの残高確認10件を含めています。
敷金の費用化、返還金の収入計上、相手側の預金仕訳の欠落、精算前の債務解消、二重送金は、貸借が一致していても検出します。
実際の契約で権利が異なる場合は、その内容を記録してください。この仮定を単独契約者、事業、係争中の案件などへそのまま流用しないでください。
契約資料の確認には[国土交通省の賃貸住宅標準契約書と解説](https://www.mlit.go.jp/jutakukentiku/house/jutakukentiku_house_tk3_000023.html)も参照できます
（2026年10月24日確認）。このひな形によって、例に置いた双方の請求権や控除額の負担割合が決まるわけではありません。

## 勘定科目表 — `config/chart-of-accounts.yaml`

帳簿設定・勘定科目表・ルール・仕訳・資産の型付き読み込みでは、未解決のルート
`views` を拒否します。YAML のマージで追加された場合も同様です。会計ビューを選んで
解決してから読み込み、編集時は元の文書に他のビューを残してください。
仕訳の構造化 API による全体置換も、保存されたビューを保持できないため拒否します。
`views` を削除すると、他の会計上の解釈が失われます。

クラウドは、ビューを含む `config/book.yaml`・仕訳・資産の元文書を保存できます。
Overlay のコードは実行しません。帳簿のビューは最大16個で、既定のビューを1つ
指定します。すべてのビューで、型・貸借一致・勘定科目・参照先・締め済み期間を
確認します。帳簿ID、会計期間、通貨、単位の小数桁数、整合性に関する設定は共通です。
仕訳のステータスは共通部分に記録し、個別のビューでは変更できません。
同期・クローンでも、解決前の元文書を保持します。

Web の金額は、既定のビューの**未承認の参考値**です。記帳の承認は、確認した
共有の元記録に対するもので、ビュー別の計算結果を承認するものではありません。
名前付きビューの承認済みレポートは、別途保持・承認した標準計算の結果を使います。
[計算結果の保持と承認](cli-reference.md#iris-financial)を参照してください。年度締めには、
すべての宣言済みビューが現在の入力に対して承認済みで、元取引に未記帳がないことが必要です。
SQLite は各ビューを別々に保持し、通常の表には既定のビューを保存します。仕訳・資産に
ビューの差分がある間は、一括した再構築が必要になるため、
ビューの追加と既定の変更を拒否します。仕訳が参照するビューの宣言も削除できません。
勘定科目表・ルールの `views` は、クラウドではまだ受け付けません。

```yaml
schema_version: 1
accounts:
  - path: 資産:普通預金        # 階層・コロン区切り。これが識別子
    type: asset               # asset | liability | equity | income | expense
    code: "1010"              # 任意の外部コード
    aliases: [bank, 銀行, Assets:Bank]
  - path: 収益:売上
    type: income
    aliases: [sales]
  - path: 資産:事業主貸
    type: asset
    owner: true               # 事業主個人の資金 — 純資産画面の集計に含めない
  - path: 資本:元入金
    type: equity
    retained_earnings: true   # 任意 — `iris yearend` が純利益を折り込む科目
```

科目の通常残高側は `type` から導かれます。`aliases` により、別名や別言語で科目を
参照できます。仕訳で参照する前に、ここへ科目を追加してください。

`owner: true` は、事業主個人の引き出しと持ち込みの科目を表します。個人事業主なら
事業主貸と事業主借です。科目の種類はそのままなので、貸借対照表は青色申告決算書の
並びのまま出ます。ただしこれらは事業が持つもの・負うものではなく、事業主自身の
お金の出入りなので、[純資産](web-app.md#純資産)の集計には含めません。日本向けの
初期の勘定科目表にはこの指定が入っています。

`retained_earnings: true` は、[`iris yearend`](cli-reference.md#iris-yearend) が
その年度の純利益を折り込む資本科目を表します。個人事業主なら資本:元入金、法人なら
純資産:繰越利益剰余金です。付けられるのは 1 科目だけで、`type: equity` の科目に
限ります。どちらかに反する勘定科目表は、`iris validate` とクラウドが拒否します。
どの科目にも付いていなければ `iris yearend` は勘定科目表で唯一の資本科目を使うので、
資本科目が 1 つだけの初期の勘定科目表には入っていません。資本科目を 2 つ以上
置いたら、そのうち 1 つに付けてください。

## 資産ファイル — `assets/YYYY/*.md`

```yaml
---
schema_version: 1
name: "MacBook Pro 16"
category: equipment.computer       # 自由形式
acquisition_date: 2026-04-15
acquisition_cost: 480000
salvage_value: 1
useful_life_months: 48
method: straight_line              # straight_line | declining_balance | expensed
asset_account: "資産:工具器具備品"
depreciation_expense_account: "費用:減価償却費"
accumulated_depreciation_account: "資産:減価償却累計額"
acquisition_journal: "[[2026-04-15-apple-01]]"   # 任意の wikilink
schedule:                          # 任意。記録済みの償却表（下記参照）
  - period: 2027-03                # YYYY-MM。その償却額を計上する月
    amount: 250000
  - period: 2028-03
    amount: 187500
schedule_source:                   # オーバーレイのレシピが表を書いたときに付く根拠（下記参照）
  overlay: jp-declining-balance@2026.10.1
  recipe: jp-declining-balance.teiritsu
  bindings: 5
  primitives: {declining_table: 2, flat_table: 2}
  params: {full_year_confirmed: true, cost: 480000, life: 4, rate: 0.500, guarantee: 0.12499, revised: 1.000, start: 2027-03}
disposal:                          # 任意。処分まで無し
  date: 2029-05-10
  proceeds: 50000
  journal: "[[2029-05-10-apple-disposal-01]]"
---
```

JP 固有フィールド（用途区分、特例、償却資産税フラグ）は不透明に同伴し、JP
オーバーレイが読み取ります。

ここに記述した資産の購入は、`expensed` のものも含めて `asset_account` に
計上し、償却は `iris asset depreciate` に計上させてください。`expensed` の
資産では、取得月に取得価額の全額を 1 回で償却します。購入をそのまま経費の
科目にも計上すると、二重に計上されます。

`method: expensed` では、`useful_life_months` を省略するか `0` にします。
正の耐用月数はエラーになります。`schedule` も省略してください。取得月の全額償却は
iris が直接計算します。`straight_line` と `declining_balance` には、正の
`useful_life_months` が必要です。

### `schedule:` — 計算させるか、表を記録するか

定額法では `schedule` を省略でき、`useful_life_months` から iris が償却額を
計算します。即時費用化では `schedule` を省略する必要があり、耐用月数を使わずに
取得月に全額を償却します。それ以外 — 改定償却率に切り替わる日本の定率法、
定額法へ移行する米国 MACRS など — は償却表をファイルに記録し（`method:
declining_balance` には必須です）、iris はその値をそのまま使います。

各行は `period`（`YYYY-MM`）と `amount` の 2 つです。年 1 回計上する帳簿なら
年度ごとに 1 行、期末の月の日付で書きます。月次で計上する帳簿なら月ごとに
1 行です。どちらでも動きます。

資産ごとの上限は、償却表4,096行、`useful_life_months` 4,096か月です。
計算ツールは、必要な行数と日付の範囲をメモリ確保前に確認し、9999年を超える表を
拒否します。これは実装上の上限で、税務上の要件ではありません。ローカルの償却表表示・
償却仕訳作成・資産CSV出力では、1回の処理を資産4,096ファイル、元ファイル合計64 MiB、償却表合計100,000行まで
に制限します。資産ファイルは通常のファイルに限り、上限は256 KiBです。不正な表や上限を
超えた入力はエラーになります。金額をゼロとして表示したり、途中までのCSVを返したりはしません。
新しく実行したレシピには計算部品のバージョン2を記録します。過去のバージョン1は、
同じ計算量の上限内で当時の計算を再現します。バージョンが不明な記録を最新版で代用しません。

MCPの表計算ツールには最小単位の整数額を渡します。大きな金額は10進整数の文字列で指定し、
結果も `amountExact`・`totalExact` または生成されたYAMLで読み取ってください。
ツールの `scale` は書き込み先の帳簿に合わせます。省略時は0です。たとえば最小単位で
12,345、`scale: 2` なら、YAMLは `amount: 123.45` となり、読み戻しても12,345単位です。
結果には使用した `scale` も含みます。

表は AI アシスタントが組み立てます。帳簿の地域オーバーレイにその方式の
**レシピ**があれば — 日本の定率法は `jp-declining-balance.teiritsu` — 公表されている率を入力として
それを実行し、レシピが表を組み立ててファイルに根拠付きで書き込みます
（`iris overlay recipe`、または対応する MCP ツール）。レシピのない方式は、
計算ツールを組み合わせて表を作ります（[CLI と AI](cli-and-llm.md) 参照）。
書き込んだあとは、帳簿・レポート・CSV 出力のすべてがこの表を使います。

iris は表の形を検査します。行が昇順で重複がないこと、マイナスがないこと、
取得月より前・耐用年数より後・除却後の行がないこと、そして合計が
`acquisition_cost` − `salvage_value` と一致すること（除却した資産では、それを
超えないこと。[資産を除却する](#資産を除却する)参照）です。行だけを見ても切替の年が
正しいかは検査できません — それは `schedule_source` の役目です（次節）。手で
組み立てた表では、使った償却率をファイルに残しておいてください（未知のキーは
そのまま保持されます）。税理士が公表されている率と突き合わせられます。

### `schedule_source:` — 表の出どころを記録し、再計算で照合する

レシピが表を書いたときは、その根拠も一緒に記録されます。オーバーレイのバージョン
（`jp-declining-balance@2026.10.1`。帳簿独自の `config/overlays/` のレシピなら `book:<ハッシュ>`）、
レシピ、実行時のエンジンのバージョン、そして渡した入力 — 公表表の率、耐用年数、
最初の行の月です。`iris validate` はその入力でレシピを**再計算**し、記録された行と
違えばファイルを受け付けません。合計さえ合えば通ってしまう「1 年遅れの切替」は
もう通りません。入力はファイルに残るので、税理士が公表表と突き合わせられます。
`schedule_source` のない表は形式のみを検査します。再計算には、帳簿の現在の固定バージョンとは
異なっていても、帳簿内に保持した正確な版を使います。同梱版やダウンロードキャッシュで
不足する出典を代用しません。定義の不足、帳簿独自の定義のハッシュ変更、必要な
エンジン機能の不足は、明示的に診断します。

### 資産を除却する

`disposal:` に除却日と売却代金（`proceeds`）を書きます。減価償却は除却月まで
（除却月を含む）、それまでと同じ月額で続きます。除却は償却を打ち切るだけで、
前倒しにはしません。その時点で残っている取得価額が**除却時の帳簿価額**です。
`iris asset schedule` では `DISPOSAL_NBV`、`iris export assets` では
`disposal_nbv` として、実際に償却した額 `accumulated` と並べて表示します。
除却の仕訳では、資産の取得価額とこの償却累計額を消し、売却代金を計上し、
売却代金と除却時の帳簿価額の差額を売却益または売却損・除却損として計上します。

計算で求める定額法の償却表は、除却月で自動的に止まります。記録した償却表は
iris が書き換えることはありません。除却月より後の行を削除し、除却した年度の行は
保有していた期間分の償却額（日本では月割）に書き換えてください。こうすると表の
合計は `acquisition_cost` − `salvage_value` を下回ってかまいませんが、上回っては
いけません。レシピが書いた表なら、`iris validate` は除却月より前の行を引き続き
再計算で照合します。除却した年度の行はあなたが決める行です。

日本の一括償却資産（`toku_rei: ikkatsu_3yr`）とその除却には未対応です。
現在の `jp-small-asset-deduction` パッケージは、この区分を
`asset.ikkatsu-unsupported` エラーで拒否します。通常の36か月の定額償却では、
一括償却資産の年間償却額を表せません。証憑を残し、未解決の処理を
`notes/open-questions.md` に記録して確認を受けてください。`disposal:` の省略で
対応できるようにはなりません。

## 申告記録 — `filings/<recipe>.md`

申告に使った集計値を、記録済みのファイルとして持ちます。地域オーバーレイの集計
レシピ（日本では消費税申告の `jp-tax-filing.shouhizei-general` と `jp-tax-filing.shouhizei-simplified`）
が記帳済みの仕訳を集計し、申告書に必要な形に組み合わせます。`iris overlay recipe
… --apply --out filings/jp-tax-filing.shouhizei-general.md` で、償却表と同じ根拠付きで記録
されます。

```yaml
---
schema_version: 1
filing: jp-tax-filing.shouhizei-general
period: {from: 2026-01-01, to: 2026-12-31}
source:
  overlay: jp-tax-filing@2026.10.1
  recipe: jp-tax-filing.shouhizei-general
  bindings: 5
  params: {from: 2026-01-01, to: 2026-12-31, scope_confirmed: true}
figures:
  sales_10: 11000000
  sales_tax_10: 1000000
  deductible_tax: 620000
  net_tax: 380000
  payable: 380000
  # …
---
（同じ数値の読みやすい表）
```

`iris validate` は仕訳に対してレシピを再計算し、数値が仕訳から導けなくなった
申告記録を受け付けません。申告後に訂正を記帳すると、レシピを再実行する（または
訂正を戻す）までエラーになります。AI は `figures` から様式に転記します。明細を
手で足し直すことはありません。申告記録は `compiled/` と違って同期され、帳簿と
一緒に封印されます。

## 帳簿独自のオーバーレイ層 — `config/overlays/`（任意）

公開された機能パッケージを `book.yaml` の `overlay:` または `overlays:` で選択します。
帳簿はその上に独自の層を追加できます。

```text
config/overlays/
├── overlay.yaml        # id: book / extends: jp-tax-classification@2026.10.1
├── fields.yaml         # 任意のフィールド型・候補値
├── functions.yaml      # 任意: 共有する式
├── rules/*.yaml        # 追加のチェック（公開ルールと同じ id なら上書き）
├── recipes/*.yaml      # 追加の計算
├── derive/*.yaml       # 追加の派生値の提案
└── tests/*.yaml        # ゴールデンケース — `iris overlay test` が実行
```

複数の公開バージョンを使う場合は、独自の層の `extends` にそのすべてをリストで
指定します。独自の式は地域共通パッケージの CEL 関数を使えます。他の公開パッケージの
関数は、その内部で使います。既存のルール・派生・レシピを上書きした場合、
`overlay_settings` のパッケージ ID は引き継ぎます。独自の層で新しく作った項目は、
予約された `book` キーに設定します。公開パッケージの組み合わせや独自の層の
manifest の ID を変えても、このキーは変わりません。

```yaml
overlay_settings:
  book:
    rules:
      local.memo:
        params: {memo: invoice}  # config/overlays/rules/ に追加したルールの入力
```

ルール・派生には宣言した項目 ID を使います。新しい独自レシピの既定値には、
パッケージ名を除いたレシピ名を使います。公開フィールド定義は独自の層で置き換えられません。
独自のルールに必須入力を追加する場合は、先にその定義を同期し、次に設定値を同期します。
公開バージョンを更新するときは、ローカルの更新プレビューで選択全体、設定と対応する
`extends` を確認してから適用します。元の独自定義と親バージョンは保持します。
クラウドは上限内の出典を保存し、コンパイル・評価は行いません。中断によって
信頼済みの層と親の選択が食い違った場合は、ローカルの実行を止めます。保存済みの
出典を確認し、改めて更新内容を確認してから続けてください。

ルールとレシピは帳簿のレコードに対する [CEL](https://cel.dev) の式で書きます。
ファイルにもネットワークにも触れず、計算量に上限のある言語なので、AI に書かせて
も安全です。`iris validate` は明示的に選択された公開パッケージと並べて信頼済みの層を
適用します。クラウドは独自定義を実行せず、基本の整合性・権限チェックを行います。
これらのファイルを変更できるのは帳簿の
オーナーだけです。このマシンが初めてこの層のあるバージョンに出会うと、ファイルを
表示して一度だけ確認します（`iris overlay trust` が回答を記録します）。それまでは
公開オーバーレイのみを適用します。`iris overlay list` と公開レシピの MCP ツールは
引き続き使えます。CLI と MCP の `describe_overlay.issues` は
`overlay.book-layer-untrusted` を報告し、独自の項目の設定は信頼後に検証します。
この層のレシピは出どころとして
`book:<ハッシュ>` を記録するので、レビュアーは帳簿固有のレシピから生まれた償却表だと
分かります。公開オーバーレイはオープンソース（Apache-2.0）で、公開リポジトリ
[`irisbooks/overlays`](https://github.com/irisbooks/overlays) にあります。ひとつの
帳簿を超えて役立つ層は、そこにプルリクエストとして提案できます。

信頼はマシンごとの記録であり、clone には含まれません。過去の独自定義は
`config/overlay-packages/local/HASH/` で確認し、
`iris overlay trust --source book:HASH [path]` で明示的に信頼できます。
保存済みの正確な内容と帳簿内の元の親を確認し、パッケージの選択は変更しません。
現在の層を信頼しても、別の過去のハッシュへの信頼は付与されません。
過去の出典が不足・改変していれば、再計算には使えません。

## `config/rules.yaml`（任意）

AI が分類時に参照しうる、人が整備したヒント。強制されることはありません。

```yaml
schema_version: 1
categorization:
  - when:
      payee_matches: "Amazon"
      amount_max: 50000
    propose:
      account: "費用:消耗品費"
      confidence: 0.85
```

## パースキャッシュ — `notes/raw/<source>.md`

AI が `raw/` 配下の資料を解析すると、出所パスをミラーした恒久的・正規化済みの
ビューをここに書きます。各行はステータス（`journaled` / `ignored` / `deferred`）を
持つため、同じ明細を開き直しても作業をやり直しません。

```markdown
---
source: raw/2026-04-sbi.csv
source_sha: <iris hash>
parsed_at: 2026-05-11
counts: { total: 47, journaled: 42, ignored: 3, deferred: 2 }
---

## Rows
| id | date       | description | amount | status    | target / reason                          |
|----|------------|-------------|--------|-----------|------------------------------------------|
| 1  | 2026-04-01 | Amazon JP   |  -5000 | journaled | journals/2026-04/2026-04-01-amazon-01.md |
```

パースキャッシュを再利用する前に、`source_sha` と現在の原本の `iris hash` を
比較します。原本が変わった場合は、変更された行と既存の仕訳への参照を確認し、
完了済みの行の状態を保ってから追加の仕訳を作成します。

## 同期されるもの・されないもの

クラウド同期では、`iris sync` が**同期対象**のファイルをクラウドにミラーします。

- **同期される:** `journals/`、`assets/`、`filings/`、`notes/`（パースキャッシュ
  含む）、`AGENTS.md`（共有の作業ガイド）、`raw/`（バイト列そのまま）、`config/book.yaml`、
  `config/chart-of-accounts.yaml`、`config/rules.yaml`、
  `config/balance-assertions.yaml`、`config/overlays/`、`config/overlay-packages/`。
- **同期されない:** `.iris/`（実行時状態）、`README.md` / `CLAUDE.md`（ローカルの案内）、`compiled/`（再生成可能）。

関連: [基本コンセプト](concepts.md) ·
[CLI コマンドリファレンス](cli-reference.md)。

### 独立した年度帳簿と取得原価の期首情報

`iris yearend` は翌年度の `config/book.yaml` に完全な期首保有情報を書きます。
各年度の帳簿は単独で評価でき、過年度の帳簿とのリンクは不要です。
過去の期間も表示する場合に、その年度の帳簿を選びます。

```yaml
opening_inventory:
  - account: Assets:Fund
    unit: FUND
    method: fifo
    quantity: 100
    carrying_value_minor: 1200000
    acquisition_cost_minor: 1000000
    lots:
      - id: original-purchase
        date: 2025-11-01
        quantity: 100
        cost_minor: 1000000
```

数量は単位の scale に従う整数、金額は帳簿通貨の最小単位の整数です。
簿価と取得原価は別々に保持します。簿価の情報により、同じ科目にある帳簿通貨の現金と
単位付き保有残高も区別します。FIFO・個別法では元のロットと取得日を保持し、移動平均では
ロットなしの数量・原価を保持します。取得原価の null は不明を表します。
期首仕訳は引き続き金額と数量の残高を表し、この帳簿自身の期首保有情報と一致する
必要があります。評価替え後の期首金額から取得原価を推測しないでください。

明示したロット ID はそのまま保持します。購入時のロット ID が省略されている場合、
分析処理は会計年度・仕訳パス・元の行番号から、その帳簿の保有情報内で使う ID を生成します。
クラウドへのリンクで帳簿 ID が変わっても、ロット ID は変わりません。

公開された取得費ポリシーを使う場合、期首情報に `allocation_cost_minor` と
`allocation_policy` を保持できます。前者は別途計算した取得費、後者は正確な
部品の版とポリシーの識別子です。元の取得原価や帳簿価額を置き換えるものでは
ありません。単価の端数処理を伴う場合は、この情報を `iris yearend` で引き継ぎ、
時価から再構成しないでください。これらの項目には bindings 6 対応エンジンが
必要です。この契約を使う地域別の投資部品は開発候補であり、承認済み財務ビューの
計算や税務申告書の提出は追加しません。
