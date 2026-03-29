---
description: Gmailのメール検索・取得・迷惑メール管理・カテゴリタブ一括整理を行う。
  ユーザーがメールに関する操作を求めたら必ずこのスキルを使用すること。
  「メールを検索」「〜からのメール」「〜のメールある？」「未読メール確認」「メール何通来てる？」
  「迷惑メールを削除」「スパムを整理」
  「Socialタブを整理」「プロモーションを整理」「ソーシャルメールをアーカイブ」「SNS通知を既読に」
  「最近Amazonで何か買ったっけ」「請求書のメール探して」のような間接的なメール確認リクエストにも対応。
---

# Gmail操作

## 操作の判定

| 操作 | トリガーとなる表現例 | 使用コマンド |
|------|---------------------|-------------|
| 検索 | 「メールを検索」「〜からのメール」「〜のメールを探して」 | `+triage` / `messages get` |
| 取得 | 「メールの詳細」「メールを開いて」「本文を見せて」 | `messages get` |
| スパム管理 | 「迷惑メールを削除」「スパムを整理」「迷惑メール確認」 | `messages list` + `messages trash` |
| カテゴリタブ整理 | 「Socialタブを整理」「プロモーションを整理」「SNS通知を既読に」 | `+triage` + `messages batchModify` |

---

## 共通設定

Google Workspace CLI（`gws`）を使用:
```bash
gws gmail <subcommand> [options]
```

---

## メール検索

### 処理フロー

1. ユーザー入力から検索意図を解釈
2. 自然言語をGmail検索クエリに変換
3. gwsコマンドを実行
4. 出力をMarkdown形式に整形して表示

### 自然言語からGmail検索クエリへの変換

| 自然言語表現 | Gmail検索クエリ |
|-------------|----------------|
| 「Amazonからのメール」 | `from:amazon.co.jp` |
| 「〜さんへのメール」 | `to:email@example.com` |
| 「件名に請求書を含む」 | `subject:請求書` |
| 「今週のメール」 | `newer_than:7d` |
| 「先月のメール」 | `newer_than:1m` |
| 「今年のメール」 | `after:YYYY/01/01`（現在年を使用） |
| 「1月1日以降」 | `after:YYYY/01/01` |
| 「12月31日まで」 | `before:YYYY/12/31` |
| 「添付ファイル付き」 | `has:attachment` |
| 「PDFが添付されている」 | `filename:pdf` |
| 「未読メール」 | `is:unread` |
| 「ラベル〜のメール」 | `label:ラベル名` |
| 「重要なメール」 | `is:important` |
| 「スター付き」 | `is:starred` |

### 複合クエリの組み立て

複数の条件はスペースで連結（AND検索）:
- 「Amazonからの今月のメール」→ `from:amazon.co.jp newer_than:1m`
- 「添付ファイル付きの請求書」→ `subject:請求書 has:attachment`

### 実行コマンド

#### 概要のみ（本文不要 — デフォルト）

```bash
gws gmail +triage --query '<検索クエリ>' --max <N> --format json
```

#### 本文付き

Step 1: メッセージ一覧取得
```bash
gws gmail +triage --query '<検索クエリ>' --max <N> --format json
```

Step 2: 各メッセージの本文取得（必要な分だけ）
```bash
gws gmail users messages get --params '{"userId":"me","id":"<message_id>"}' --format json
```

### オプション

| オプション | 説明 |
|-----------|------|
| `--query` | **必須** Gmail検索クエリ |
| `--max` | 最大取得件数（デフォルト: 20） |
| `--format` | 出力形式: json / table / yaml / csv |
| `--labels` | ラベル名を出力に含める |

### 出力の整形

`+triage` のJSON出力を以下のMarkdown形式に変換:

```markdown
## メール検索結果（N件）

検索クエリ: `<query>`

### 1. 件名
- **From**: 送信者名 <email@example.com>
- **Date**: YYYY-MM-DD HH:MM
- **ID**: `message_id`

---
```

| 項目 | ルール |
|------|--------|
| 日付 | RFC2822 → `YYYY-MM-DD HH:MM` |
| 送信者 | `"Name" <email>` 形式をそのまま表示 |
| 本文 | 要求時のみ `messages get` で取得して表示（500文字超は省略） |
| HTMLメール | `messages get` で取得したpayloadから抽出 |
| 0件 | 「該当するメールが見つかりませんでした」 |
| ラベル | 日本語表示（変換表はreference.md参照） |

---

## メール取得

### 処理フロー

1. ユーザーからメッセージIDを取得（検索結果から選択）
2. `messages get` を実行
3. レスポンスから情報を抽出し、Markdown形式に整形して表示

### 実行コマンド

```bash
gws gmail users messages get --params '{"userId":"me","id":"<メッセージID>"}' --format json
```

### gws出力からの情報抽出

gws はGmail API の生レスポンスを返す。以下のフィールドを `payload.headers` から抽出:

| 表示項目 | ヘッダー名 |
|---------|-----------|
| 件名 | `Subject` |
| From | `From` |
| To | `To` |
| 日付 | `Date` |

本文は `payload.parts` または `payload.body` の `data` フィールドからBase64デコードして取得。
ラベルは `labelIds` フィールドから取得。

### 出力の整形

```markdown
## メール詳細

- **件名**: 件名
- **From**: 送信者
- **To**: 宛先
- **Date**: YYYY-MM-DD HH:MM
- **Labels**: ラベル1, ラベル2

### 本文

本文テキスト...

### 添付ファイル（N件）

| ファイル名 | 種類 | サイズ |
|-----------|------|-------|
| file.pdf | application/pdf | 1.2 MB |
```

---

## バッチ操作（スパム管理・カテゴリタブ整理）

### 処理フロー（共通）

1. **一覧取得**: gwsコマンドで対象メールを一覧表示
2. **ユーザー確認**: テーブル形式で表示し、操作の同意を得る
3. **実行**: 確認後、操作に応じたgwsコマンドで処理

### 操作別パラメータ

| 操作 | 検索コマンド | 実行コマンド |
|------|------------|-------------|
| スパム管理 | `messages list`（`includeSpamTrash:true`必須）+ 各IDに `messages get`（metadata） | 各IDに `messages trash` |
| Socialタブ整理 | `+triage --query 'category:social is:unread'` | `messages batchModify` (removeLabelIds: INBOX,UNREAD) |
| Promotionsタブ整理 | `+triage --query 'category:promotions is:unread'` | `messages batchModify` (removeLabelIds: INBOX,UNREAD) |
| 汎用ラベル操作 | `+triage --query '<任意クエリ>'` | `messages batchModify` |

他のカテゴリ（Updates、Forums）も同様に `category:<name> is:unread` で対応可能。
汎用ラベル操作では `addLabelIds` でラベル付与、`removeLabelIds` でラベル削除が可能（少なくとも一方は必須）。例: 特定メールに一括でラベルを付ける、特定条件のメールをまとめてアーカイブする等。

### Step 1: 一覧取得

**カテゴリタブ整理**:
```bash
gws gmail +triage --query '<検索クエリ>' --max 50 --format json
```

**スパム管理**（`+triage`はスパムフォルダ非対応のため`messages list`を使用）:

Step 1-1: メッセージID一覧を取得
```bash
gws gmail users messages list --params '{"userId":"me","q":"label:spam","maxResults":50,"includeSpamTrash":true}' --format json
```

Step 1-2: 各IDのメタデータを取得（件名・送信者・日時の表示用）
```bash
# 各メッセージIDに対して並列実行
gws gmail users messages get --params '{"userId":"me","id":"<message_id>","format":"metadata","metadataHeaders":["Subject","From","Date"]}' --format json
```

`format: metadata` + `metadataHeaders` で必要なヘッダーのみ取得し、本文ダウンロードを回避する。
レスポンスの `payload.headers` から Subject / From / Date を抽出してテーブル表示に使用する。

### Step 2: ユーザーへの表示と確認

JSON出力をテーブル形式に変換して表示:

```markdown
## <操作名>一覧（N件）

| # | 送信者 | 件名 | 日時 |
|---|--------|------|------|
| 1 | sender@example.com | Subject line | 2026-02-10 15:30 |

これらのメール（N件）を<操作（ゴミ箱に移動/アーカイブして既読に）>しますか？
```

| 項目 | ルール |
|------|--------|
| 全件表示 | **全メールを1件ずつテーブルに表示する。「〜等」「〜など」で要約・省略しない** |
| 日付 | RFC2822 → `YYYY-MM-DD HH:MM` |
| 確認 | **必ずユーザーの明示的な同意を得てから実行** |
| 0件 | 「対象のメールはありません。」と表示して終了 |

### Step 3: 実行

**スパム管理** — 各メッセージをゴミ箱に移動:

```bash
# 各メッセージIDに対して実行
gws gmail users messages trash --params '{"userId":"me","id":"<message_id>"}'
```

**カテゴリタブ整理** — ラベル一括変更:

Step 3-1: +triageの出力から全メッセージIDを収集

Step 3-2: batchModifyでラベル変更
```bash
gws gmail users messages batchModify --params '{"userId":"me"}' --json '{"ids":["id1","id2",...],"removeLabelIds":["INBOX","UNREAD"]}'
```

**注意**: batchModifyの `ids` にはメッセージIDの配列を渡す。+triageの出力からIDを収集する。`addLabelIds` が必要な場合は JSON に追加。

### 結果の表示

成功時:

```markdown
## <操作名>完了

- **対象件数**: N件
- **処理成功**: N件
- **結果**: 成功
```

一部失敗時:

```markdown
## <操作名>結果

- **対象件数**: N件
- **処理成功**: M件
- **失敗**: K件
- **結果**: 一部失敗（失敗したメッセージIDを報告）
```

---

## 認証エラー時

認証トークンエラーが発生した場合:

```bash
gws auth login -s gmail
```

ブラウザが開くので、ユーザーにOAuth認証を完了してもらう。

認証状態の確認:
```bash
gws auth status
```

---

## 重要な制限事項

1. **送信可能**: `gws gmail +send` で送信可能（必要に応じて別途スキル化）
2. **完全削除不可**: スパム管理はゴミ箱への移動のみ。完全削除（expunge）はできない
3. **添付ファイルダウンロード不可**: ファイル情報の表示のみ
4. **本文取得は2ステップ**: `+triage` は概要のみ。本文が必要な場合は `messages get` で個別取得
5. **スコープ一元管理**: readonly/modifyの区別なし。`gws auth login -s gmail` で全操作対応

---

## 技術仕様

詳細な技術仕様（JSON出力構造、検索演算子など）は `~/.claude/skills/gmail/reference.md` を参照。
