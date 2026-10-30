# CLI と自分の LLM で記帳する

これはファイルファーストな記帳の進め方です。自分の AI アシスタント
（Claude、Cursor、Copilot、その他 MCP 対応エージェント）が帳簿のファイルを
読み書きし、`iris` CLI が検証と集計を行います。仕訳などの記録は YAML
フロントマター付きの Markdown、設定は単独の YAML ファイルです。ローカルの
`iris` はアカウントもネット接続も不要です。AI サービスには接続が必要な場合があります。

## CLI の利用とサポート

`iris` CLI は無料で、**現状のまま（as is）**提供します。動作や出力の正確さ、
個別サポート、不具合の修正、継続的な更新は保証しません。出力は自分で確認し、
帳簿は別途バックアップしてください。質問や不具合の報告は
[Discord コミュニティ](https://discord.gg/wZDsv9gyb9)へお寄せください。回答は保証しません。

## 全体イメージ

設定を選ぶ前に、使いたいものや人に渡したいものを AI と確認します。仕訳を
残したいのか、数字を確認したいのか、資料と説明をまとめて引き継ぎたいのかで、
進め方は変わります。資料が足りなくても、元資料へのリンク、確認済みの事実と
仮の金額、未解決の質問、次の作業を引き継ぎメモに残せます。何を用意すれば
役立つか分からない場合は、AI に提案してもらいます。

そのあとの作業は、次の4段階です。

1. 資料を渡す、AI が読めるファイルの場所を伝える、起きたことを話す。
   必要なツールとアクセス権があれば、明細の取得も AI に頼めます。
2. **AI** が元資料を帳簿内の `raw/` に保存し、内容を読み取り、**仕訳**と説明を提案する。
3. **`iris`** が構造と計算を検証し、レポートを計算する。
4. **あなた**が内容を確認し、承認するか質問する。通常は確認後に記帳します。
   自動記帳を認めている場合は、その帳簿で選んだ方針に従います。

AI は判断と説明、`iris` は検証と計算を担います。手作業でファイルを整理したり、
形式を覚えたりする必要はありません。検証に通っても、資料の読み取りまで
正しかったと保証されるわけではありません。

作業後は、保存した記録や計算結果が自分の目的にどう役立つかを AI に説明して
もらいます。今使えるものと、目的を達成するまでに必要な資料・確認・外部での
作業を分けて確認します。

| 用意できたもの | 今できること |
| --- | --- |
| 元資料とノート | 資料や確認済みの事実を保存し、確認や再開に使えます。仕訳を作る前でも保存できます。 |
| 下書きの仕訳（draft） | 提案内容を確認できます。通常の会計レポートには含まれません。 |
| 記帳済みの仕訳（posted） | 対象の帳簿・期間のレポートに反映されます。申告書の作成・提出は別の作業です。 |

資料が足りない場合も、確認できた内容は保存し、不足する情報をノートに残します。
次に誰が何をすればよいかを AI に説明してもらい、詳しいチェックリストは帳簿と
一緒に保存します。`iris validate` は記録の構造や選択したルールへの適合を確認します。
会話中の計算が正しいか、資料がすべてそろっているか、申告書が完成したかは別途確認が必要です。

## 家計は無理なく続けられる詳しさで

日々の私的な支出は、役に立つ範囲で記録すれば十分です。領収書をすべて残す
必要はありません。今の手持ち現金を伝え、前回から何に使ったかを AI に
大まかに聞いてもらえます。その際、現金の補充や移動も確認します。カードや
銀行の明細があれば、金額をそのまま使い、用途は AI が大まかに分類できます。
推定や使途不明の差額は明記し、架空の買い物で埋めないようにします。

事業の帳簿は、金額・日付・科目を正確にし、根拠となる資料も大切にします。
個人の記録でも、税務や経費精算に使うものは同じ扱いです。希望する記録の
詳しさは `notes/workflow.md` に、推定の根拠は仕訳の本文やノートに残すよう
AI に頼んでください。判断や質問もファイルに残るため、次の会話や別の AI に
作業を引き継げます。同期を使うと、クラウドのコピーとサーバー側の変更履歴も残ります。

## 領収書の明細、家計の集計、過去分の追記

記帳前に、残す詳しさを `notes/workflow.md` で決めます。
事業用Bookで領収書ごとの記録を選ぶ場合は、1仕訳に合計しても元の品目明細を保存してください。
日常の家計管理では、確認済みの支出総額を使い、分類の推定を明示して集計する方法もあります。
本人が決めた基準額以上の購入は別に記録し、費用として追跡するか、資産として管理するかを説明します。
事業用資産や税務の処理は、資産の手順と実際の要件に従います。家計の例の金額や分類からは判断しません。

以下は独立した2つの架空の管理用Bookです。同じ支出を分けた例ではありません。
通貨はJPY、scaleは0、会計年度は2026年1月〜12月、任意のpackageは未選択とします。
各Bookの勘定科目で預金・現金を資産、開始残高を純資産、例に使う費用科目を費用として定義してください。
コードは記帳後の形式です。各Bookの方針と権限の範囲でdraftを作成・確認してpostします。
税務や立替精算に使う場合は、それぞれの資料要件も確認してください。
[国税庁 No.2080](https://www.nta.go.jp/taxes/shiraberu/taxanswer/shotoku/2080.htm)は白色申告の記帳で日々の合計を記載する方法も説明しています。
ここで領収書ごとに残すのは作業方針であり、すべての場合に一律で求められる法的要件ではありません
（令和8年4月1日現在の法令等。2026年10月24日確認）。

### 領収書と口座明細が同じ支払を示す場合は1件にまとめる

事業用Bookの開始残高は預金100,000円、現金10,000円、純資産110,000円です。
1月5日の文具の領収書には2品目ありますが、支払は1件です。

```csv
date,merchant,item,amount,currency
2026-01-05,Synthetic Stationer,Paper,1000,JPY
2026-01-05,Synthetic Stationer,Pens,320,JPY
```

```yaml
schema_version: 1
date: 2026-01-05
status: posted
lines:
  - {account: Expenses:Supplies, debit: 1320}
  - {account: Assets:Cash, credit: 1320}
attachments:
  - {path: raw/receipts/stationery.csv, type: receipt, locator: L2-L3}
```

1月12日のソフトウェア代3,300円は、領収書とカード明細が同じ利用を示します。
`Expenses:Software` を借方、`Liabilities:Card` を貸方に1回だけ計上し、両方の資料を添付します。
カード明細の各利用を既存の領収書仕訳と照合し、未記帳分だけを補います。
1月18日の鉄道代2,200円は領収書がなく、本人が日付・金額・支払者・業務目的を確認したとします。

```csv
date,merchant,amount,purpose,receipt_status
2026-01-18,Synthetic Rail,2200,Owner confirms client meeting travel,missing
```

```yaml
schema_version: 1
date: 2026-01-18
status: posted
tags: [no-receipt]
lines:
  - {account: Expenses:Travel, debit: 2200}
  - {account: Liabilities:Card, credit: 2200}
attachments:
  - {path: raw/cards/2026-01.csv, type: bank_statement, locator: L4}
  - {path: raw/statement-review.csv, locator: L2}
```

`no-receipt` と未入手の原本の問題を `notes/open-questions.md` に残します。
カード明細は利用額を示し、本人の確認記録には目的を残します。この管理用仕訳だけで請求書の適格性や必要経費への算入が決まるわけではありません。
取引内容や金額自体が不明なら、費用を推測せず、分類を保留して不足情報を確認してください。
後日の預金引落はカード債務の精算です。購入費用を再度計上しません。
1月20日の現金引出は `Assets:Cash` を借方5,000円、`Assets:Bank` を貸方5,000円に記録します。費用は発生しません。
後から見つかった1月28日の顧客向けフォルダーの領収書1,100円は、`Expenses:Supplies` と現金で記録します。
発見・確認の経緯をメモに残し、取引日は実際の日付を使ってください。
家計の月次推定を事業の証拠に転用したり、ファイル名から税務上の適格性を決めたりしないでください。
家事按分は[形式リファレンス](book-format-reference.md#費用の事業分と家事分を分ける)の日付付き基準に従います。

### 家計の推定分類と大きな購入を区別する

個人用Bookの開始残高は預金200,000円、現金10,000円、純資産210,000円です。
1月10日に預金から現金へ10,000円を移します。
本人が1月の通常の現金支出総額9,000円を確認し、8,000円・1,000円の分類は推定とします。
個々の店名や取引日は分かっていません。

```csv
period_from,period_through,total_cash_paid,groceries_estimate,transport_estimate,currency
2026-01-01,2026-01-31,9000,8000,1000,JPY
```

```yaml
schema_version: 1
date: 2026-01-31
status: posted
lines:
  - {account: Expenses:Groceries, debit: 8000}
  - {account: Expenses:Transport, debit: 1000}
  - {account: Assets:Cash, credit: 9000}
attachments:
  - {path: raw/interview.csv, locator: L2}
```

1月31日は合意した集計期間の末日です。個々の購入日を推測しているわけではありません。
確認済み総額、推定した分類、対象期間、除外した取引を本文に残してください。
後から正確な領収書で集計の一部を置き換える場合は、その対象額を確認して置換・振替します。
集計に加えて同じ支出を追記すると二重計上になります。
この簡略な記録は家計管理用であり、領収書単位の税務・立替精算の証拠にはしません。

本人が個別記録の基準を **50,000円以上** と決めたとします。
60,000円のソファは1月15日のカード購入として別に残し、現金とカードの両方の集計から除外します。
本人がこの個人用Bookで費用として追跡する方針を選んだ例です。事業の資産計上基準や税務処理を示すものではありません。

```csv
date,merchant,description,amount,currency
2026-01-15,Synthetic Furniture,Personal sofa,60000,JPY
```

```yaml
schema_version: 1
date: 2026-01-15
status: posted
lines:
  - {account: Expenses:Furniture, debit: 60000}
  - {account: Liabilities:Card, credit: 60000}
attachments:
  - {path: raw/receipts/sofa.csv, type: receipt, locator: L2}
  - {path: raw/cards/2026-01.csv, locator: L4-L5}
```

### 口座明細、処理状況、実際の行位置を残す

個人用のカード明細は `raw/cards/2026-01.csv` です。ソファの説明欄には引用符内の改行があります。
元資料の改行を消して整形しないでください。

```csv
date,description,charge,payment,balance
2026-01-01,Opening,0,0,0
2026-01-07,Synthetic Market,12000,0,12000
2026-01-15,"Sofa delivery
order S-15",60000,0,72000
2026-01-19,Synthetic Rail,8000,0,80000
2026-01-31,Closing balance,0,0,80000
```

個人用のカード集計には、スーパー12,000円と鉄道8,000円だけを含めます。
分類の推定は明示し、利用額は明細どおりに記録します。ソファ60,000円は除外します。
**集計20,000円＋個別購入60,000円＝明細の利用額80,000円** です。
ソファは実際の1月15日の日付と資料を保ちます。先の現金支出9,000円は別の集計であり、カード利用額には含めません。

```yaml
schema_version: 1
date: 2026-01-31
status: posted
lines:
  - {account: Expenses:Groceries, debit: 12000}
  - {account: Expenses:Transport, debit: 8000}
  - {account: Liabilities:Card, credit: 20000}
attachments:
  - {path: raw/cards/2026-01.csv, type: bank_statement, locator: L3}
  - {path: raw/cards/2026-01.csv, locator: L6}
```

元の拡張子を保ち、rawからのパス全体を `notes/` の下へ移してメモの場所を決めます。
`raw/cards/2026-01.csv` に対応するのは `notes/raw/cards/2026-01.csv.md` です。
預金も同じ対応で、`raw/bank/2026-01.csv` なら `notes/raw/bank/2026-01.csv.md` になります。
このパースメモはAIが維持する作業記録であり、自動取込や自動の重複防止機能ではありません。
処理済み仕訳への参照を保ちます。開始・終了残高の行は無視する理由を明示します。
処理を終えるために不明な出金を無視しないでください。取引の事実が足りない行は `deferred` とし、
不足している情報を `notes/open-questions.md` に残します。

```markdown
---
source: raw/cards/2026-01.csv
source_sha: sha256:9bfde1fbdc1a8cffcdf724cb867a3dd1980dabdf03efaa2734682bcbe386991b
parsed_at: 2026-10-24
counts: {total: 5, journaled: 3, ignored: 2, deferred: 0}
---

## Rows

| id | date | description | amount | status | target / reason | locator |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-01-01 | Opening | 0 | ignored | Zero opening liability; no transaction | L2 |
| 2 | 2026-01-07 | Synthetic Market | -12000 | journaled | journals/2026-01/2026-01-31-card-summary.md | L3 |
| 3 | 2026-01-15 | Sofa delivery / order S-15 | -60000 | journaled | journals/2026-01/2026-01-15-sofa.md | L4-L5 |
| 4 | 2026-01-19 | Synthetic Rail | -8000 | journaled | journals/2026-01/2026-01-31-card-summary.md | L6 |
| 5 | 2026-01-31 | Closing balance | 0 | ignored | Balance-only observation; no transaction | L7 |

IDs count data records, excluding the header. Locators count actual physical
lines, including the header and quoted line breaks. Ignored opening/closing
rows are balance metadata, not skipped spending. Negative charge amounts in
this note are statement presentation; liability assertions use credit-positive
account direction. This assistant-maintained note is not a native importer or
automatic duplicate guarantee. Preserve completed targets before backfilling.
```

データレコードID 3は実際の `L4-L5`、ID 4は `L6` に対応します。
IDはヘッダーと引用符内の改行を数えません。`L` は両方を含む実際の行番号です。
ネイティブのCSV読取とWebプレビューで、この行範囲を保ちます。
メモを再利用する前に、`source_sha` と `iris hash` を照合してください。
明細が再発行された場合は別に保存し、変更行を既存の仕訳参照と比較して、完了済みの判断も残します。
hashを更新するだけでは照合になりません。領収書と口座明細が同じ取引なら、費用も1件です。

### 元資料で過去分を補い、現金も別に照合する

個人用Bookで1月31日に確認した現金は10,970円です。

```csv
date,owner_reported_cash
2026-01-31,10970
```

後から見つかった領収書をpostする前の帳簿上の現金は11,000円です。
`iris reconcile` は実際11,000円・期待10,970円・差額+30円を表示して終了コード1を返します。預金190,000円は一致しています。
理由が分からない間は差額を残してください。30円の購入を作ったり、確認値を書き換えて一致させたりしません。
10月24日に1月29日のコピー代の元の領収書が見つかり、9,000円の集計には含まれないことを確認したとします。
元資料を保存し、取引日は実際の日付を使います。

```csv
date,merchant,description,amount,currency
2026-01-29,Synthetic Library,Personal copies,30,JPY
```

```yaml
schema_version: 1
date: 2026-01-29
status: posted
lines:
  - {account: Expenses:Copies, debit: 30}
  - {account: Assets:Cash, credit: 30}
attachments:
  - {path: raw/receipts/backfill.csv, type: receipt, locator: L2}
```

発見・確認した日時は `notes/backfill.md` に説明します。取引日やファイル名の日付の代わりには使いません。
draftの作成前に、すでに記帳されていないか確認してください。
postには通常の権限とsealの確認が必要です。この例では2026年度が未封印であると仮定します。
終了済み・過年度の場合は、権限のある再開・訂正の手順を使います。今日の取引へ移したり、封印済みの入力を書き換えたりしないでください。
元資料がそろわない問題は、未解決の質問として残します。

[残高照合](book-format-reference.md#残高照合)に `scope: posted`、`unit: JPY` を明示して観測値を追加します。
CSVから確認値が自動作成されるわけではありません。事業用Bookは1月27日の現金13,680円、
1月31日の現金12,580円・預金95,000円・カード債務5,500円を確認します。負債は貸方を正とします。
個人用の確認値は、1月の預金・現金・カード債務と、2月の預金・精算後の債務を確認します。

```yaml
schema_version: 1
assertions:
  - id: cash-close
    date: 2026-01-31
    account: Assets:Cash
    measure: amount
    unit: JPY
    scope: posted
    expected: 10970
    evidence: {path: raw/cash-count.csv, sha: sha256:397b3eadca51ca10e939460e0ee82390a7aec7312db5e633b011e3a6054654e8, locator: L2}
  - id: bank-close
    date: 2026-01-31
    account: Assets:Bank
    measure: amount
    unit: JPY
    scope: posted
    expected: 190000
    evidence: {path: raw/bank/2026-01.csv, sha: sha256:a175549e16e2ccdda81172918c7ec2a89c3731c299d5b127d050ddeda48889c7, locator: L4}
  - id: card-close
    date: 2026-01-31
    account: Liabilities:Card
    measure: amount
    unit: JPY
    scope: posted
    expected: 80000
    evidence: {path: raw/cards/2026-01.csv, sha: sha256:9bfde1fbdc1a8cffcdf724cb867a3dd1980dabdf03efaa2734682bcbe386991b, locator: L7}
  - id: bank-after-card-payment
    date: 2026-02-28
    account: Assets:Bank
    measure: amount
    unit: JPY
    scope: posted
    expected: 110000
    evidence: {path: raw/bank/2026-02.csv, sha: sha256:6ad346750ec1cdbe6ed31cf4cfeaa8f07143cd1614c565ef2ae7168845cd04e2, locator: L3}
  - id: card-after-payment
    date: 2026-02-28
    account: Liabilities:Card
    measure: amount
    unit: JPY
    scope: posted
    expected: 0
    evidence: {path: raw/cards/settlement.csv, sha: sha256:b3b8cf9395f45432e2072b7858cd8d7770c0404c659af4e391416442b2e9674f, locator: L2}
```

実際の資料に基づく追記を確認・postした後、次の読取専用コマンドで照合します。

```bash
iris validate --json /path/to/business
iris reconcile /path/to/business
iris report pl --from 2026-01-01 --to 2026-01-31 /path/to/business
iris report pl --from 2026-02-01 --to 2026-02-28 /path/to/business
iris validate --json /path/to/personal
iris reconcile /path/to/personal
iris report pl --from 2026-01-01 --to 2026-01-31 /path/to/personal
iris report pl --from 2026-02-01 --to 2026-02-28 /path/to/personal
```

| 1月末の確認値 | 事業用 | 個人用 |
| --- | ---: | ---: |
| 預金 | 95,000 | 190,000 |
| 現金 | 12,580 | 10,970 |
| カード債務 | 5,500 | 80,000 |
| 費用 | 7,920 | 89,030 |
| 収入 | 0 | 0 |
| 純資産 | 102,080 | 120,970 |

2月10日の引落は `Liabilities:Card` を借方、`Assets:Bank` を貸方に記録します。
事業用5,500円、個人用80,000円です。2月28日の預金は89,500円・110,000円、カード債務は0円になります。
現金と純資産は変わらず、2月の収入・費用も0円です。2月の預金・カードの元資料でも確認します。
残高照合は事業用6件、個人用5件です。

実行確認用の各Bookには、7仕訳、元の預金・カード明細、hashで対応付けたパースメモ、独立した現金確認、詳しさの方針、追記の経緯を含めています。
事業用の費用は1,320円＋3,300円＋2,200円＋1,100円、個人用は60,000円＋20,000円＋9,000円＋30円です。
預金の一致だけでは個人用の現金差額を見落とします。預金・現金と費用総額が一致していても、ソファの分類と元資料を個別に残した証明にはなりません。
合計額とともに、選んだ詳しさが保たれているかも確認します。

## 税理士も顧客ごとの作業フォルダで記帳する

税理士・会計事務所にも、自分の AI と帳簿ファイルで作業する方法を勧めます。
顧客ごとに帳簿を保存するフォルダを分け、専用の AI セッションや VM には
その顧客のフォルダだけを渡します。たとえば、顧客Aの Cowork セッションには
顧客Aの必要な年度の帳簿だけを読み書きさせ、全顧客をまとめた親フォルダは渡しません。

共有された既存の帳簿をそのフォルダに clone し、権限のある手順で同期します。
ガイドとノートを読み、修正案の作成・検証・記帳をその帳簿の方針に沿って進めます。
引き継ぎに必要な情報も顧客のファイルに残します。一時的な VM とは別に、
継続して保管できる場所にもコピーを持ってください。

接続ツールや認証情報の範囲も確認します。ホスト側の共通 MCP サーバーは、
指定フォルダの外にあるクラウド帳簿にもアクセスできる場合があります。PAT の
役割指定も、顧客を1社に限定する機能ではありません。事務所全体の認証情報や
一括処理ツールは顧客の AI セッションに渡さず、必要なら clone・同期を別の環境で
行い、対象ファイルと他の顧客に届かないツールだけを渡します。実際のアクセス範囲を確認してください。

[Web アプリ](web-app.md) はレポートの閲覧、レビュー、権限に応じた承認、履歴確認に
使い、ファイルでの作業を補います。

## 最初の一度: AI をつなぐ

AI が CLI を実行でき、帳簿を読み書きできるなら MCP の登録は不要です。MCP 接続を
使いたい場合や、不足するローカルの案内を追加したい場合に `iris onboard` を実行します。

```bash
iris onboard
```

`iris onboard` は `iris mcp serve`（`iris` の各動詞をツールとして公開する小さな
サーバー）を MCP 対応アシスタントに登録し、Claude Code スキルを書き込みます。
Claude Code には常に登録され、Claude Desktop・Codex・Cursor・Gemini CLI・
VS Code はインストールが検出された場合に登録されます。これにより、アシスタント
は台帳の状態を推測せず、`validate`・`diff`・`balance`・`report`・`status`、そして
サインイン後は `sync` を直接呼べます。

現在の接続状態は `iris onboard --status` でいつでも確認できます（AI 向けには
`--json` を追加）。`iris onboard` の再実行は常に安全で、登録はその場で更新され
ます。すべて元に戻すには `iris offboard` — 帳簿やサインインには触れずに、登録
とスキルを削除します。

この接続設定は、帳簿フォルダがあるマシンのためのものです。クラウド連携済みの
帳簿なら、外出先でも同期済みの記録やレポートを読めます。リモートコネクタは読み取り専用で、
変更にはローカルの環境を使います。
[外出先の AI から帳簿へ（リモートコネクタ）](remote-connector.md)
を参照してください。

新しい帳簿には、英語の短い作業ガイド `AGENTS.md` がルートに入ります。
記帳ポリシー、データを守るルール、最小限の仕訳例、資料の調べ方をまとめています。
ローカルの CLI・MCP と Web・API は同じひな形を使います。このファイルは帳簿と
同期され、クローンでも既存の内容が保たれます。`README.md` はフォルダーの説明、
`CLAUDE.md` は `AGENTS.md` への案内です。Owner は内容を変更できます。
クラウドでの変更にも Owner 権限が必要です。古いローカル帳簿では `iris onboard` が
不足するガイドを追加し、既存の `LLM-GUIDE.md` の方針を `AGENTS.md` に引き継ぎます。
カスタマイズ済みのガイドは上書きしません。

> **サンドボックス内のアシスタント**（`iris` バイナリの無い VM など）: 帳簿内に
> 同梱コピーはありません。ホストの MCP を使う場合は、ホストが `iris mcp serve`
> を実行し、アシスタントは同じフォルダに対してツールを呼び出します。顧客の
> 作業では、ホストへの接続も前述のアクセス範囲に制限してください。

Cowork の `.mcpb` 拡張では、**帳簿をまとめる親フォルダ**（例: `~/IrisBooks`）を
選び、各帳簿をその直下の子フォルダに置きます。Cowork にも作業するフォルダへの
ファイルアクセスを許可してください。親フォルダが空でも起動でき、AI に
`create_book` で帳簿を作るよう依頼できます。AI は `list_books` で帳簿を確認し、
各操作で対象の帳簿を指定します。子フォルダに帳簿を追加するたびに MCP の共通設定を
変更する必要はありません。手動で設定する場合は
`iris mcp serve --books-dir ~/IrisBooks` を使います。`--book-path PATH` も引き続き
1 つの帳簿に使えます。[MCP コマンド](cli-reference.md#iris-mcp)も参照してください。

税理士の作業では、親フォルダに1社の帳簿だけを置きます。たとえば、
`~/IrisBooks/ClientA/2026` と `~/IrisBooks/ClientA/2027` を置き、顧客Aの
AI の接続先は `~/IrisBooks/ClientA` にします。クラウドの認証情報の範囲も
別途確認してください。会話を分けるだけではアクセスは制限されません。

## オンラインの案内と任意のダウンロード

AI は帳簿の `AGENTS.md`、作業の現状、関係する質問や過去の判断を確認してから、
使用中のコマンドのヘルプやツールの入力形式を使います。`iris docs` は同梱された英語資料の
トピック、`iris docs <topic>` は節と語数を一覧します。`--section <id>` は必要な節、
`--full` は章の全文を明示的に読みます。ローカル MCP の `read_docs` も `topic`・
`section`・`full` で同じ内容を返し、帳簿の指定は不要です。認証・ダウンロード・通信は不要です。

導入を依頼する場合は[開始ガイド](/start/)、現在のクラウド認証は
[クラウド接続](/start/cloud/)を使います。同梱資料を読めない古いツールは
[索引](/llms.txt)を使えます。[AI 向け全マニュアル](/llms-full.txt)は任意の参照資料です。
Markdown を保存する場合は帳簿の外に置き、取得元とリリースタグを残します。
`https://raw.githubusercontent.com/irisbooks/iris/<release-tag>/docs/llm.md` のタグは、
可能なら `iris version` と一致させ、必要な節だけを検索します。帳簿のルールは選択中の
オーバーレイを確認してください。資料を読むことは操作の許可にはなりません。

## iris のバージョンを確認して更新する

```bash
iris update --check --json     # 使用中のバージョン・最新版・実行ファイルの場所
iris update                   # 検証してから実行ファイルを置き換える
```

更新確認は、指定したときだけ公開サーバーに問い合わせます。ログインは不要です。
帳簿の操作は引き続きオフラインで使えます。確認に失敗した場合、最新版かどうかは
不明です。開発版・リリース候補は `development` と表示され、自動では置き換えません。
公開版より新しいバージョンを古いものに戻すこともありません。

更新後は帳簿のフォルダーで `iris onboard` を実行して AI 向けの案内を更新し、
IrisBooks の MCP サーバーを再起動します。AI に `check_update` を呼び出してもらい、
サーバーが使うバージョンを確認してください。結果には実行ファイルの場所と、
PATH が別のファイルを指している場合の案内も表示されます。

`.mcpb` 拡張には別の実行ファイルが含まれます。確認結果のリンクから対応する
バンドルを入手し、同じ親フォルダを指定してクライアントの拡張設定から入れ直し、
再起動してください。1 つの帳簿を指定する旧版から更新する場合は、その帳簿の
親フォルダを新しい設定で選びます。CLI の更新だけでは拡張は更新されません。Windows で実行ファイルが
使用中のため置き換えられない場合は、IrisBooks の MCP サーバーを停止して再実行します。

`iris update` がない古い版は、[インストーラー](getting-started.md)を再実行して更新し、
続けて `iris onboard` を実行します。AI が更新をインストールする前には、ユーザーの
許可が必要です。すでに更新を依頼されている場合は、再確認は不要です。

## 毎日のループ

### 1. AI に情報を渡す

銀行CSV、領収書の画像、PDF 請求書をチャットに添付するか、AI が読める
フォルダの場所を伝えます。必要なツールとアクセス権を与えて取得を頼む方法も
あります。元資料の `raw/` への保存は AI に任せられます。自分で置きたい場合は、
日付別・取引先別などのサブフォルダも自由に使えます。家計の現金支出なら、
資料なしで、残高と短い聞き取りから始めることもできます。

### 2. AI に処理させる

アシスタントに「この明細を記録して」「最近の家計の現金支出を整理したい」などと
頼みます。`AGENTS.md` に従い、AI は次を行います。

- 資料がある場合は全文読み、`notes/raw/<source>.md` に**パースキャッシュ**を書きます。
  各行を `journaled`・`ignored`・`deferred` で記録した恒久的な表です。あとで同じ
  明細を開き直しても作業をやり直さずに済みます。
- 聞き取りの場合は、伝えた内容や推定の根拠を仕訳の本文やノートに残します。
- 希望する詳しさに合わせて、`journals/YYYY-MM/…-NN.md` に `status: draft` の仕訳を提案します。
- 事業の判断で未解決の点や重要な不明点は `notes/open-questions.md` に記録します。
  家計の推定額や推測した分類も明記します。

### 3. 検証する

```bash
iris validate
```

全ファイルをチェックします。YAML が解析でき、借方=貸方、科目が勘定科目表に存在し、
日付が整合し、ステータスが正当で、（日本の課税事業者向けには）税区分が整合して
いるか。エラー — たいていは勘定科目表に無い科目か、貸借不一致 — を直して再実行
します。このループは AI に任せられます。

`iris validate` の末尾に「同期キューでブロックされたファイルがある」旨の注記が
出た場合、それはファイルの問題ではなくサーバー側の拒否です。
[トラブルシューティング](troubleshooting.md) を参照。

### 4. レビューして帳簿を読む

```bash
iris balance                         # 本日時点の試算表（記帳済みのみ）
iris report pl --from 2026-04-01 --to 2026-06-30
iris report bs --as-of 2026-06-30
iris search --payee amazon --from 2026-04-01     # 仕訳を検索
iris references raw/2026-05-invoice.pdf                # この資料を引用する仕訳
```

帳簿フォルダにアクセスできる場合、通常のファイル一覧・読み取り・文字列検索・
下書きやノートの編集には `rg`・`grep`・`find`・`cat`・`sed` やエディタを使います。
操作は選択した帳簿内で行い、記帳データを編集した後は検証します。ローカル MCP は
会計計算、検証、認証、同期、記帳・締め・償却・翌年度帳簿の
作成などの専用処理に使います。検索などの参照ツールは任意の補助です。
構造化した条件や締め済み状態での検索、ファイルに直接アクセスできないクライアント
で利用できます。

`iris search` と `iris references` は、構造化したオフラインの参照にも使えます。

### 5. 記帳する

下書きは、記帳するまで各種レポートや残高に反映されません。内容に納得できたら
記帳します。

```bash
iris post journals/2026-05/2026-05-04-example-com-01.md
```

`iris post` はファイルを検証（空でない・貸借一致）し、`status: posted` にし、
帳簿がクラウド連携済みなら同期します。`--dry-run` で変更せず確認できます。
`status:` フィールドを手で編集してもかまいません。`post` は貸借チェックと同期を
兼ねた便利コマンドです。

## オンラインにする（クラウド）

ローカル帳簿をクラウドにリンクすると、Web アプリ・複数端末・共同作業・期間
年度の締め・恒久履歴が使えるようになります。上記のファイルファーストな
流れは変わらず、`iris sync` が増えるだけです。

```bash
iris api login            # ブラウザでサインイン。このデバイス専用の CLI セッションが発行される
iris api whoami           # 実際に使う認証情報とAPI接続先を確認
iris api books new        # クラウド帳簿を作成…
# …または既存のものにこのフォルダをリンク:
iris api books link <book-id>
iris sync                 # 明示的な push + pull を1回
```

ブラウザー認証は、CLI側のコールバックへ接続できる環境で使います。
リモート・画面のない環境や別のブラウザープロファイルで承認する場合は、`iris api login --device` を選びます。
本人の端末で承認した後、`iris api login --device-complete` と `iris api whoami` で確認してください。
許可待ちは認証の完了ではありません。[ログイン方式とアカウントの分離](cli-reference.md#iris-api-login)も参照してください。

ブラウザーで承認するときに、この CLI で利用する帳簿を選んでください。
最初の帳簿や翌年度の帳簿を作る場合は、**帳簿の作成を許可する**を選びます。
この認証情報で作成した帳簿には同じ操作権限でアクセスでき、他の方法で追加された
帳簿は含まれません。コールバック・ファイル・端末認証の承認画面は同じ選択方式です。
年度の引継ぎには、引継ぎ元の Owner 権限と Full の操作権限が必要です。

以後：

- `iris sync` はローカルの変更を push し、新規分（例：税理士がファイルで作成・同期した
  仕訳）を pull します。ファイルごとに受理/拒否を報告します。
- `iris diff` は同期前に「何が push されるか」を正確に表示します。
- `iris api history --path journals/2026-05/...md <book-id>` はファイルの
  訂正・削除の履歴を表示します。

同期は**明示的**なまま — 依頼したときだけ動き、裏では動きません。

## 固定資産と減価償却

償却資産がある場合は、各資産を `assets/YYYY/<name>.md` に記述します（取得価額・
耐用年数・方法）。続いて：

```bash
iris asset schedule                       # 各資産の償却計画を見る
iris asset depreciate --year 2026         # 資産ごとに期末の仕訳を 1 本
iris asset depreciate --month 2026-05     # 月次で締めるならその月の仕訳を生成
```

`iris asset depreciate` は提案仕訳（`status: draft`）を書き出すので、ほかの仕訳と
同様にレビューして記帳します。詳細と日本固有のルールは
[日本の税務・コンプライアンス](japan-tax-and-compliance.md) に。

### AI が間違えられない減価償却

定額法は iris が自分で計算します。国ごとの事情が入る方法 — 日本の定率法、米国の
MACRS — は進め方が違います。AI が償却率を調べ、方法が切り替わる時点を判断し、
計算は iris に渡して、出来上がった表を資産ファイルの `schedule:` に記録します。

そのために MCP 経由で次の資産ツールが使えます。

| ツール | 役割 |
| --- | --- |
| `asset_schedule` | エンジンによる資産別の数値。申告にはこの値をそのまま使う |
| `declining_table` | 指定した率での定率法の表 |
| `flat_table` | 償却し終わるまで一定額を計上する表 |
| `straight_line_table` | 基準額を N 期間で均等に割る表 |
| `list_recipes` / `run_recipe` | 地域オーバーレイに用意された組み合わせ。あればこちらを優先 |

両モードとも `list_recipes` で CLI と同じレシピ ID と入力形式を確認し、
`run_recipe(recipe=..., params={...})` で結果を表示します。保存時は `apply=true` と
帳簿相対パスの `out` を追加します。`out` だけでは保存しません。親モードは `book` も必要です。

肝心なのは、AI が残高を手で掛け算していかないことです。計算の取りこぼしはそこで
起き、しかも合計だけは合ってしまう取りこぼしは iris には見抜けません。だから
正確な表を組み合わせる形にしています。さらに、帳簿の地域オーバーレイにその方式の
**レシピ**があれば — 日本の定率法は `jp-declining-balance.teiritsu` — AI はその ID で `run_recipe` を呼びます。レシピが
決められた順序で表を組み立て、行の出どころを記録するので、`iris validate` が
再計算して 1 年遅れの切替を捕まえられます。手で組み合わせるのは、レシピのない
方式の代替手段です。ファイル形式と iris が検査する内容は
[`schedule:`](book-format-reference.md#schedule-計算させるか表を記録するか) に。

## エクスポート

```bash
iris export                 # journals.csv, trial-balance.csv, ledger-*.csv
iris export --year 2026     # 会計年度で絞り込み
iris export assets          # 資産別の償却スケジュール
```

CSV は、日本語などの非 ASCII 文字を Excel が正しく開けるよう UTF-8（BOM 付き）で書き出します。
文字列のセル（取引先・摘要・タグ・勘定科目名・資産名）が `=`・`+`・`-`・`@` で
始まる場合は先頭に `'` を付けて書き出します。表計算ソフトが数式として実行せず、
文字列として表示するためです。金額のセルは変えません。
クラウド連携済みの帳簿では、`iris api history --all --json <book-id>` で
帳簿の（つまりその年度の）訂正・削除の履歴をファイルに書き出せます。

## やってはいけないこと

次のルールが帳簿の信頼性を保ちます（AI もこれに従います）。

- 記帳済みの仕訳を一括編集しない — 訂正仕訳を起こす。
- `compiled/` を手で編集しない — 再生成可能な出力。
- 仕訳の中で科目を勝手に作らない — 先に勘定科目表へ追加する。

次へ: GUI 側は [Web アプリを使う](web-app.md)、全コマンドは
[CLI コマンドリファレンス](cli-reference.md)。
