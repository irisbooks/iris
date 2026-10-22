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
  `YYYY-MM-DD-<取引先>-NN.md`、Web アプリやリモートコネクタで作られた仕訳は
  サーバーが `YYYY-MM-DD-<取引先>-jNNN.md` と名付けます(取引先は元の表記のまま)。
  どちらも正しい形で、連番が別なので衝突しません。
- `.iris/` はローカルの帳簿 ID と同期状態を保持します。マシン固有で同期されません。

## `config/book.yaml`

```yaml
schema_version: 1
book_id: lb_...                 # init 時はローカル ID。クラウド連携時に置き換わる
name: "Acme Design"
region: JP                      # ISO 3166-1。税・ロケールのルールを選択
overlay: jp@2026.09.1           # 地域ルールのバージョン。init 時に固定（下記参照）
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

`overlay` は**地域オーバーレイ**、つまり `iris validate` とサーバーがこの帳簿に
適用する、国ごとのチェックと計算のバージョン付きセットを指します（日本なら
`toku_rei` の特例区分の制約、少額減価償却の年 300 万円上限、消費税の税区分・
税率ルール）。オーバーレイが最初に用意された地域は日本です。オーバーレイの無い
地域の帳簿には `overlay:` の行がなく、普遍的なチェックだけが行われます。その地域の
オーバーレイが公開されたら、`iris overlay upgrade` で固定できます。固定する
バージョンは `iris init` の時点でお使いの `iris` に組み込まれているものが一度だけ
書き込まれるため、帳簿の検証ルールが黙って変わることはありません。お使いの `iris` には、それが
作られる前に公開されたすべてのバージョンが含まれているため、そのどれを固定した
帳簿もオフラインで使えます。新しいバージョンは `iris` 本体とは別に公開されます。
`iris overlay upgrade` は最新版を確認したうえで固定を移し、`iris overlay fetch` は
帳簿がすでに固定している、お使いの `iris` より新しいバージョン（別のパソコンで
作った帳簿など）をダウンロードします。どちらも先に署名を検証します。従来の `overlay:` で固定された
バージョンが組み込まれておらずダウンロードもされていない場合、`iris validate` は
警告を出し、代わりに使ったバージョンを表示します。クラウドは常に帳簿が固定した
バージョンで検査し、公開されていないバージョンへの固定は受け付けません。

## 複数の公開オーバーレイを固定する

`overlays` には、使いたいオーバーレイの**固定バージョンを複数指定**できます。
`overlay` と同時には書けません。地域共通のパッケージと専門分野のパッケージを
組み合わせる場合は、次のように書きます。

```yaml
# 設定例です。jp-rsu は、公開されてから指定できます。
overlays:
  - jp@2026.09.1
  - jp-rsu@2026.10.1
```

すべてのバージョンが、このマシンに組み込まれているか、ダウンロード済みである
必要があります。不足分は `iris overlay fetch` で取得します。複数指定の場合、
1 つでも見つからなければ検証はエラーになり、別のバージョンには置き換わりません。
同じパッケージの重複、地域・依存関係の不一致、公開ルールの ID やフィールド定義の
衝突もエラーです。列挙する順序で優先順位は変わりません。各パッケージの CEL 関数は
その内部で使い、レシピの出典には、そのレシピを持つパッケージのバージョンを記録します。

パッケージの `overlay.yaml` には `region: JP` や、対応する依存バージョン
`requires_overlays: {jp: [2026.09.1]}` を宣言できます。新しい科目選択や
パラメーターの仕組みを使う場合は `requires_bindings: 2` を指定します。
`iris overlay upgrade --dry-run` で、更新後の組み合わせ、テスト、帳簿独自の層、
設定値を確認できます。`--to jp-rsu@<version>` ならそのパッケージだけを更新し、
`--to` を省略すると、固定している各パッケージの最新版をまとめて確認します。

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

`iris autocomplete journals/2026-10/2026-10-21-sale.md` を実行すると、
保有科目の貸方5万円と、利益の貸方2万円をプレビューします。
`--apply` とプレビューの `--revision` で適用できます。
`default` オーバーレイは自動で使われるため、仕訳の属性を追加する必要はありません。
手数料があれば、費用の行に明記してください。金額だけの通常の仕訳も、
貸借を合わせる1行を `debit: null` または `credit: null` にできます。
補完後も下書きのままで、検証は記録された金額を確認します。
操作は [iris autocomplete](cli-reference.md#iris-autocomplete) を参照してください。

## 勘定科目表 — `config/chart-of-accounts.yaml`

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
  overlay: jp@2026.09.1
  recipe: jp.teiritsu
  bindings: 1
  params: {cost: 480000, life: 4, rate: 0.500, guarantee: 0.12499, revised: 1.000, start: 2027-03}
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

### `schedule:` — 計算させるか、表を記録するか

定額法と即時費用化なら `schedule` は省略できます。`useful_life_months` から
iris が償却額を計算します（即時費用化の資産は、取得月に全額）。それ以外 — 改定償却率に切り替わる日本の定率法、
定額法へ移行する米国 MACRS など — は償却表をファイルに記録し（`method:
declining_balance` には必須です）、iris はその値をそのまま使います。

各行は `period`（`YYYY-MM`）と `amount` の 2 つです。年 1 回計上する帳簿なら
年度ごとに 1 行、期末の月の日付で書きます。月次で計上する帳簿なら月ごとに
1 行です。どちらでも動きます。

表は AI アシスタントが組み立てます。帳簿の地域オーバーレイにその方式の
**レシピ**があれば — 日本の定率法は `jp.teiritsu` — 公表されている率を入力として
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
（`jp@2026.09.1`。帳簿独自の `config/overlays/` のレシピなら `book:<ハッシュ>`）、
レシピ、実行時のエンジンのバージョン、そして渡した入力 — 公表表の率、耐用年数、
最初の行の月です。`iris validate` はその入力でレシピを**再計算**し、記録された行と
違えばファイルを受け付けません。合計さえ合えば通ってしまう「1 年遅れの切替」は
もう通りません。入力はファイルに残るので、税理士が公表表と突き合わせられます。
`schedule_source` のない表は形式のみを検査します。再計算には、帳簿の現在の固定バージョンとは
異なっていても、記録された版を使います。`iris` に組み込まれた版または署名検証済みの
ダウンロードキャッシュから読み込みます。その版が見つからない場合、帳簿独自のルールの
ハッシュが変わった場合、必要なエンジン機能が使えない場合は、警告を出して形式のみを
検査します。

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

例外は日本の一括償却資産（`toku_rei: ikkatsu_3yr`）です。物がなくなっても、
3 分の 1 ずつの損金（必要経費）算入は続きます。この資産には `disposal:` を書かず、
除却したことはファイル本文に書き残してください。`disposal:` を書くと、iris は
除却月で償却表を止めてしまいます。

## 申告記録 — `filings/<recipe>.md`

申告に使った集計値を、記録済みのファイルとして持ちます。地域オーバーレイの集計
レシピ（日本では消費税申告の `jp.shouhizei-general` と `jp.shouhizei-simplified`）
が記帳済みの仕訳を集計し、申告書に必要な形に組み合わせます。`iris overlay recipe
… --write filings/jp.shouhizei-general.md` で、償却表と同じ根拠付きで記録
されます。

```yaml
---
schema_version: 1
filing: jp.shouhizei-general
period: {from: 2026-01-01, to: 2026-12-31}
source:
  overlay: jp@2026.09.1
  recipe: jp.shouhizei-general
  bindings: 1
  params: {from: 2026-01-01, to: 2026-12-31, non_invoice_pct: 80}
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

地域オーバーレイ — 帳簿の地域に付いてくるルール・レシピ・派生 — は iris と一緒に
公開され、`book.yaml` の `overlay:` で固定されます。帳簿はその上に独自の層を
追加できます。

```text
config/overlays/
├── overlay.yaml        # id: book / extends: jp@2026.09.1
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
公開バージョンを更新するときは、保存済みの層が新バージョンでコンパイルできなくても、
公開パッケージの設定が正しければ、新しい帳簿設定を同期できます。続いて新バージョンに
合わせて定義を修正し、`extends` を同期します。複数のファイルを修正する場合、
各定義は公開パッケージと独自の関数を使ってコンパイルできる必要があります。
他の定義の修正待ちでも、ファイル数・サイズの上限は適用されます。
仕訳などの書き込みは、保存済みの層と
すべての設定値がそろうまでエラーになります。

ルールとレシピは帳簿のレコードに対する [CEL](https://cel.dev) の式で書きます。
ファイルにもネットワークにも触れず、計算量に上限のある言語なので、AI に書かせて
も安全です。`iris validate` は公開オーバーレイと並べてこの層を適用し、クラウドは
すべてのメンバーの書き込みに適用します。これらのファイルを変更できるのは帳簿の
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
  `config/chart-of-accounts.yaml`、`config/rules.yaml`、`config/overlays/`。
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
