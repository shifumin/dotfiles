# CLAUDE.md

Claude Codeを使用する際の必須ガイドライン。

> **優先度**: このドキュメントの指示は、デフォルトの動作よりも優先される。

---

## 🔴 重要な原則

以下は**必ず遵守**する原則:

| # | 原則 | 説明 |
|---|------|------|
| 1 | **既存のコードスタイルを厳守** | プロジェクトの規約から逸脱しない |
| 2 | **プロジェクトのツールを使用** | 新しいツールやフレームワークを勝手に導入しない |
| 3 | **コミット前の必須チェック** | リンターとテストを必ず実行する |
| 4 | **テストの同期** | 実装を追加・変更した場合は、対応するテストも追加・変更する |
| 5 | **疑問があれば必ず質問** | 要件や仕様に疑問が生じた場合は、作業を中断してユーザーに確認する |

---

## インタラクション

- **短縮応答の解釈**: ユーザーが「y」「yes」「ok」と答えた場合 → 「はい」「了承」として解釈する

---

## コード品質

| 項目 | ルール | 理由 |
|------|--------|------|
| **テスト作成** | 正常系・異常系・エッジケースを網羅し、publicインターフェースのみテスト | 内部実装への依存を避け、リファクタリング耐性を高めるため |
| **YARDコメント** | Rubyコード実装時はYARDコメントを追記（クラス、メソッド、パラメータ、戻り値） | AIとIDEがコードを正確に理解するため |
| **ドキュメント更新** | 必要に応じてREADME.md（英語）とCLAUDE.mdを更新 | コードとドキュメントの乖離を防ぐため |

**YARDコメントの例:**
```ruby
# ユーザーを検索する
#
# @param name [String] 検索するユーザー名
# @param limit [Integer] 取得件数の上限（デフォルト: 10）
# @return [Array<User>] マッチしたユーザーの配列
# @raise [ArgumentError] nameが空の場合
def find_users(name, limit: 10)
  # ...
end
```

---

## セキュリティ

**コミット前に以下が含まれていないか確認**:

| 種類 | 例 |
|------|-----|
| 認証情報 | APIキー、トークン、パスワード |
| 個人情報 | 公開を意図しないメール、電話番号 |
| インフラ情報 | 内部URL、秘密鍵、証明書 |
| 環境情報 | 本番環境の接続文字列、ホスト名 |

**確認方法:**
```bash
git diff --staged
```

**秘匿情報が含まれている場合**: 即座にユーザーに報告し、コミットを中止する。

---

## シェルコマンド

環境設定が必要なコマンドは、必ず `mise exec` を使用して実行する。

**対象コマンド**: bundle, rails, rspec, pnpm, node, ruby など

**理由**: miseで管理されているツールと環境変数を正しく読み込むため

**例:**
```bash
# ✅ OK: mise exec経由
mise exec -- bundle exec rspec spec/models/post_spec.rb
mise exec -- pnpm install
mise exec -- rails console

# ❌ NG: 直接実行（環境変数が読み込まれない）
bundle exec rspec spec/models/post_spec.rb
```

---

## カスタムコマンド

`~/.claude/commands/` に定義されたコマンド:

### 基本

| コマンド | 説明 |
|----------|------|
| `finish` | リンター・テスト実行、ドキュメント更新 |
| `push` | 適切な粒度でcommit/push |
| `rubocop` | Rubyリンター実行 |

### リファクタリング

| コマンド | 説明 |
|----------|------|
| `check-srp` | 単一責任の原則違反をチェック |
| `check-performance` | パフォーマンス改善点をチェック |
| `update-test` | テストを調整 |
| `update-document` | CLAUDE.md/README.mdを更新 |
| `update-claude-md` | CLAUDE.mdに内容を追加 |
| `optimize-for-ai` | ドキュメントをAI向けに最適化 |

### GitHub

| コマンド | 説明 |
|----------|------|
| `create-github-repo` | GitHubリポジトリを作成 |
| `review-pr` | PRをレビュー |
| `review-pr-comment` | PRコメントを確認 |

### カレンダー

| コマンド | 説明 |
|----------|------|
| `list-calendar-events` | 予定を一覧表示 |
| `create-calendar-event` | 予定を作成 |
| `update-calendar-event` | 予定を更新 |
| `delete-calendar-event` | 予定を削除 |

> **注意**: Googleカレンダーの操作はMCPツールではなく、上記のカスタムコマンド（スクリプト）を使用すること

### その他

| コマンド | 説明 |
|----------|------|
| `multi-llm-search` | 複数LLMで同時検索 |
| `notebooklm-upload` | NotebookLMに音声概要を作成 |

---

## 外部連携ドキュメント

詳細な使用方法は以下を参照:

| 連携先 | ドキュメント |
|--------|-------------|
| GitHub | `~/.claude/docs/github-workflow.md` |
| Google Calendar | `~/.claude/docs/google-calendar.md` |

---

## プロジェクト固有の設定

プロジェクト固有の追加情報がある場合は、以下に記載:

<!-- プロジェクト固有の設定をここに追加 -->
