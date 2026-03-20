# Gmail技術仕様

SKILL.mdから参照される技術仕様。引数・実行方法はSKILL.mdを参照。

## 目次

1. +triage JSON出力構造
2. messages get（Gmail API生レスポンス）
3. messages list
4. messages batchModify
5. messages trash
6. 認証
7. ラベル名の日本語変換
8. 日付変換ルール
9. エラーハンドリング
10. トラブルシューティング

---

## +triage JSON出力構造

```json
{
  "messages": [
    {
      "date": "Sat, 14 Mar 2026 12:32:57 +0000",
      "from": "connpass <no-reply@connpass.com>",
      "id": "19cec55e4828cdf7",
      "subject": "イベント名 に資料が追加されました。"
    }
  ],
  "query": "is:unread",
  "resultSizeEstimate": 5
}
```

### オプション

| オプション | 説明 |
|-----------|------|
| `--query` | Gmail検索クエリ（デフォルト: `is:unread`） |
| `--max` | 最大件数（デフォルト: 20） |
| `--format` | 出力形式: json / table / yaml / csv |
| `--labels` | ラベル名を出力に含める |

特徴:
- **概要情報のみ**: id, from, subject, dateを返す（本文なし）
- **クエリ対応**: `--query` で任意のGmail検索クエリを受け付ける
- **スパム非対応**: `includeSpamTrash` オプションなし。スパム検索は `messages list` を使う

---

## messages get（Gmail API生レスポンス）

```json
{
  "id": "19cebb41f895b906",
  "threadId": "19cebb41f895b906",
  "labelIds": ["CATEGORY_PROMOTIONS", "UNREAD", "IMPORTANT"],
  "payload": {
    "headers": [
      {"name": "Date", "value": "Sat, 14 Mar 2026 09:36:15 +0000"},
      {"name": "From", "value": "\"Amazon.co.jp\" <store-news@amazon.co.jp>"},
      {"name": "To", "value": "shifumin4230@gmail.com"},
      {"name": "Subject", "value": "件名"}
    ],
    "mimeType": "multipart/alternative",
    "parts": [
      {
        "mimeType": "text/plain",
        "body": {
          "size": 1234,
          "data": "Base64エンコードされた本文..."
        }
      },
      {
        "mimeType": "text/html",
        "body": {
          "size": 5678,
          "data": "Base64エンコードされたHTML..."
        }
      }
    ]
  }
}
```

### ヘッダーからの情報抽出

| 表示項目 | ヘッダー名 |
|---------|-----------|
| 件名 | `Subject` |
| From | `From` |
| To | `To` |
| 日付 | `Date` |

### 本文の取得方法

1. `payload.parts` から `mimeType: "text/plain"` のパートを探す
2. `body.data` をBase64デコード（URL-safe Base64）
3. plain_textが空の場合は `mimeType: "text/html"` を使用

### 添付ファイルの確認

`payload.parts` 内で `filename` が空でないパートが添付ファイル:

```json
{
  "mimeType": "application/pdf",
  "filename": "document.pdf",
  "body": {
    "size": 123456,
    "attachmentId": "..."
  }
}
```

---

## messages list

```bash
gws gmail users messages list --params '{"userId":"me","q":"<検索クエリ>","maxResults":50}' --format json
```

```json
{
  "messages": [
    {
      "id": "19cebb41f895b906",
      "threadId": "19cebb41f895b906"
    }
  ],
  "nextPageToken": "...",
  "resultSizeEstimate": 201
}
```

- ID + threadID のみ返す。詳細は `messages get` で取得
- `--page-all` で自動ページング可能
- `includeSpamTrash:true` でスパム・ゴミ箱のメールも対象

---

## messages batchModify

### リクエスト

```bash
gws gmail users messages batchModify --json '{"ids":["id1","id2","id3"],"removeLabelIds":["INBOX","UNREAD"]}'
```

### パラメータ

| フィールド | 必須 | 説明 |
|-----------|------|------|
| `ids` | Yes | メッセージIDの配列 |
| `addLabelIds` | No | 追加するラベルID |
| `removeLabelIds` | No | 削除するラベルID |

`addLabelIds` と `removeLabelIds` の少なくとも一方は必須。

### レスポンス

成功時は空レスポンス（204 No Content相当）。

---

## messages trash

### リクエスト

```bash
gws gmail users messages trash --params '{"userId":"me","id":"<message_id>"}'
```

### レスポンス

ゴミ箱に移動されたメッセージオブジェクトが返る。

---

## 認証

### ログイン

```bash
gws auth login -s gmail
```

### 状態確認

```bash
gws auth status
```

`token_valid: true` であれば認証済み。scopesに `gmail.modify` が含まれていれば変更操作も可能。

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

入力例: `Sat, 14 Mar 2026 09:36:15 +0000`
出力: `2026-03-14 18:36`（UTC→JST変換）

---

## エラーハンドリング

### エラー種別と対処

| エラーメッセージ | 原因 | 対処 |
|-----------------|------|------|
| 認証関連エラー | トークン期限切れ | `gws auth login -s gmail` で再認証 |
| `400 Bad Request` | パラメータ不正 | `--params` のJSON構文を確認 |
| `404 Not Found` | メッセージID不正 | IDを再確認 |
| `429 Too Many Requests` | レートリミット | しばらく待ってリトライ |

---

## トラブルシューティング

| 問題 | 原因 | 対処 |
|------|------|------|
| 検索結果が0件 | クエリが厳しすぎる | 条件を緩和、演算子を確認 |
| スパム検索が0件 | `+triage`を使用している | `messages list` with `includeSpamTrash:true` を使う |
| 本文が空 | Base64デコードしていない | `payload.parts[].body.data` をBase64デコード |
| 文字化け | エンコーディング問題 | Base64デコード後にUTF-8として解釈 |
| batchModifyが失敗 | IDが多すぎる | IDを分割して複数回実行（1回あたり100件まで推奨） |
