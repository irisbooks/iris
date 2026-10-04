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
│   └── <fy>/<recipe>.md           # 申告用の集計値の記録（オーバーレイのレシピが書く）
├── notes/
│   ├── workflow.md  decisions.md  open-questions.md  todos.md
│   └── raw/<raw/ のミラー>.md      # パースキャッシュ
├── compiled/                      # AI 生成レポート（再生成可能）
├── README.md  LLM-GUIDE.md  CLAUDE.md   # 人間・AI 向けガイド
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
book_id: lb_...                 # init 時に発行。不変
name: "Acme Design"
region: JP                      # ISO 3166-1。税・ロケールのルールを選択
overlay: jp@2026.09.1           # 地域ルールのバージョン。init 時に固定（下記参照）
language: ja                    # ISO 639-1。勘定科目の言語はこれに従う
currency: JPY                   # ISO 4217
scale: 0                        # 補助単位の指数 — 不変（JPY 0, USD 2, BHD 3）
entity_kind: individual         # individual | company | partnership | trust
fiscal_start_month: 4           # 1〜12
fiscal_year: 2026               # この帳簿が扱う会計年度（この例では 2026-04-01〜2027-03-31）
created_at: "2026-06-20T12:34:56Z"

# 任意:
tax_id: "..."                   # 地域ごとに不透明
opening_balance_equity_account: "資本:元入金"   # `iris yearend` が純利益を折り込む科目
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
作った帳簿など）をダウンロードします。どちらも先に署名を検証します。固定された
バージョンが組み込まれておらずダウンロードもされていない場合、`iris validate` は
警告を出し、代わりに使ったバージョンを表示します。クラウドは常に帳簿が固定した
バージョンで検査し、公開されていないバージョンへの固定は受け付けません。

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
| `date` | はい | `YYYY-MM-DD`。ファイル名の接頭辞と一致 |
| `payee` | はい | 母語表記可。ファイル名のスラッグはこれから導出 |
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
```

科目の通常残高側は `type` から導かれます。`aliases` により、別名や別言語で科目を
参照できます。仕訳で参照する前に、ここへ科目を追加してください。

`owner: true` は、事業主個人の引き出しと持ち込みの科目を表します。個人事業主なら
事業主貸と事業主借です。科目の種類はそのままなので、貸借対照表は青色申告決算書の
並びのまま出ます。ただしこれらは事業が持つもの・負うものではなく、事業主自身の
お金の出入りなので、[純資産](web-app.md#純資産)の集計には含めません。日本向けの
初期の勘定科目表にはこの指定が入っています。

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
`schedule_source` のない表は形式のみを検査します。お使いの `iris` に組み込まれた
オーバーレイのバージョンが記録と違う場合は、警告を出して形式のみを検査します。

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
├── functions.yaml      # 任意: 共有する式
├── rules/*.yaml        # 追加のチェック（公開ルールと同じ id なら上書き）
├── recipes/*.yaml      # 追加の計算
├── derive/*.yaml       # 追加の派生値の提案
└── tests/*.yaml        # ゴールデンケース — `iris overlay test` が実行
```

ルールとレシピは帳簿のレコードに対する [CEL](https://cel.dev) の式で書きます。
ファイルにもネットワークにも触れず、計算量に上限のある言語なので、AI に書かせて
も安全です。`iris validate` は公開オーバーレイと並べてこの層を適用し、クラウドは
すべてのメンバーの書き込みに適用します。これらのファイルを変更できるのは帳簿の
オーナーだけです。このマシンが初めてこの層のあるバージョンに出会うと、ファイルを
表示して一度だけ確認します（`iris overlay trust` が回答を記録します）。それまでは
公開オーバーレイのみを適用します。この層のレシピは出どころとして
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

## 同期されるもの・されないもの

クラウド同期では、`iris sync` が**同期対象**のファイルをクラウドにミラーします。

- **同期される:** `journals/`、`assets/`、`filings/`、`notes/`（パースキャッシュ
  含む）、`raw/`（バイト列そのまま）、`config/book.yaml`、
  `config/chart-of-accounts.yaml`、`config/rules.yaml`、`config/overlays/`。
- **同期されない:** `.iris/`（実行時状態）、`README.md` / `LLM-GUIDE.md` /
  `CLAUDE.md`（ガイド）、`compiled/`（再生成可能）。

関連: [基本コンセプト](concepts.md) ·
[CLI コマンドリファレンス](cli-reference.md)。
