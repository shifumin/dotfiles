---
description: Googleカレンダーの予定を一覧表示
---

# list-calendar-events

Rubyスクリプト（google_calendar_fetcher.rb）を使用してGoogleカレンダーから予定を取得し、一覧表示します。

## 使用方法

### 引数
- **引数なし** → 今日の予定を表示（デフォルト）
- `明日` → 明日の予定を表示
- `明後日` → 明後日の予定を表示
- `YYYY-MM-DD` → 指定日の予定を表示（例: 2025-11-16）

### コマンド例
```
/list-calendar-events                    # 今日
/list-calendar-events 明日               # 明日
/list-calendar-events 明後日             # 明後日
/list-calendar-events 2025-11-16         # 日付指定（YYYY-MM-DD形式）
```

### 出力例

```markdown
## 2025-11-16 の予定

- [終日] 評価会議期間（25下期中間）【仕事】
- [終日] 第11回東京エクストリームウォーク100【しふみん】
- 10:00-20:00 🗼東京散歩【しふみん】
- 10:00-13:00 洗濯【しふみん】
- 10:30-11:00 デイリースクラム【仕事】
- 12:00-13:00 昼休憩【仕事】
- 13:00-15:00 Gin PBR【仕事】
- 19:30-21:00 アリオ市原買い物【しふみん】
- 20:30-21:00 フェリエ【私用】
```

## カレンダー設定

以下の3つのGoogleカレンダーから予定を取得します：

| Calendar ID | カレンダー名 | 表記 | 用途 |
|---|---|---|---|
| `work@example.com` | `work@example.com` | `【仕事】` | 仕事用 |
| `personal@group.calendar.google.com` | `しふみん` | `【しふみん】` | 個人用 |
| `private@example.com` | `Private Calendar` | `【私用】` | 個人用2 |

## 処理手順

1. **引数の解析**
   - 日付引数（今日/明日/明後日/YYYY-MM-DD）を解析
   - 対象日付をYYYY-MM-DD形式で決定
   - 引数マッピング:
     - 引数なし → 引数なし（今日）
     - `明日` → `tomorrow`
     - `明後日` → 日付計算（YYYY-MM-DD形式）
     - `YYYY-MM-DD` → そのまま

2. **Rubyスクリプトで予定を取得**
   - `Bash`ツールで以下のコマンドを実行:
     ```bash
     mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_fetcher.rb [date_arg]
     ```
   - JSON形式でレスポンスを取得

3. **JSON出力の構造**
   ```json
   {
     "date": "2025-01-15",
     "calendars": [
       {
         "id": "calendar@example.com",
         "summary": "Calendar Name",
         "events": [
           {
             "id": "event_id",
             "summary": "Event Name",
             "description": "...",
             "start": { "date_time": "2025-01-15T10:00:00+09:00", "date": null },
             "end": { "date_time": "2025-01-15T11:00:00+09:00", "date": null },
             "event_type": "default"
           }
         ]
       }
     ]
   }
   ```

4. **予定データの整形**
   - **除外処理**: `event_type`が`workingLocation`の予定は除外する
   - 各予定について以下の処理を実行：
     - **時刻フォーマット**:
       - `start.date`が存在する場合: 終日予定 → `[終日]`
       - `start.date_time`が存在する場合: 時間指定予定 → `HH:MM-HH:MM`形式に変換
     - **複数日にまたがる予定の処理**:
       - 前日から継続中の予定: 対象日の00:00を開始時刻として表示
         - 例: 11/14 10:00 - 11/16 10:30 → `00:00-10:30 予定名【カレンダー名】`
       - 当日開始で翌日以降に終了: 対象日の23:59を終了時刻として表示
         - 例: 11/16 10:00 - 11/18 12:00 → `10:00-23:59 予定名【カレンダー名】`
       - 対象日を完全に含む長期予定: `00:00-23:59 予定名【カレンダー名】`
     - **カレンダー名の判定**:
       - `id`が`work@example.com` → `【仕事】`
       - `id`が`personal@group.calendar.google.com` → `【しふみん】`
       - `id`が`private@example.com` → `【私用】`
       - 上記以外のカレンダーID → `【不明】`
     - **予定名のクリーンアップ**:
       - 末尾の不要な記号（✔︎、！、✓など）を除去
       - 予定名が空の場合: `(タイトルなし)`として記載
       - 絵文字を含む予定名: そのまま記載（除去しない）
   - **並び順ロジック**:
     1. 終日予定（`start.date`が存在）を先頭グループに配置
        - 終日予定内では取得順（APIレスポンスの順序を維持）
     2. 時間指定予定（`start.date_time`が存在）を次グループに配置
        - 開始時刻の昇順でソート（早い時刻が上）
        - 同時刻の場合は取得順

5. **予定を出力**
   - 整形した予定一覧をコンソールに出力
   - **出力形式**:
     ```markdown
     ## YYYY-MM-DD の予定

     - [終日] 予定名【カレンダー名】
     - HH:MM-HH:MM 予定名【カレンダー名】
     ```
   - **注意**: ファイルへの書き込みは行わない（表示のみ）

## データ処理ルール

### 予定の記載形式

- **終日の予定**: `- [終日] 予定名【カレンダー名】`
- **時間指定の予定**: `- HH:MM-HH:MM 予定名【カレンダー名】`

### 並び順

1. 終日予定（`start.date`が存在）を先頭グループに配置
   - 終日予定内では取得順（APIレスポンスの順序を維持）
2. 時間指定予定（`start.date_time`が存在）を次グループに配置
   - 開始時刻の昇順でソート（早い時刻が上）
   - 同時刻の場合は取得順

### 時刻フォーマット

- 24時間形式（例: `10:30-11:00`, `13:00-13:45`）
- 分は2桁表示（例: `09:00`, `13:05`）
- ISO 8601形式のタイムスタンプ（例: `2025-11-16T10:00:00+09:00`）から時刻部分を抽出

### 除外する予定

- **勤務場所イベント**: `event_type`が`workingLocation`の予定（例: 「自宅」「オフィス」など）

### 除外する情報

- **予定名末尾の記号**: ✔︎、！、✓など
- **場所情報**: 出力しない
- **ステータス情報**: APIから取得されるが出力しない

### 重複予定の扱い

- 同じ予定が複数のカレンダーに表示されている場合でも、それぞれカレンダー名を付けて記載

### エッジケース

- **予定が0件の場合**: 「予定はありません」と表示
- **不明なカレンダーIDの予定**: `【不明】`として記載（エラーにしない）
- **予定名が空の場合**: `(タイトルなし)`として記載
- **絵文字を含む予定名**: そのまま記載（除去しない）
- **複数日にまたがる予定**: 対象日の00:00や23:59を使用して時刻範囲を表示

## 注意事項

- **認証**: Rubyスクリプトの認証が事前に設定済みであること（`~/.credentials/calendar-fetcher-token.yaml`が存在）
- **環境変数**: `mise.local.toml`にカレンダーIDとOAuth認証情報が設定されていること
- **読み取り専用**: このコマンドはファイルへの書き込みを行わない（表示のみ）

## トラブルシューティング

| 問題 | 原因 | 対処方法 |
|---|---|---|
| Rubyスクリプトエラー | 認証トークンの期限切れ | `ruby google_calendar_authenticator.rb`を再実行して認証 |
| カレンダーにアクセスできない | 環境変数未設定 | `mise.local.toml`にGOOGLE_CALENDAR_IDS等を設定 |
| 日付引数エラー | 形式不正 | `YYYY-MM-DD`形式で指定（例: 2025-11-16） |
| 予定が取得できない | カレンダーIDが間違っている | `mise.local.toml`のGOOGLE_CALENDAR_IDSを確認 |
| JSONパースエラー | スクリプト実行エラー | Bashツールの出力でエラーメッセージを確認 |

## 技術仕様

### Rubyスクリプト

- **パス**: `~/ghq/github.com/shifumin/google-calendar-tools-ruby/google_calendar_fetcher.rb`
- **実行コマンド**: `mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_fetcher.rb [date_arg]`
- **日付引数**:
  - 引数なし: 今日
  - `y`, `yesterday`, `昨日`: 昨日
  - `t`, `tomorrow`, `明日`: 明日
  - `YYYY-MM-DD`: 指定日

### JSON出力例

```json
{
  "date": "2025-11-16",
  "calendars": [
    {
      "id": "work@example.com",
      "summary": "work@example.com",
      "description": null,
      "timezone": "Asia/Tokyo",
      "events": [
        {
          "id": "event_id",
          "summary": "ミーティング",
          "description": null,
          "start": {
            "date_time": "2025-11-16T10:30:00+09:00",
            "date": null
          },
          "end": {
            "date_time": "2025-11-16T11:00:00+09:00",
            "date": null
          },
          "event_type": "default"
        }
      ]
    },
    {
      "id": "personal@group.calendar.google.com",
      "summary": "しふみん",
      "description": null,
      "timezone": "Asia/Tokyo",
      "events": [
        {
          "id": "event_id_2",
          "summary": "終日イベント",
          "description": null,
          "start": {
            "date_time": null,
            "date": "2025-11-16"
          },
          "end": {
            "date_time": null,
            "date": "2025-11-17"
          },
          "event_type": "default"
        }
      ]
    }
  ]
}
```

### 時刻変換ロジック

- `start.date_time`が`2025-11-16T10:30:00+09:00`の場合 → `10:30`を抽出
- `end.date_time`が`2025-11-16T11:00:00+09:00`の場合 → `11:00`を抽出
- 結果: `10:30-11:00`

## 実行の流れ（例）

### ケース1: 引数なしで実行
```bash
/list-calendar-events
```
→ 今日（2025-11-16）の予定を表示

### ケース2: 明日を指定
```bash
/list-calendar-events 明日
```
→ 明日（2025-11-17）の予定を表示

### ケース3: 日付を直接指定
```bash
/list-calendar-events 2025-12-25
```
→ 2025年12月25日の予定を表示
