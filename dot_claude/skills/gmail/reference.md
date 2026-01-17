# Gmail技術仕様

統合スキル `~/.claude/skills/gmail/SKILL.md` から参照される技術仕様。

## スクリプト一覧

| スクリプト | 用途 |
|-----------|------|
| gmail_searcher.rb | メール検索 |
| gmail_fetcher.rb | メール取得 |
| gmail_authenticator.rb | OAuth認証 |

パス: `~/ghq/github.com/shifumin/gmail-tools-ruby/`

---

## Searcher (gmail_searcher.rb)

### 引数

| 引数 | 必須 | 説明 |
|------|------|------|
| `--query` | 必須 | Gmail検索クエリ |
| `--max-results` | 任意 | 最大取得件数（デフォルト: 10, 最大: 100） |
| `--no-body` | 任意 | 本文を除外（高速化） |

### JSON出力構造

```json
{
  "query": "from:amazon.co.jp",
  "result_count": 3,
  "messages": [
    {
      "id": "18abc123def456",
      "thread_id": "18abc123def000",
      "date": "Fri, 17 Jan 2025 10:30:00 +0900",
      "from": "Amazon.co.jp <auto-confirm@amazon.co.jp>",
      "to": "user@example.com",
      "subject": "ご注文の確認",
      "snippet": "ご注文ありがとうございます。お届け予定日...",
      "labels": ["INBOX", "UNREAD", "CATEGORY_UPDATES"],
      "body": {
        "plain_text": "本文テキスト...",
        "has_html": true
      }
    }
  ]
}
```

---

## Fetcher (gmail_fetcher.rb)

### 引数

| 引数 | 必須 | 説明 |
|------|------|------|
| `--message-id` | 必須 | メッセージID |
| `--format` | 任意 | 取得形式（デフォルト: full） |

### formatオプション

| 値 | 説明 |
|----|------|
| `full` | 全情報（ヘッダー、本文、添付ファイル） |
| `minimal` | ID、スレッドID、ラベルのみ |
| `metadata` | ヘッダーのみ（本文なし） |
| `raw` | RFC2822形式の生データ |

### JSON出力構造（format=full）

```json
{
  "id": "18abc123def456",
  "thread_id": "18abc123def000",
  "date": "Fri, 17 Jan 2025 10:30:00 +0900",
  "from": "sender@example.com",
  "to": "recipient@example.com",
  "subject": "件名",
  "labels": ["INBOX", "UNREAD"],
  "body": {
    "plain_text": "本文テキスト...",
    "html": "<html>...</html>"
  },
  "attachments": [
    {
      "filename": "document.pdf",
      "mime_type": "application/pdf",
      "size": 123456
    }
  ]
}
```

---

## Authenticator (gmail_authenticator.rb)

### 引数

引数なし。実行すると対話型のOAuth認証フローを開始。

### 認証ファイル

| ファイル | 説明 |
|----------|------|
| `~/.credentials/gmail-readonly-token.yaml` | 読み取り専用トークン |

### 必要な環境変数

| 環境変数 | 説明 |
|----------|------|
| `GOOGLE_CLIENT_ID` | OAuth 2.0クライアントID |
| `GOOGLE_CLIENT_SECRET` | OAuth 2.0クライアントシークレット |

---

## Gmail検索クエリ演算子リファレンス

### 送信者・宛先

| 演算子 | 説明 | 例 |
|--------|------|-----|
| `from:` | 送信者 | `from:amazon.co.jp` |
| `to:` | 宛先 | `to:user@example.com` |
| `cc:` | CC | `cc:team@example.com` |
| `bcc:` | BCC | `bcc:backup@example.com` |

### 件名・内容

| 演算子 | 説明 | 例 |
|--------|------|-----|
| `subject:` | 件名に含む | `subject:請求書` |
| `"完全一致"` | フレーズ検索 | `"注文確認"` |
| `OR` | OR検索 | `from:amazon OR from:rakuten` |
| `-` | 除外 | `-from:noreply` |

### 日付

| 演算子 | 説明 | 例 |
|--------|------|-----|
| `after:` | 指定日以降 | `after:2025/01/01` |
| `before:` | 指定日以前 | `before:2025/12/31` |
| `newer_than:` | 相対日（新しい） | `newer_than:7d`, `newer_than:1m` |
| `older_than:` | 相対日（古い） | `older_than:1y` |

**相対日の単位**: `d`（日）、`m`（月）、`y`（年）

### 添付ファイル

| 演算子 | 説明 | 例 |
|--------|------|-----|
| `has:attachment` | 添付あり | `has:attachment` |
| `filename:` | ファイル名/拡張子 | `filename:pdf`, `filename:report.xlsx` |

### ラベル・状態

| 演算子 | 説明 | 例 |
|--------|------|-----|
| `label:` | ラベル | `label:work` |
| `is:unread` | 未読 | `is:unread` |
| `is:read` | 既読 | `is:read` |
| `is:starred` | スター付き | `is:starred` |
| `is:important` | 重要 | `is:important` |
| `in:inbox` | 受信トレイ | `in:inbox` |
| `in:sent` | 送信済み | `in:sent` |
| `in:trash` | ゴミ箱 | `in:trash` |
| `in:spam` | 迷惑メール | `in:spam` |

### カテゴリ

| 演算子 | 説明 |
|--------|------|
| `category:primary` | メイン |
| `category:social` | ソーシャル |
| `category:promotions` | プロモーション |
| `category:updates` | 新着 |
| `category:forums` | フォーラム |

---

## ラベル名の日本語変換

| ラベルID | 日本語表示 |
|----------|-----------|
| `INBOX` | 受信トレイ |
| `SENT` | 送信済み |
| `DRAFT` | 下書き |
| `TRASH` | ゴミ箱 |
| `SPAM` | 迷惑メール |
| `UNREAD` | 未読 |
| `STARRED` | スター付き |
| `IMPORTANT` | 重要 |
| `CATEGORY_PERSONAL` | メイン |
| `CATEGORY_SOCIAL` | ソーシャル |
| `CATEGORY_PROMOTIONS` | プロモーション |
| `CATEGORY_UPDATES` | 新着 |
| `CATEGORY_FORUMS` | フォーラム |

---

## 日付変換ルール

### 自然言語 → Gmail検索クエリ

| 入力 | 変換ロジック | 例（現在: 2025-01-17） |
|------|-------------|----------------------|
| 今日 | `after:YYYY/MM/DD before:YYYY/MM/DD+1` | `after:2025/01/17 before:2025/01/18` |
| 昨日 | `after:YYYY/MM/DD-1 before:YYYY/MM/DD` | `after:2025/01/16 before:2025/01/17` |
| 今週 | `newer_than:7d` | `newer_than:7d` |
| 先週 | `older_than:7d newer_than:14d` | 複合クエリ |
| 今月 | `newer_than:1m` | `newer_than:1m` |
| 先月 | `older_than:1m newer_than:2m` | 複合クエリ |
| 今年 | `after:YYYY/01/01` | `after:2025/01/01` |
| N日前から | `newer_than:Nd` | `newer_than:3d` |

### RFC2822 → YYYY-MM-DD HH:MM変換

入力例: `Fri, 17 Jan 2025 10:30:00 +0900`
出力: `2025-01-17 10:30`

---

## エラーハンドリング

### エラーJSON構造

```json
{
  "error": "エラーメッセージ"
}
```

### エラー種別と対処

| エラーメッセージ | 原因 | 対処 |
|-----------------|------|------|
| `No credentials found` | 初回認証未実施 | authenticator実行 |
| `invalid_grant` | トークン期限切れ | トークン削除後、authenticator再実行 |
| `GOOGLE_CLIENT_ID is not set` | 環境変数未設定 | mise.local.toml確認 |
| `Error: --query is required` | 必須引数不足 | クエリを指定 |
| `Invalid format` | 不正なformat値 | full/minimal/metadata/rawから選択 |

---

## サイズ表示の変換

添付ファイルサイズ（バイト）を人間が読みやすい形式に変換:

| バイト数 | 表示 |
|----------|------|
| < 1024 | `N B` |
| < 1024^2 | `N.N KB` |
| < 1024^3 | `N.N MB` |
| >= 1024^3 | `N.N GB` |

---

## トラブルシューティング

| 問題 | 原因 | 対処 |
|------|------|------|
| 検索結果が0件 | クエリが厳しすぎる | 条件を緩和、演算子を確認 |
| 本文が空 | HTMLのみのメール | `has_html: true`を確認 |
| 文字化け | エンコーディング問題 | UTF-8強制変換済みだが、まれに発生 |
| タイムアウト | 結果が多すぎる | `--max-results`を減らす、`--no-body`を使用 |
