Google Calendarの予定を削除します。

ARGUMENTS: $ARGUMENTS

## 処理手順

1. ユーザーの入力から以下の情報を解釈する:
   - タイトル（キーワード）: 必須
   - 日付: 任意（指定がなければ今日）

2. 日付の解釈ルール:
   - 「今日」「明日」「昨日」などの相対表現を絶対日付に変換
   - 「12/5」「2025-01-15」などの日付表現を解釈
   - 指定がない場合は今日の日付を使用

3. fetcherを使ってイベント一覧を取得:
   ```bash
   mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_fetcher.rb <日付>
   ```

4. 取得したイベントからタイトルがキーワードに部分一致するものを抽出

5. マッチ結果に応じて処理を分岐:
   - **0件**: 該当するイベントが見つからない旨を伝えて終了
   - **1件**: そのイベントの情報を表示し、削除してよいか確認
   - **複数件**: AskUserQuestionツールで削除対象を選択させる（イベントのタイトルと時刻を表示）

6. ユーザーの確認後、deleterを実行:
   ```bash
   mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_deleter.rb --event-id='<イベントID>'
   ```

7. 実行結果をユーザーにわかりやすく伝える

## 入力例と解釈

| 入力 | キーワード | 日付 |
|------|-----------|------|
| 歯医者 | 歯医者 | 今日 |
| 明日の会議 | 会議 | 明日 |
| 12/5 定例 | 定例 | 12/5 |
| 昨日のランチ | ランチ | 昨日 |

## 注意事項

- 削除は取り消せないため、必ずユーザーに確認してから実行する
- 認証トークンが存在しない場合のエラーが出たら、先に `mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_authenticator.rb --mode=readwrite` の実行が必要と伝える
- イベントの特定には大文字・小文字を区別しない部分一致を使用する
