---
description: ライブラリアップデートPRをレビューし、マージ可否を判断する。
  「ライブラリ更新レビュー」「依存関係の更新確認」「review library update」
  「PRレビュー ライブラリ」「dependabot」「bump PR」などのリクエストで使用。
  ライブラリのバージョンアップに関するPRを見かけたら、このスキルを使うこと。
---
# Reviewing Library Updates

ライブラリアップデートPRをレビューし、セキュリティ・Breaking Changes・互換性・CI結果を確認してマージ可否を判断する。

PR URLを引数で受け取る。省略時はAskUserQuestionで確認。

---

## 処理フロー

### 1. PR基本情報の取得

URL `https://github.com/<owner>/<repo>/pull/<number>` からowner/repo/numberを抽出し、並列実行:

```bash
gh pr view <PR番号> --repo <owner>/<repo> --json title,body,state,author,createdAt,url,headRefName,baseRefName
gh pr diff <PR番号> --repo <owner>/<repo>
gh pr checks <PR番号> --repo <owner>/<repo>
```

diffから更新ライブラリを特定:

| 環境 | 対象ファイル |
|------|------------|
| Ruby | Gemfile.lock |
| Node.js | package.json, pnpm-lock.yaml |

各ライブラリの名前・更新前バージョン・更新後バージョンを抽出する。

### 2. PR bodyからの情報抽出（Dependabot対応）

Dependabot/Renovate等が生成するPR bodyには有用な情報が含まれている。`gh pr view` の `body` フィールドから以下を先に確認する:

- Release notes（リリースノートの要約）
- Changelog（変更履歴の抜粋）
- Commits（コミット一覧）
- Compatibility score

PR bodyに十分な情報がある場合はStep 3の外部取得を省略できる。情報が不足している場合のみStep 3へ進む。

### 3. 変更内容の調査

#### リポジトリの特定

| 環境 | コマンド | フォールバック |
|------|---------|-------------|
| Ruby | `bundle info <gem名>` でHomepage取得 | `gem specification <gem名> homepage --remote` |
| Node.js | `npm info <package名> repository.url` | — |

コマンドで取得できない場合はWebSearchで `<ライブラリ名> github` を検索。

#### リリースノートの確認

| 優先度 | 情報源 | 取得方法 |
|-------|--------|---------|
| 1 | GitHubリリース一覧 | `gh release list --repo <library-repo> --limit 20` で一覧取得 |
| 2 | 個別リリース | `gh release view <tag> --repo <library-repo>` （タグは `v1.0.0` と `1.0.0` 両方試す） |
| 3 | CHANGELOG.md | WebFetchツール |
| 4 | 公式ドキュメント | WebFetchツール |

更新前から更新後までの**全リリース**を確認する。中間バージョンにBreaking Changesが含まれている場合があるため、`gh release list` で該当範囲のリリースを特定してから個別に確認する。

### 4. レビュー観点のチェック

#### CI/テスト結果

`gh pr checks` の結果を確認する。CI失敗はマージ判断に直結する重要な情報。

| 状態 | 意味 |
|------|------|
| pass | 全チェック通過 |
| fail | テスト失敗あり（原因を調査） |
| pending | 実行中（結果待ち） |

CI失敗時は失敗しているジョブ名を記録し、ライブラリ更新との関連性を判断する。

#### セキュリティ修正

リリースノートで「security」「vulnerability」「CVE」を検索し、CVE番号・深刻度・概要を記録する。

#### Breaking Changes

| 影響度 | 条件 |
|-------|------|
| 高 | APIシグネチャ変更、非推奨機能削除、必須設定追加 |
| 中 | オプション設定変更、警告追加 |
| 低 | 後方互換性あり（バグ修正、パフォーマンス改善） |

バージョン種別も判断材料にする:
- **major**: Breaking Changesの可能性が高い。慎重に確認
- **minor**: 新機能追加が中心だが非推奨化の可能性あり
- **patch**: バグ修正・セキュリティ修正が中心。通常は安全

#### 互換性

| 項目 | 確認内容 |
|------|---------|
| Runtime | Ruby/Node.jsバージョンの要件変更 |
| 依存関係 | 依存ライブラリのバージョン変更 |
| Framework | Rails等のフレームワーク互換性 |

### 5. プロジェクトへの影響調査

Breaking Changes検出時のみ実施する。Grepツールでライブラリの使用箇所を検索し、影響を受けるファイルとコード行を特定する。

| 環境 | 検索対象 |
|------|---------|
| Ruby | `*.rb`, `*.erb` |
| Node.js | `*.ts`, `*.tsx`, `*.js`, `*.jsx` |

Breaking Changesが検出されなかった場合はこのステップをスキップしてよい。

### 6. レビュー結果の出力

出力フォーマットに従って結果を報告する。

---

## 出力フォーマット

```markdown
### PR情報
- **タイトル**: {PRタイトル}
- **ブランチ**: {head} → {base}
- **作成者**: {author}

### ライブラリ更新内容

| ライブラリ名 | 更新前 | 更新後 | 種別 |
|-------------|--------|--------|------|
| {名前} | {バージョン} | {バージョン} | {patch/minor/major} |

### CI結果: PASS / FAIL / PENDING

（FAILの場合）
- **失敗ジョブ**: {ジョブ名}
- **関連性**: ライブラリ更新に起因 / 既存の問題 / 不明

### 変更内容の要約

**{ライブラリ名} ({更新前} → {更新後})**
- {リリースノートからの主な変更点}

### セキュリティ修正: あり / なし

（ありの場合）
| CVE番号 | 深刻度 | 概要 |
|---------|--------|------|

### Breaking Changes: あり / なし

（ありの場合）
- **影響度**: 高 / 中 / 低
- **詳細**: {変更の詳細}
- **影響箇所**: {ファイルパス:行番号}
- **対応方法**: {必要な対応}

### 互換性: OK / 要確認

### 総評

**判断**: マージ可 / 条件付き / 要対応
**理由**: {条件付き/要対応の場合の理由}
```

### 判断基準

| CI結果 | セキュリティ修正 | Breaking Changes | 互換性 | 判断 |
|--------|---------------|-----------------|--------|------|
| FAIL | - | - | - | 要対応（CI修正が必要） |
| PASS | あり | - | - | マージ可（脆弱性修正を優先） |
| PASS | なし | なし | OK | マージ可 |
| PASS | なし | 高 | - | 要対応（コード修正後にマージ） |
| PASS | なし | 中 | OK | 条件付き（設定変更確認後にマージ） |
| PASS | なし | - | NG | 要対応（環境要件確認後にマージ） |
| PENDING | - | - | - | 条件付き（CI完了を待ってから判断） |
