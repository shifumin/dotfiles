# CLAUDE.md

このドキュメントは、Claude Codeを使用する際の必須ガイドラインです。

## 重要な原則

1. **既存のコードスタイルを厳守** - プロジェクトの規約から逸脱しない
2. **プロジェクトのツールを使用** - 新しいツールやフレームワークを勝手に導入しない
3. **コミット前の必須チェック** - リンターとテストを必ず実行する
4. **テストの同期** - 実装を追加・変更した場合は、対応するテストも追加・変更する
5. **疑問があれば必ず質問** - 要件や仕様に疑問が生じた場合は、作業を中断してユーザーに確認する

## コード品質

- **テスト作成**: 正常系・異常系・エッジケースを網羅し、publicインターフェースのみテスト
- **ドキュメント更新**: 必要に応じてREADME.md（英語）とCLAUDE.mdを更新

## セキュリティ

**コミット前に以下が含まれていないか確認**:
- APIキー、トークン、パスワード
- 公開を意図しない個人情報
- 内部URL、秘密鍵、証明書
- 本番環境の接続情報

`git diff --staged`で確認し、秘匿情報が含まれている場合は即座にユーザーに報告。

## カスタムコマンド

~/.claude/commands/ に定義されたコマンド:

### 基本
- **finish** - リンター・テスト実行、ドキュメント更新
- **push** - 適切な粒度でcommit/push
- **rubocop** - Rubyリンター実行

### リファクタリング
- **check-srp** - 単一責任の原則違反をチェック
- **check-performance** - パフォーマンス改善点をチェック
- **update-test** - テストを調整
- **update-document** - CLAUDE.md/README.mdを更新
- **update-claude-md** - CLAUDE.mdに内容を追加

### GitHub
- **create-github-repo** - GitHubリポジトリを作成
- **review-pr** - PRをレビュー
- **review-pr-comment** - PRコメントを確認

### カレンダー
- **list-calendar-events** - 予定を一覧表示
- **create-calendar-event** - 予定を作成
- **update-calendar-event** - 予定を更新
- **delete-calendar-event** - 予定を削除

### その他
- **multi-llm-search** - 複数LLMで同時検索
- **notebooklm-upload** - NotebookLMに音声概要を作成

## 外部連携ドキュメント

詳細な使用方法は以下を参照:
- **GitHub連携**: `~/.claude/docs/github-workflow.md`
- **Google Calendar連携**: `~/.claude/docs/google-calendar.md`

## プロジェクト固有の設定

プロジェクト固有の追加情報がある場合は、以下に記載:

---

**注意**: このドキュメントの指示は、デフォルトの動作よりも優先されます。
