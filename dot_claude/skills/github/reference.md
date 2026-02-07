# GitHub技術仕様

統合スキル `~/.claude/skills/github/SKILL.md` から参照される技術仕様。

---

## PR関連コマンド

### gh pr view JSONフィールド

| カテゴリ | フィールド |
|---------|----------|
| 基本情報 | number, title, body, state, url |
| ブランチ | headRefName, baseRefName, headRepository |
| 作成者 | author |
| 日時 | createdAt, updatedAt, mergedAt, closedAt |
| レビュー | reviews, reviewRequests, reviewDecision |
| ラベル | labels, milestone, projectCards |
| 変更 | files, additions, deletions, changedFiles |
| マージ | mergeable, mergeStateStatus |
| CI | statusCheckRollup |

### gh pr list フィルタ例

| 目的 | コマンド |
|------|---------|
| 自分のopen PR | `gh pr list --author @me` |
| レビュー待ち | `gh pr list --search "review:required"` |
| 特定ラベル | `gh pr list --label "bug"` |
| マージ済み（直近） | `gh pr list --state merged --limit 10` |

### gh pr diff オプション

| オプション | 説明 |
|-----------|------|
| `--patch` | patch形式で出力 |
| `--name-only` | 変更ファイル名のみ |

### gh pr merge 戦略

| フラグ | 説明 |
|--------|------|
| `--merge` | マージコミット |
| `--squash` | スカッシュマージ |
| `--rebase` | リベースマージ |
| `--auto` | CIパス後に自動マージ |
| `--delete-branch` | マージ後にブランチ削除 |

---

## Issue関連コマンド

### gh issue view JSONフィールド

| フィールド | 説明 |
|-----------|------|
| number, title, body, state, url | 基本情報 |
| author, assignees | 人 |
| labels, milestone, projectCards | 分類 |
| comments | コメント一覧 |
| createdAt, updatedAt, closedAt | 日時 |

### gh issue list フィルタ例

| 目的 | コマンド |
|------|---------|
| 自分にassign | `gh issue list --assignee @me` |
| 特定ラベル | `gh issue list --label "bug"` |
| キーワード検索 | `gh issue list --search "keyword"` |

---

## CI/Checks

### gh pr checks JSONフィールド

| フィールド | 説明 |
|-----------|------|
| name | チェック名 |
| state | PENDING, SUCCESS, FAILURE, ERROR |
| conclusion | success, failure, neutral, cancelled, timed_out |
| url | チェック詳細URL |

---

## Workflow/Actions

### gh run list JSONフィールド

| フィールド | 説明 |
|-----------|------|
| databaseId | Run ID |
| displayTitle | 表示タイトル |
| status | queued, in_progress, completed |
| conclusion | success, failure, cancelled |
| headBranch | ブランチ名 |
| createdAt | 開始日時 |
| url | Actions URL |

### gh run view オプション

| オプション | 説明 |
|-----------|------|
| `--log` | 全ジョブのログ |
| `--log-failed` | 失敗ジョブのログのみ |
| `--json jobs` | ジョブ一覧をJSON出力 |
| `--exit-status` | 終了コードをrunの結果に合わせる |

---

## 通知API

### エンドポイント

| 操作 | コマンド |
|------|---------|
| 一覧取得 | `gh api notifications` |
| 既読にする | `gh api -X PUT notifications` |
| 特定スレッド既読 | `gh api -X PATCH notifications/threads/{id}` |

### レスポンス構造

| フィールド | 説明 |
|-----------|------|
| .subject.title | 通知タイトル |
| .subject.type | PullRequest, Issue, Release等 |
| .reason | review_requested, mention, assign等 |
| .updated_at | 更新日時 |
| .repository.full_name | リポジトリ名 |

---

## 検索クエリ構文

`gh pr list` / `gh issue list` の `--search` で使えるGitHub検索構文:

| 構文 | 説明 | 例 |
|------|------|-----|
| `is:open` / `is:closed` | 状態フィルタ | `--search "is:open"` |
| `author:user` | 作成者 | `--search "author:octocat"` |
| `review:required` | レビュー未完了 | `--search "review:required"` |
| `review:approved` | レビュー承認済み | `--search "review:approved"` |
| `draft:true` | ドラフトPR | `--search "draft:true"` |
| `label:name` | ラベル | `--search "label:bug"` |
| `milestone:name` | マイルストーン | `--search "milestone:v1.0"` |
| `created:>YYYY-MM-DD` | 作成日以降 | `--search "created:>2026-01-01"` |

---

## PRコメント取得（API経由）

```bash
# PRのレビューコメント
gh api repos/{owner}/{repo}/pulls/{number}/comments \
  --jq '.[] | {user: .user.login, body: .body, path: .path, line: .line, created_at: .created_at}'

# PRの通常コメント（conversation）
gh api repos/{owner}/{repo}/issues/{number}/comments \
  --jq '.[] | {user: .user.login, body: .body, created_at: .created_at}'
```
