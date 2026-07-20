# 帳簿ファイル形式リファレンス

帳簿はプレーンな Markdown と YAML のフォルダです。このページはその中身の
リファレンスです。これらを手書きする場面はほとんどありません（AI が書き、
`iris validate` がチェックします）が、形を理解しておくと役立ちます。

> このページを正しく保つために: スキーマは `iris/book/schema.go` をミラーして
> います。そこでフィールドが変わったら、このページ（と日本語版）も更新して
> ください。

## フォルダ構成

```text
your-book/
├── config/
│   ├── book.yaml                 # 識別情報・地域・会計年度・通貨
│   ├── chart-of-accounts.yaml    # 勘定科目
│   └── rules.yaml                # 任意の分類ヒント（空でも可）
├── raw/                          # 元資料。構造は自由、種類は中身から判別
├── journals/
│   └── <fy>/<mm>/
│       └── YYYY-MM-DD-<取引先>-NN.md
├── assets/
│   └── YYYY/<asset-name>.md       # 固定資産（取得年別）
├── notes/
│   ├── workflow.md  decisions.md  open-questions.md  todos.md
│   └── raw/<raw/ のミラー>.md      # パースキャッシュ
├── compiled/                      # AI 生成レポート（再生成可能）
├── README.md  LLM-GUIDE.md  CLAUDE.md   # 人間・AI 向けガイド
└── .iris/                         # 実行時状態 — 手で編集しない
```

補足:

- `journals/<fy>/<mm>/` の `<fy>` は仕訳の会計日付（`date:`）が属する
  **会計年度**、`<mm>` は日付の暦月です。暦年会計の帳簿
  （`fiscal_start_month: 1` — 個人事業主は全員）では日付の数字を
  そのまま写すだけです: `2026-07-15` → `journals/2026/07/`。
  4月始まりの帳簿では `2027-02-15` は FY2026 に属するため
  `journals/2026/02/` に置きます。フォルダは常に会計日付を反映し、
  仕訳が対象とする期間ではありません。セグメントは入れ子のフォルダです —
  `journals/2026/07/` と書き、`journals/2026-07/` のようなハイフン 1
  フォルダにはしません。
- フォルダはファイル**内**の日付のキャッシュにすぎず、ファイルが正です。
  別のレイアウトでも壊れることはありません（レポート・シール・
  エクスポートはフォルダではなく日付を読みます）。`iris organize` が
  置き場所のずれた仕訳を正規レイアウトに戻します。
- `.iris/` はローカルの帳簿 ID と同期状態を保持します。マシン固有で同期されません。

## `config/book.yaml`

```yaml
schema_version: 1
book_id: lb_...                 # init 時に発行。不変
name: "Acme Design"
region: JP                      # ISO 3166-1。税・ロケールのルールを選択
language: ja                    # ISO 639-1。勘定科目の言語はこれに従う
currency: JPY                   # ISO 4217
scale: 0                        # 補助単位の指数 — 不変（JPY 0, USD 2, BHD 3）
entity_kind: individual         # individual | company | partnership | trust
fiscal_start_month: 4           # 1〜12
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

## 仕訳ファイル — `journals/<fy>/<mm>/*.md`

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
| `lines` | はい | 2行以上。各行に `account` + `debit`/`credit` のどちらか一方 |
| `lines[].memo` | いいえ | 行ごとのメモ |
| `lines[].quantity` + `unit` | いいえ | `book.yaml` の `units` の単位の数量（常に正。向きは借方/貸方から） |
| `lines[].tax` | いいえ | 日本の消費税 — 下記参照 |
| 本文 | いいえ | 閉じ `---` の後の自由 Markdown |

**金額**は通貨の自然な表記で、`scale` の桁数まで書きます。`scale: 0`（JPY）なら
円単位（`1000` = ¥1000、小数不可）、`scale: 2` なら ドルとセント（`12.34` = $12.34、
裸の `12` は $12.00 で $0.12 ではない）。内部はすべて整数の補助単位です。

**検証:** 借方=貸方、各科目が勘定科目表に存在（またはエイリアス一致）、日付が
ファイル名と一致、ステータスが正当、YAML が解析できる。レポートに載るのは
**`posted`** のみ。

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
```

科目の通常残高側は `type` から導かれます。`aliases` により、別名や別言語で科目を
参照できます。仕訳で参照する前に、ここへ科目を追加してください。

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
declining_rate: 417                # 月あたりベーシスポイント。定率法のみ
asset_account: "資産:工具器具備品"
depreciation_expense_account: "費用:減価償却費"
accumulated_depreciation_account: "資産:減価償却累計額"
acquisition_journal: "[[2026-04-15-apple-01]]"   # 任意の wikilink
disposal:                          # 任意。処分まで無し
  date: 2029-05-10
  proceeds: 50000
  journal: "[[2029-05-10-apple-disposal-01]]"
---
```

JP 固有フィールド（用途区分、特例、償却資産税フラグ）は不透明に同伴し、JP
オーバーレイが読み取ります。

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
| 1  | 2026-04-01 | Amazon JP   |  -5000 | journaled | journals/2026/04/2026-04-01-amazon-01.md |
```

## 同期されるもの・されないもの

有料プランでは、`iris sync` が**同期対象**のファイルをクラウドにミラーします。

- **同期される:** `journals/`、`assets/`、`notes/`（パースキャッシュ含む）、
  `raw/`（バイト列そのまま）、`config/book.yaml`、
  `config/chart-of-accounts.yaml`、`config/rules.yaml`。
- **同期されない:** `.iris/`（実行時状態）、`README.md` / `LLM-GUIDE.md` /
  `CLAUDE.md`（ガイド）、`compiled/`（再生成可能）。

関連: [基本コンセプト](concepts.md) ·
[CLI コマンドリファレンス](cli-reference.md)。
