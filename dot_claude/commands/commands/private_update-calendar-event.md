Google Calendarの予定を更新します。

ARGUMENTS: $ARGUMENTS

## 処理手順

1. ユーザーの入力から以下の情報を解釈する:
   - **イベント特定情報**:
     - タイトル（キーワード）: 必須
     - 日付: 任意（指定がなければ今日）
   - **更新内容**:
     - summary（タイトル）: 任意
     - start_time（開始日時）: 任意
     - end_time（終了日時）: 任意
     - description（説明）: 任意
     - location（場所）: 任意

2. 日時の解釈ルール:
   - 「今日」「明日」「昨日」などの相対表現を絶対日付に変換
   - 「12/5」「2025-01-15」などの日付表現を解釈
   - 時刻のみ指定された場合は対象イベントの日付を使用
   - タイムゾーンはAsia/Tokyo
   - ISO8601形式（例: 2025-12-01T19:00:00）に変換

3. fetcherを使ってイベント一覧を取得:
   ```bash
   mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_fetcher.rb <日付>
   ```

4. 取得したイベントからタイトルがキーワードに部分一致するものを抽出

5. マッチ結果に応じて処理を分岐:
   - **0件**: 該当するイベントが見つからない旨を伝えて終了
   - **1件**: 現在の情報と更新後の情報を表示し、更新してよいか確認
   - **複数件**: AskUserQuestionツールで更新対象を選択させる（イベントのタイトルと時刻を表示）

6. ユーザーの確認後、updaterを実行:
   ```bash
   mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_updater.rb --event-id='<イベントID>' [--summary='<新タイトル>'] [--start='<新開始日時>'] [--end='<新終了日時>'] [--description='<新説明>'] [--location='<新場所>']
   ```

7. 実行結果をユーザーにわかりやすく伝える

## 入力例と解釈

| 入力 | キーワード | 日付 | 更新内容 |
|------|-----------|------|---------|
| 会議の開始時間を14時に変更 | 会議 | 今日 | start: 14:00 |
| 明日の歯医者を15時からに変更 | 歯医者 | 明日 | start: 15:00 |
| 12/5の定例会議をタイトル「週次定例」に変更 | 定例会議 | 12/5 | summary: 週次定例 |
| 打ち合わせの場所を会議室Bに変更 | 打ち合わせ | 今日 | location: 会議室B |
| ランチを12時から13時に変更 | ランチ | 今日 | start: 12:00, end: 13:00 |
| 面接のタイトルを「最終面接」に、場所を「本社5F」に変更 | 面接 | 今日 | summary: 最終面接, location: 本社5F |

## 注意事項

- 更新前に必ずユーザーに確認する（現在の値と更新後の値を並べて表示）
- 認証トークンが存在しない場合のエラーが出たら、先に `mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_authenticator.rb --mode=readwrite` の実行が必要と伝える
- イベントの特定には大文字・小文字を区別しない部分一致を使用する
- 時刻のみ指定された場合は、対象イベントの日付を維持する
- 開始時刻・終了時刻を変更する際は、終了時刻が開始時刻より後になるよう注意する
