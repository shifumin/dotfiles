# review-pr [PR URL]

PRをレビューし、変更内容と改善点をまとめる。

## 実行フロー

### STEP 1: PR情報の取得

URLパターン: `github\.com/([^/]+)/([^/]+)/pull/(\d+)`

以下を**並列実行**:

```bash
gh pr view <PR番号> --repo <owner>/<repo> --json title,body,state,author,createdAt,url,headRefName,baseRefName
gh pr view <PR番号> --repo <owner>/<repo> --json files,additions,deletions,changedFiles
gh pr diff <PR番号> --repo <owner>/<repo>
```

| エラー | 原因 |
|--------|------|
| `Could not resolve to a PullRequest` | PR番号が不正 |
| `Could not resolve to a Repository` | リポジトリ名不正 or アクセス権限なし |
| `HTTP 404` | 認証が必要 → `gh auth status`で確認 |

### STEP 2: 変更ファイルの読み込み

以下に該当するファイルは**必ずReadツールで読み込む**:

| 条件 | 対象 |
|------|------|
| ファイル特性 | 新規追加、変更100行以上、diffがtruncated |
| N+1チェック対象 | `app/{workers,services,controllers,models}/**/*.rb` |
| 重要ファイル | `db/migrate/**/*.rb`, `client/src/**/*.{ts,tsx}` |

**理由**: diffは途中で切れることがあり、正確な行番号の特定に必要

### STEP 3: 外部リソース確認（条件付き）

`client/src/**` の変更がある場合のみ実行:

**SmartHR Design Systemリポジトリ**: `~/ghq/github.com/kufu/smarthr-design-system`

1. 変更ファイルから使用コンポーネントを抽出
2. `src/content/` でガイドラインを検索（Grep）
3. 該当ガイドラインをReadで確認

参考: https://smarthr.design

### STEP 4: レビュー観点チェック

#### 必須チェック（全PR）

**A-1. N+1問題**

対象: `app/{workers,services,controllers,models}/**/*.rb`

| NG | 説明 |
|----|------|
| ループ内AR呼び出し | `each`/`map`内での`find_by`/`where` |
| eager load未使用 | `includes`/`preload`なしのアソシエーション呼び出し |

```ruby
# NG
users.each { |u| u.posts.count }

# OK
users.includes(:posts).each { |u| u.posts.count }
```

**A-2. PRのdescriptionとの整合性**

記載内容とコード変更が一致しているか確認

#### 条件付きチェック

| トリガー | チェック内容 |
|----------|-------------|
| `db/migrate/**` | migration妥当性、up/down整合性、インデックス適切性 |
| `client/src/**` | Design System準拠（下記参照） |
| `app/models/**` | scopeの適切な使用 |

**Design Systemチェック項目**:

| カテゴリ | 確認内容 |
|----------|----------|
| スタイリング | styled-componentsよりprops優先、レイアウトはStack/Cluster |
| コンポーネント | SmartHR UI標準コンポーネント使用、デザイントークン使用 |
| a11y | セマンティックHTML、ラベル、キーボード操作 |

**Railsモデルチェック**:

```ruby
# NG: クラスメソッドでのクエリ定義
def self.confirmed = where.not(confirmed_at: nil)

# OK: scopeを使用（チェーン可能、nil安全）
scope :confirmed, -> { where.not(confirmed_at: nil) }
```

#### 推奨チェック

- SRP違反
- エラーハンドリング
- セキュリティ（SQLi, XSS, CSRF）
- パフォーマンス

## 出力フォーマット

```markdown
### PR情報
- **タイトル**: [タイトル]
- **作成者**: [作成者]
- **状態**: OPEN/MERGED/CLOSED
- **ブランチ**: [head] → [base]
- **関連チケット**: [チケット番号]

### やりたいこと / やったこと
[descriptionから抽出]

### 変更内容のまとめ
#### `path/to/file.rb`
**変更行**: L123-L145
**変更概要**: [概要]

### 良い点
- [実装の優れている点]

### 修正が必要な点
#### 1. [問題の概要]
**ファイル**: `path/to/file.rb:123`
**問題点**: [影響]
**修正案**:
\`\`\`ruby
[コード]
\`\`\`

### PRのdescriptionとの整合性
✅ 整合性あり / ⚠️ 差異あり（詳細）

### チェック実施状況
- [x] N+1問題
- [x] description整合性
- [ ] Migration（該当なし）
- [ ] Design System（該当なし）
- [ ] Railsベストプラクティス（該当なし）

### 総評
[評価]
**承認推奨**: ✅ 承認可 / ⚠️ 条件付き / ❌ 要修正
```

## 禁止事項

| 禁止 | 理由 |
|------|------|
| diffから行番号を推測 | 不正確になる |
| Read未確認コードへの言及 | 存在確認できない |
| 修正不要項目の記載 | ノイズになる |
| 絶対パス使用 | `~`を使用すること |

## 使用例

```bash
/review-pr https://github.com/owner/repo/pull/12345
```
