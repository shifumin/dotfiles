# CLAUDE.md

このドキュメントは、Claude Codeを使用する際の必須ガイドラインです。以下の指示に必ず従ってください。

## 🚨 重要な原則

1. **既存のコードスタイルを厳守する** - プロジェクトの規約から逸脱しない
2. **プロジェクトのツールを使用する** - 新しいツールやフレームワークを勝手に導入しない
3. **コミット前の必須チェック** - リンターとテストを必ず実行する
4. **テストの同期** - 実装を追加・変更した場合は、対応するテストも必ず追加・変更する
5. **ドキュメントの更新** - 必要に応じてREADME.mdとCLAUDE.mdを更新する
   - **README.mdは英語で記述する** - プロジェクトの国際的な利用を考慮し、README.mdは英語で書く
6. **CLAUDE.mdへの記載形式** - CLAUDE.mdに内容を追加する際は、Claude Codeが理解しやすい明確で構造化された形式で記載する
7. **要件や仕様に疑問があれば必ず立ち止まって質問する** - 実装方法や要件・仕様に疑問が生じた場合は、必ず作業を中断してユーザーに確認する

## 💡 コード品質ガイドライン

### クリーンコードの原則
- **変数名・関数名は意図を明確に** - 読み手が推測せずに理解できる名前を使用する
- **関数・メソッドは単一責任の原則（Single Responsibility Principle）に則る** - 1つの関数は1つの責任のみを持つ
- **複雑なロジックには説明を追加する** - コメントやドキュメンテーションで意図を明確にする
- **必要な場合は早期returnを利用する** - ネストを深くせず、読みやすいコードを心がける
- **エラーメッセージは明確にする** - 何が問題で、どう解決すべきかを示す
- **マジックナンバーは避ける** - 定数や設定値として意味のある名前を付ける

### メソッドの可視性
- **publicインターフェースの明確化** - ヘルパーメソッドはprivateにし、必要最小限のpublicメソッドのみを公開

### ファイル命名規則
- **無効な文字の処理** - ファイル名に使用できない文字（`/`, `:`, `*`, `?`, `"`, `<`, `>`, `|`）は `_` に置換
- **意味のある命名** - ファイルの内容が推測できる名前を使用
- **一貫性のある形式** - プロジェクト全体で統一された命名パターンを維持

### テスト作成の原則
- **必要十分なテストを作成** - 過剰なテストは避け、本質的なケースをカバーする
- **正常系・異常系・エッジケースを網羅** - 期待される動作だけでなく、例外処理やエッジケースもテスト
- **publicインターフェースのみテスト** - privateメソッドの直接テストは禁止

## 🔄 標準ワークフロー

### 作業開始前
- README.mdを読んでプロジェクトの概要を理解
- 既存のコードパターンとツールを確認
- テストの実行方法を確認

### 実装中
- 既存パターンに従って実装
- エラーハンドリングを実装
- テストを同時に作成・更新
- 実装変更後は必ずテストを実行

### 作業完了前
- リンターとテストを実行
- 変更内容を確認（git diff）

## 📄 ファイル操作

- 日本語ファイルはUTF-8で保存
- 編集前に必ず`Read`ツールでファイルを読み込む
- 新規ファイル作成は`Write`ツールを使用

## 🔐 セキュリティ

**コミット前に以下が含まれていないか確認**:
- APIキー、トークン、パスワード
- 公開を意図しない個人情報
- 内部URL、秘密鍵、証明書
- 本番環境の接続情報

`git diff --staged`で確認し、秘匿情報が含まれている場合は即座にユーザーに報告。

## 🛡️ カスタムコマンド

~/.claude/commands/に以下のカスタムコマンドが定義されています：

### 基本コマンド
- **finish** - リンターとテストを実行し、必要に応じてドキュメントを更新
- **push** - 変更内容を適切な粒度でcommit/push
- **rubocop** - Rubyのリンター実行

### リファクタリング・更新コマンド
- **check-srp** - 単一責任の原則（SRP）違反をチェックしてリファクタリング
- **check-performance** - パフォーマンス改善点をチェック
- **update-test** - テストを必要十分な状態に調整
- **update-document** - CLAUDE.md/README.mdを更新
- **update-claude-md** - CLAUDE.mdに内容を追加

### GitHub連携コマンド
- **create-github-repo** - GitHubリポジトリを作成
- **review-pr** - プルリクエストをレビュー
- **review-pr-comment** - PRコメントを確認

### カレンダーコマンド
- **list-calendar-events** - カレンダーの予定を一覧表示
- **create-calendar-event** - カレンダーに予定を作成
- **update-calendar-event** - カレンダーの予定を更新
- **delete-calendar-event** - カレンダーの予定を削除

### その他
- **multi-llm-search** - 複数LLMで同時検索
- **notebooklm-upload** - NotebookLMに音声概要を作成

## 🐙 GitHub連携

GitHubのURL参照やプルリクエスト操作は必ず`gh`コマンドを使用。

**重要原則**:
- GitHubのURLを直接参照しない（404エラーの原因）
- WebFetch toolでのGitHub URLアクセスは禁止
- 必ず`gh`コマンドを使用
- エラー時は`gh auth status`で認証確認

### PR情報取得（URLが提供された場合）
```bash
# 基本情報
gh pr view <PR番号> --repo <owner/repo> --json title,body,state,author,url,headRefName,baseRefName

# ファイル変更情報
gh pr view <PR番号> --repo <owner/repo> --json files,additions,deletions,changedFiles

# 差分
gh pr diff <PR番号> --repo <owner/repo>
```

### その他のコマンド
```bash
gh pr list                    # PR一覧
gh pr create --title "" --body ""  # PR作成
gh issue list                 # Issue一覧
gh issue view [番号]           # Issue詳細
gh api repos/[owner]/[repo]/pulls/[番号]/comments  # PRコメント
```

## 📅 Google Calendar連携

ユーザーがカレンダーの予定に関する操作をリクエストした場合、以下のRubyスクリプトを使用して自動的に処理する。スラッシュコマンドの明示的な呼び出しは不要。

### 対応する操作とキーワード例

| 操作 | トリガーとなる表現例 |
|------|---------------------|
| 予定取得 | 「今日の予定」「明日のスケジュール」「12/5の予定を教えて」 |
| 予定作成 | 「予定を作成」「〜を登録」「カレンダーに追加」 |
| 予定更新 | 「予定を変更」「時間を〜に変更」「〜を更新」 |
| 予定削除 | 「予定を削除」「〜をキャンセル」「予定を消して」 |

### スクリプトパスと実行方法

すべてのスクリプトは以下のディレクトリに配置:
`~/ghq/github.com/shifumin/google-calendar-tools-ruby/`

実行時は必ず`mise exec`を使用:
```bash
mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby <script_name>.rb [options]
```

### 予定取得（google_calendar_fetcher.rb）

```bash
mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_fetcher.rb [date_arg]
```

- **引数**: 日付（`tomorrow`, `YYYY-MM-DD`形式、または引数なしで今日）
- **出力**: JSON形式（カレンダーごとのイベント情報）
- **表示形式**:
  - 終日予定: `[終日] 予定名【カレンダー名】`
  - 時間指定: `HH:MM-HH:MM 予定名【カレンダー名】`
- **カレンダー名マッピング**:
  - `work@example.com` → `【仕事】`
  - `d05uihnd5h2o08hohn57q6k940@group.calendar.google.com` → `【しふみん】`
  - `shifumin4230@gmail.com` → `【私用】`

### 予定作成（google_calendar_creator.rb）

```bash
mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_creator.rb --summary='<タイトル>' --start='<開始日時>' --end='<終了日時>' [--description='<説明>'] [--calendar='<カレンダーID>']
```

- **必須情報**: タイトル、開始日時
- **日時形式**: ISO8601（例: 2025-12-01T19:00:00）
- **終了日時省略時**: 開始時刻から30分後
- **デフォルトカレンダー**: しふみん（`d05uihnd5h2o08hohn57q6k940@group.calendar.google.com`）
- **実行前に必ずユーザーに確認する**

### 予定更新（google_calendar_updater.rb）

```bash
mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_updater.rb --event-id='<イベントID>' [--summary='<新タイトル>'] [--start='<新開始日時>'] [--end='<新終了日時>'] [--description='<新説明>'] [--location='<新場所>']
```

- **処理フロー**:
  1. fetcherでイベント一覧を取得
  2. キーワードで対象イベントを特定
  3. 0件: 該当なしを通知、1件: 確認後更新、複数件: 選択を求める
  4. 更新前後の内容をユーザーに確認してから実行

### 予定削除（google_calendar_deleter.rb）

```bash
mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_deleter.rb --event-id='<イベントID>'
```

- **処理フロー**:
  1. fetcherでイベント一覧を取得
  2. キーワードで対象イベントを特定
  3. 0件: 該当なしを通知、1件: 確認後削除、複数件: 選択を求める
  4. **削除は取り消せないため、必ずユーザーに確認してから実行**

### 認証エラー時

認証トークンエラーが発生した場合、以下のコマンドの実行を案内:
```bash
mise exec --cd ~/ghq/github.com/shifumin/google-calendar-tools-ruby -- ruby google_calendar_authenticator.rb --mode=readwrite
```

## 📝 プロジェクト固有の設定

プロジェクト固有の追加情報がある場合は、以下に記載してください：

---

**注意**: このドキュメントの指示は、デフォルトの動作よりも優先されます。必ず従ってください。
