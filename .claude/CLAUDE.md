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

## 📄 ファイル作成・編集時の注意事項

### 文字エンコーディングの扱い
**重要**: 日本語を含むファイルの作成・編集時は以下を徹底する
- **新規ファイル作成時**:
  - 空ファイルを作成する場合は`touch`コマンドを使用
  - 内容があるファイルを作成する場合は、最初に`Read`ツールで読み込んでから`Write`ツールを使用
  - 日本語を含むファイルは必ずUTF-8エンコーディングで保存
- **既存ファイル編集時**:
  - 必ず先に`Read`ツールでファイルを読み込む
  - `Edit`または`Write`ツールで編集を行う
- **文字化けが発生した場合**:
  - ファイルを再度`Read`ツールで読み込み
  - 正しい内容で`Write`ツールを使用して上書き保存

### ファイル操作のベストプラクティス
- **Writeツールの使用を優先** - `touch`コマンドで空ファイルを作成してから書き込むより、直接`Write`ツールで内容を書き込む
- **エンコーディングの確認** - 日本語ファイルの読み込み後、文字化けしていないか確認
- **段階的な編集** - 大きな変更は複数の小さな編集に分けて実行

### コミット・プッシュ前の秘匿情報確認
**重要**: コミット前に以下が含まれていないか確認
- APIキー、トークン、パスワード
- 公開を意図しない個人情報
- 内部URL、秘密鍵、証明書
- 本番環境の接続情報

`git diff --staged`で確認し、秘匿情報が含まれている場合は即座にユーザーに報告。




## 📊 GitHub PR参照方法

### GitHub PRのURLが提供された場合
- **必ず`gh`コマンドを使用してPR情報を取得する** - 直接URLにアクセスせず、GitHub CLIを使用
- 以下のコマンドを順番に実行してPR情報を網羅的に取得:
  1. `gh pr view <PR番号> --repo <オーナー/リポジトリ名> --json title,body,state,author,createdAt,url,headRefName,baseRefName`
  2. `gh pr view <PR番号> --repo <オーナー/リポジトリ名> --json files,additions,deletions,changedFiles`
  3. `gh pr diff <PR番号> --repo <オーナー/リポジトリ名>`
- PR情報を取得できない場合は、プライベートリポジトリか認証の問題である可能性を説明

## 🔧 トラブルシューティング

### 一般的なデバッグのヒント
- verbose/debugフラグを活用して詳細情報を確認
- dry-runオプションで変更内容をプレビュー
- ログファイルやエラー出力を確認

### テスト失敗時
特定のテストのみ実行して原因を特定

### リンターエラー時
自動修正オプションを試みる

### 依存関係エラー時
パッケージマネージャーで依存関係をインストール

## 🛡️ Claude Codeカスタムコマンド

~/.claude/commands/に以下のカスタムコマンドが定義されています：

### 基本コマンド
- **finish** - リンターとテストを実行し、必要に応じてドキュメントを更新
- **push** - 変更内容を適切な粒度でcommit/push
- **rubocop** - Rubyのリンター実行

### リファクタリング・更新コマンド
- **check-srp** - 単一責任の原則（SRP）違反をチェックしてリファクタリング
- **update-test** - テストを必要十分な状態に調整
- **update-document** - CLAUDE.md/README.mdを更新
- **update-claude-md** - CLAUDE.mdに内容を追加

### Web検索コマンド
- **multi-llm-search** - ChatGPT O3、Claude Opus 4、Gemini 2.5 Proで同時検索
- **chatgpt-o3-search** - ChatGPT O3でWeb検索
- **claude-opus4-search** - Claude Opus 4でWeb検索  
- **gemini-25pro-search** - Gemini 2.5 ProでWeb検索
- **gemini-search** - Google Gemini CLIでWeb検索

### その他
- **notebooklm-upload** - NotebookLMに音声概要を作成

## 🐙 GitHub連携

GitHubのURL参照やプルリクエスト操作は必ず`gh`コマンドを使用してください：

```bash
# プルリクエストの詳細確認
gh pr view [PR番号]

# プルリクエストの差分確認  
gh pr diff [PR番号]

# プルリクエストのコメント確認
gh api repos/[owner]/[repo]/pulls/[PR番号]/comments

# プルリクエストの作成
gh pr create --title "タイトル" --body "本文"

# プルリクエストの一覧確認
gh pr list

# GitHub Issues の確認
gh issue list
gh issue view [Issue番号]
```

**重要原則**:
- GitHubのURLを直接参照しない（404エラーの原因となるため）
- WebFetch tool でのGitHub URL アクセスは禁止
- 必ず`gh`コマンドを使用してリポジトリ情報にアクセスする
- エラーが発生した場合は`gh auth status`で認証状態を確認

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
