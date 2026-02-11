# Gmail技術仕様

SKILL.mdから参照される技術仕様。引数・実行方法はSKILL.mdを参照。

## 目次

1. Searcher JSON出力構造
2. Fetcher
3. Spam Trasher
4. Authenticator
5. ラベル名の日本語変換
6. 日付変換ルール
7. エラーハンドリング
8. トラブルシューティング

---

## Searcher JSON出力構造

デフォルト:
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

`--include-html`使用時:
```json
{
  "body": {
    "plain_text": "本文テキスト...",
    "html": "<html>...</html>"
  }
}
```

---

## Fetcher

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

## Spam Trasher (gmail_spam_trasher.rb)

### 引数

| オプション | 必須 | デフォルト | 説明 |
|-----------|:----:|-----------|------|
| `--max-results=N` | No | 500 | 処理する最大スパムメッセージ数 |
| `--dry-run` | No | - | プレビューのみ（ゴミ箱に移動しない） |
| `--batch-size=N` | No | 100 | バッチあたりのメッセージ数（最大: 100） |

### 認証

| 項目 | 値 |
|------|-----|
| スコープ | `gmail.modify` |
| トークンファイル | `~/.credentials/gmail-modify-token.yaml` |
| 認証コマンド | `ruby gmail_authenticator.rb --scope=modify` |

### JSON出力構造

dry-run時:
```json
{
  "dry_run": true,
  "spam_count": 42,
  "message_ids": ["18abc123def456", "18abc789ghi012"]
}
```

実行成功時:
```json
{
  "spam_count": 42,
  "trashed_count": 42,
  "failed_batches": [],
  "success": true
}
```

スパムなし:
```json
{
  "spam_count": 0,
  "message": "No spam messages found."
}
```

一部失敗時:
```json
{
  "spam_count": 42,
  "trashed_count": 30,
  "failed_batches": [
    {
      "batch_index": 0,
      "size": 12,
      "error": "Rate limit exceeded"
    }
  ],
  "success": false
}
```

---

## Authenticator (gmail_authenticator.rb)

### 引数

| オプション | 必須 | デフォルト | 説明 |
|-----------|:----:|-----------|------|
| `--scope` | No | `readonly` | OAuthスコープ: `readonly` または `modify` |

### 認証ファイル

| スコープ | ファイル | 説明 |
|----------|---------|------|
| `readonly` | `~/.credentials/gmail-readonly-token.yaml` | 読み取り専用トークン（検索・取得用） |
| `modify` | `~/.credentials/gmail-modify-token.yaml` | 変更権限トークン（スパム削除用） |

### 必要な環境変数

| 環境変数 | 説明 |
|----------|------|
| `GOOGLE_CLIENT_ID` | OAuth 2.0クライアントID |
| `GOOGLE_CLIENT_SECRET` | OAuth 2.0クライアントシークレット |

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
| `No credentials found...--scope=modify` | modifyスコープ未認証 | `ruby gmail_authenticator.rb --scope=modify`を実行 |
| `invalid_grant` | トークン期限切れ | トークン削除後、authenticator再実行 |
| `GOOGLE_CLIENT_ID is not set` | 環境変数未設定 | mise.local.toml確認 |
| `Error: --query is required` | 必須引数不足 | クエリを指定 |
| `Invalid format` | 不正なformat値 | full/minimal/metadata/rawから選択 |

再認証コマンドはSKILL.mdの「認証エラー時」セクションを参照。

---

## トラブルシューティング

| 問題 | 原因 | 対処 |
|------|------|------|
| 検索結果が0件 | クエリが厳しすぎる | 条件を緩和、演算子を確認 |
| スパム検索が0件 | `--include-spam-trash`未指定 | 検索時に`--include-spam-trash`を必ず指定 |
| スパム削除がエラー | modifyトークン未認証 | `ruby gmail_authenticator.rb --scope=modify`で認証 |
| 本文が空 | HTMLのみのメール | `has_html: true`を確認 |
| 文字化け | エンコーディング問題 | UTF-8強制変換済みだが、まれに発生 |
| タイムアウト | 結果が多すぎる | `--max-results`を減らす、`--no-body`を使用 |
