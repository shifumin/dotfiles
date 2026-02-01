# Googleカレンダー技術仕様

統合スキル `~/.claude/skills/google-calendar/SKILL.md` から参照される技術仕様。

## スクリプト一覧

| スクリプト | 用途 |
|-----------|------|
| google_calendar_fetcher.rb | 予定取得 |
| google_calendar_creator.rb | 予定作成 |
| google_calendar_updater.rb | 予定更新 |
| google_calendar_deleter.rb | 予定削除 |
| google_calendar_authenticator.rb | OAuth認証 |

パス: `~/ghq/github.com/shifumin/google-calendar-tools-ruby/`

---

## Fetcher (google_calendar_fetcher.rb)

### 引数

| 引数 | 説明 |
|------|------|
| (なし) | 今日 |
| `y`, `yesterday`, `昨日` | 昨日 |
| `t`, `tomorrow`, `明日` | 明日 |
| `YYYY-MM-DD` | 指定日 |

### JSON出力構造

```json
{
  "date": "2025-01-15",
  "calendars": [
    {
      "id": "calendar@example.com",
      "summary": "Calendar Name",
      "description": null,
      "timezone": "Asia/Tokyo",
      "events": [
        {
          "id": "event_id_12345",
          "summary": "イベント名",
          "description": "説明文",
          "start": {
            "date_time": "2025-01-15T10:00:00+09:00",
            "date": null
          },
          "end": {
            "date_time": "2025-01-15T11:00:00+09:00",
            "date": null
          },
          "event_type": "default"
        }
      ]
    }
  ]
}
```

### イベント種別

| event_type | 説明 | 処理 |
|------------|------|------|
| `default` | 通常イベント | 表示 |
| `workingLocation` | 勤務場所 | **除外** |

### 終日イベント vs 時間指定イベント

| タイプ | start.date | start.date_time |
|--------|-----------|-----------------|
| 終日 | `"2025-01-15"` | `null` |
| 時間指定 | `null` | `"2025-01-15T10:00:00+09:00"` |

### jqアクセスパス

JSON出力を処理する際のjqパス:

| 目的 | jqパス |
|------|--------|
| 全イベント | `.calendars[].events[]` |
| タイトルのみ | `.calendars[].events[].summary` |
| 特定カレンダーのイベント | `.calendars[] \| select(.id == "calendar_id") \| .events[]` |
| キーワード検索（大文字小文字無視） | `.calendars[].events[] \| select(.summary \| test("キーワード"; "i"))` |
| 終日イベントのみ | `.calendars[].events[] \| select(.start.date != null)` |
| 時間指定イベントのみ | `.calendars[].events[] \| select(.start.date_time != null)` |

**注意**: jqコマンドはシングルクォートで囲むこと（シェルの特殊文字解釈を防ぐため）

### 制限事項

- fetcherは**単一日付のみ対応**（2引数目は無視される）
- 日付範囲検索は、forループで各日を個別に取得して結合する

---

## Creator (google_calendar_creator.rb)

### 引数

| 引数 | 必須 | 説明 |
|------|------|------|
| `--summary` | 必須 | イベントタイトル |
| `--start` | 必須 | 開始日時（ISO8601） |
| `--end` | 任意 | 終了日時（ISO8601）。省略時は開始から30分後 |
| `--description` | 任意 | 説明文 |
| `--calendar` | 任意 | カレンダーID。省略時はデフォルト |

### 実行例

```bash
mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_creator.rb \
  --summary='定例会議' \
  --start='2025-01-15T14:00:00' \
  --end='2025-01-15T15:00:00' \
  --calendar='calendar_id@group.calendar.google.com'
```

---

## Updater (google_calendar_updater.rb)

### 引数

| 引数 | 必須 | 説明 |
|------|------|------|
| `--event-id` | 必須 | 更新対象のイベントID |
| `--summary` | 任意 | 新しいタイトル |
| `--start` | 任意 | 新しい開始日時（ISO8601） |
| `--end` | 任意 | 新しい終了日時（ISO8601） |
| `--description` | 任意 | 新しい説明文 |
| `--location` | 任意 | 新しい場所 |

### 実行例

```bash
mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_updater.rb \
  --event-id='abc123xyz' \
  --start='2025-01-15T15:00:00' \
  --end='2025-01-15T16:00:00'
```

---

## Deleter (google_calendar_deleter.rb)

### 引数

| 引数 | 必須 | 説明 |
|------|------|------|
| `--event-id` | 必須 | 削除対象のイベントID |

### 実行例

```bash
mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_deleter.rb \
  --event-id='abc123xyz'
```

---

## Authenticator (google_calendar_authenticator.rb)

### 引数

| 引数 | 説明 |
|------|------|
| `--mode=readonly` | 読み取り専用スコープ |
| `--mode=readwrite` | 読み書きスコープ |

### 認証エラー対処

トークン期限切れ時は**削除→再認証**の順で実行:

```bash
rm -f ~/.credentials/calendar-readwrite-token.yaml && mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_authenticator.rb --mode=readwrite
```

### 認証ファイル

| ファイル | 説明 |
|----------|------|
| `~/.credentials/calendar-readonly-token.yaml` | 読み取り用トークン |
| `~/.credentials/calendar-readwrite-token.yaml` | 読み書き用トークン |

---

## 出力整形ルール

### 並び順

1. 終日予定（`start.date`あり）を先頭グループ
   - 取得順を維持
2. 時間指定予定（`start.date_time`あり）を次グループ
   - 開始時刻の昇順

### 複数日にまたがる予定

| ケース | 表示 |
|--------|------|
| 前日から継続 | `00:00-HH:MM` |
| 翌日以降に終了 | `HH:MM-23:59` |
| 対象日を完全に含む | `00:00-23:59` |

### 予定名のクリーンアップ

- 末尾の記号（✔︎、！、✓など）を除去
- 空の場合: `(タイトルなし)` として表示
- 絵文字: そのまま表示

---

## トラブルシューティング

| 問題 | 原因 | 対処 |
|------|------|------|
| Rubyスクリプトエラー | 認証トークン期限切れ | authenticatorを再実行 |
| カレンダーにアクセスできない | 環境変数未設定 | `mise.local.toml` を確認 |
| 日付引数エラー | 形式不正 | YYYY-MM-DD形式で指定 |
| JSONパースエラー | スクリプト実行エラー | Bash出力でエラーメッセージ確認 |
