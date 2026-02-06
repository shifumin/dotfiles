---
description: Gmailのメール検索・取得を行う。
  「メールを検索」「〜からのメール」「最近のメール」「メールを探して」などのリクエストで使用。
---

# Gmail操作

## 操作の判定

| 操作 | トリガーとなる表現例 | 使用スクリプト |
|------|---------------------|---------------|
| 検索 | 「メールを検索」「〜からのメール」「〜のメールを探して」 | gmail_searcher.rb |
| 取得 | 「メールの詳細」「メールを開いて」「本文を見せて」 | gmail_fetcher.rb |

---

## 共通設定

スクリプトパス: `~/ghq/github.com/shifumin/gmail-tools-ruby/`

実行: `mise exec --cd ~/ghq/github.com/shifumin/gmail-tools-ruby -- ruby <script>.rb [options]`

---

## メール検索

### 処理フロー

1. ユーザー入力から検索意図を解釈
2. 自然言語をGmail検索クエリに変換
3. gmail_searcher.rbを実行
4. JSON出力をMarkdown形式に整形して表示

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

```bash
mise exec --cd ~/ghq/github.com/shifumin/gmail-tools-ruby -- ruby gmail_searcher.rb \
  --query='<検索クエリ>' \
  [--max-results=N] \
  [--no-body] \
  [--include-html]
```

### オプション

| オプション | 説明 |
|-----------|------|
| `--query` | **必須** Gmail検索クエリ |
| `--max-results` | 最大取得件数（デフォルト: 10、最大: 100） |
| `--no-body` | 本文を除外（高速化） |
| `--include-html` | HTML本文を取得 |

### 出力の整形

JSON出力を以下のMarkdown形式に変換:

```markdown
## メール検索結果（N件）

検索クエリ: `<query>`

### 1. 件名
- **From**: 送信者名 <email@example.com>
- **Date**: YYYY-MM-DD HH:MM
- **ID**: `message_id`

> snippet（本文プレビュー）

---
```

| 項目 | ルール |
|------|--------|
| 日付 | RFC2822 → `YYYY-MM-DD HH:MM` |
| 送信者 | `"Name" <email>` 形式をそのまま表示 |
| snippet | blockquote（`>`）で表示 |
| 本文 | 要求時のみ表示（500文字超は省略） |
| HTMLメール | `plain_text`が空の場合、`--include-html`で再取得 |
| 0件 | 「該当するメールが見つかりませんでした」 |
| ラベル | 日本語表示（変換表はreference.md参照） |

---

## メール取得

### 処理フロー

1. ユーザーからメッセージIDを取得（検索結果から選択）
2. gmail_fetcher.rbを実行
3. JSON出力をMarkdown形式に整形して表示

### 実行コマンド

```bash
mise exec --cd ~/ghq/github.com/shifumin/gmail-tools-ruby -- ruby gmail_fetcher.rb \
  --message-id='<メッセージID>' \
  [--format=full|minimal|metadata|raw]
```

### オプション

| オプション | 説明 |
|-----------|------|
| `--message-id` | **必須** メッセージID |
| `--format` | 取得形式: full/minimal/metadata/raw（デフォルト: full） |

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

## 認証エラー時

認証はブラウザでのOAuth操作が必要なため、コマンドを自動実行せずユーザーに案内する。

| エラーパターン | 対処 |
|---------------|------|
| `No credentials found` | 初回認証が必要。authenticatorを実行 |
| `invalid_grant` | トークン期限切れ。トークン削除後、authenticatorを再実行 |
| `GOOGLE_CLIENT_ID is not set` | 環境変数の設定を案内 |

### 再認証コマンド

`invalid_grant`（トークン期限切れ）の場合、トークンファイルを削除してから再認証:

```bash
rm -f ~/.credentials/gmail-readonly-token.yaml && mise exec --cd ~/ghq/github.com/shifumin/gmail-tools-ruby -- ruby gmail_authenticator.rb
```

`No credentials found`（初回認証）の場合:

```bash
mise exec --cd ~/ghq/github.com/shifumin/gmail-tools-ruby -- ruby gmail_authenticator.rb
```

---

## 重要な制限事項

1. **読み取り専用**: このスキルはメール検索・取得のみ。送信・削除は不可
2. **添付ファイルダウンロード不可**: ファイル情報の表示のみ
3. **HTML本文**: `body.html`は存在確認のみ。表示はplain_textを優先

---

## 技術仕様

詳細な技術仕様（JSON出力構造、検索演算子など）は `~/.claude/skills/gmail/reference.md` を参照。
