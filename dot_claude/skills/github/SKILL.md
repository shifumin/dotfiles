---
description: GitHubのPR・Issue・CI/Actions・通知の操作を行う。
  「PRを見て」「Issue一覧」「CIの状態」「PRを承認」「通知を確認」などのリクエストで使用。
---

# GitHub操作

GitHubのPR・Issue・CI・Workflow・通知操作は必ず`gh`コマンドを使用する。

## 重要原則

- **GitHubのURLを直接参照しない**（404エラーの原因）
- **WebFetch toolでのGitHub URLアクセスは禁止**
- 必ず`gh`コマンドを使用
- エラー時は`gh auth status`で認証確認
- **URL抽出パターン**: `github\.com/([^/]+)/([^/]+)/(pull|issues)/(\d+)` でowner・repo・番号を抽出
- **リポジトリコンテキスト**: カレントディレクトリがgitリポジトリ内なら`--repo`省略可

---

## 操作の判定

| 操作 | トリガーとなる表現例 | 使用コマンド |
|------|---------------------|-------------|
| PR一覧 | 「PR一覧」「open PRs」 | `gh pr list` |
| PR詳細 | 「このPRを見て」「PR情報」 | `gh pr view` |
| PR作成 | 「PRを作成」「PRを出して」 | `gh pr create` |
| PRマージ | 「PRをマージ」 | `gh pr merge` |
| PRチェックアウト | 「PRをチェックアウト」 | `gh pr checkout` |
| PRレビュー送信 | 「PRを承認」「approve」「changes request」 | `gh pr review` |
| Issue一覧 | 「Issue一覧」「Issueを見て」 | `gh issue list` |
| Issue詳細 | 「Issue #123を見て」 | `gh issue view` |
| Issue作成 | 「Issueを作成」「バグ報告」 | `gh issue create` |
| Issueクローズ | 「Issueを閉じて」 | `gh issue close` |
| CI/Checks確認 | 「CIの状態」「テスト通った？」 | `gh pr checks` |
| Workflow一覧 | 「Actionsの状態」「ワークフロー」 | `gh run list` |
| Workflow詳細 | 「実行結果を見て」「failedの詳細」 | `gh run view` |
| 通知確認 | 「通知を確認」「レビュー待ちある？」 | `gh api notifications` |

---

## 共通設定

| 項目 | 内容 |
|------|------|
| ツール | `gh` CLI（認証済み） |
| リポジトリ指定 | `--repo owner/repo`（カレントディレクトリがリポジトリ内なら省略可） |
| JSON出力 | 構造化データが必要な場合 `--json field1,field2` を使用 |

---

## PR操作

### PR一覧

1. ユーザー入力からフィルタ条件を解釈（state, author, label等）
2. `gh pr list` を実行
3. Markdown表形式に整形

```bash
gh pr list [--repo owner/repo] [--state open|closed|merged|all] [--author user] [--label label] [--search "query"] [--limit N] [--json number,title,author,state,url,createdAt]
```

#### 出力の整形

```markdown
## PR一覧（N件）

| # | タイトル | 作成者 | 状態 | 作成日 |
|---|---------|--------|------|--------|
| #123 | Fix login bug | @user | OPEN | 2026-01-15 |
```

### PR詳細

1. URLまたはユーザー入力からowner/repo/番号を抽出
2. 基本情報と変更ファイル情報を取得
3. Markdown形式に整形

```bash
gh pr view <number> [--repo owner/repo] --json title,body,state,author,url,headRefName,baseRefName,createdAt,reviews,labels,milestone
gh pr view <number> [--repo owner/repo] --json files,additions,deletions,changedFiles
```

必要に応じて差分を取得:
```bash
gh pr diff <number> [--repo owner/repo]
```

#### 出力の整形

```markdown
## PR #123: タイトル

- **作成者**: @user
- **状態**: OPEN / MERGED / CLOSED
- **ブランチ**: feature-branch → main
- **ラベル**: bug, urgent
- **変更**: +100 -50 (5 files)

### 説明
PR本文...

### 変更ファイル
| ファイル | 追加 | 削除 |
|---------|------|------|
| path/to/file.ts | +30 | -10 |
```

### PR作成

1. 現在のブランチとリモートを確認
2. タイトルと本文をユーザーに確認してから実行
3. 作成後にURLを報告

```bash
gh pr create --title "title" --body "body" [--base main] [--draft] [--label label] [--reviewer user]
```

**注意**: 未コミットの変更がある場合は `/push` を先に案内。

### PRマージ

1. PR番号とマージ戦略をユーザーに確認
2. CI statusを確認（`gh pr checks`）
3. マージを実行

```bash
gh pr merge <number> [--repo owner/repo] [--merge|--squash|--rebase] [--delete-branch] [--auto]
```

**重要**: マージ戦略は必ずユーザーに確認。

### PRチェックアウト

```bash
gh pr checkout <number> [--repo owner/repo]
```

### PRレビュー送信

レビュー決定の送信（approve / request-changes / comment）を行う。

**境界**: コード分析・レビュー内容の作成は `/review-pr` が担当。このスキルは決定の送信のみ。

```bash
gh pr review <number> [--repo owner/repo] --approve [--body "LGTM"]
gh pr review <number> [--repo owner/repo] --request-changes --body "reason"
gh pr review <number> [--repo owner/repo] --comment --body "comment"
```

---

## Issue操作

### Issue一覧

```bash
gh issue list [--repo owner/repo] [--state open|closed|all] [--label label] [--assignee user] [--search "query"] [--limit N] [--json number,title,author,state,labels,createdAt]
```

#### 出力の整形

```markdown
## Issue一覧（N件）

| # | タイトル | ラベル | 作成者 | 作成日 |
|---|---------|--------|--------|--------|
| #45 | Login fails on mobile | bug | @user | 2026-01-10 |
```

### Issue詳細

```bash
gh issue view <number> [--repo owner/repo] --json title,body,state,author,labels,assignees,milestone,comments,createdAt,url
```

#### 出力の整形

```markdown
## Issue #45: タイトル

- **状態**: OPEN
- **作成者**: @user
- **ラベル**: bug, priority-high
- **Assignees**: @dev1, @dev2
- **作成日**: 2026-01-10

### 説明
Issue本文...

### コメント（N件）
**@commenter** (2026-01-11):
> コメント内容
```

### Issue作成

1. タイトルと本文をユーザーに確認
2. 作成後にURLを報告

```bash
gh issue create [--repo owner/repo] --title "title" --body "body" [--label label] [--assignee user]
```

### Issueクローズ

```bash
gh issue close <number> [--repo owner/repo] [--reason "completed"|"not planned"]
```

---

## CI/Checks確認

1. PR番号を特定（コンテキストまたはユーザー入力から）
2. `gh pr checks` を実行
3. ステータスを整形表示

```bash
gh pr checks <number> [--repo owner/repo] [--json name,state,conclusion,url]
```

#### 出力の整形

```markdown
## CI Status: PR #123

| チェック | 状態 | 結果 |
|---------|------|------|
| tests | completed | success |
| lint | completed | failure |
| deploy-preview | in_progress | - |

**総合**: 1 failed, 1 passed, 1 pending
```

---

## Workflow/Actions

### Workflow Run一覧

```bash
gh run list [--repo owner/repo] [--workflow name] [--status completed|in_progress|failure|success] [--limit N] [--json databaseId,displayTitle,status,conclusion,headBranch,createdAt,url]
```

#### 出力の整形

```markdown
## Workflow Runs

| ID | タイトル | ブランチ | 状態 | 結果 | 日時 |
|----|---------|---------|------|------|------|
| 12345 | CI | main | completed | success | 2026-01-15 |
```

### Workflow Run詳細・失敗ログ

```bash
gh run view <run-id> [--repo owner/repo] [--json jobs]
gh run view <run-id> --log-failed [--repo owner/repo]
```

---

## 通知確認

1. 通知をAPI経由で取得
2. タイプと理由を整形表示

```bash
gh api notifications --jq '.[] | {subject: .subject.title, type: .subject.type, reason: .reason, updated: .updated_at}'
```

#### 出力の整形

```markdown
## 通知（N件）

| タイプ | タイトル | 理由 | 更新日時 |
|--------|---------|------|---------|
| PullRequest | Fix login bug | review_requested | 2026-01-15 |
| Issue | Add dark mode | mention | 2026-01-14 |
```

---

## エラー処理

| エラーパターン | 原因 | 対処 |
|---------------|------|------|
| `Could not resolve to a PullRequest` | PR番号が不正 | 番号を確認、`gh pr list`で一覧確認 |
| `Could not resolve to a Repository` | リポジトリ名不正 or アクセス権なし | `--repo owner/repo`を確認 |
| `HTTP 401` / `HTTP 403` | 認証エラー | `gh auth status`で確認、`gh auth login`で再認証 |
| `HTTP 404` | リソースが存在しない or プライベートリポジトリ | URL・番号確認、認証確認 |
| `GraphQL: ...` | API制限やクエリエラー | エラー詳細を確認、`--json`フィールドを確認 |
| `no default remote found` | gitリポジトリ外で`--repo`省略 | `--repo owner/repo`を明示的に指定 |

---

## 他スキル・コマンドとの使い分け

| 操作 | 使用先 | 理由 |
|------|--------|------|
| PR/Issue情報取得・作成・マージ | **このスキル** | `gh`コマンドの基本操作 |
| PRレビュー送信（approve等） | **このスキル** | `gh pr review`コマンド |
| CI/Checks・Workflow確認 | **このスキル** | `gh`コマンドの基本操作 |
| 通知確認 | **このスキル** | `gh api notifications` |
| 深いコードレビュー | `/review-pr` | ファイル読み込み・N+1チェック等を含む |
| レビューコメント対応 | `/review-pr-comment` | コメント分析・修正方針提案 |
| commit + push | `/push` | ステージング・コミット・プッシュ一連 |
| リポジトリ作成 | `/create-github-repo` | repo作成 + ghq clone |

---

## 技術仕様

詳細な技術仕様（JSONフィールド一覧、検索クエリ構文など）は `~/.claude/skills/github/reference.md` を参照。
