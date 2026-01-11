---
description: GitHubのPR・Issue操作を行う。
「PRを見て」「プルリクエストを確認」「Issueを作成」「GitHubの〜」などのリクエストで使用。
---

# GitHub連携

GitHubのPR・Issue操作は必ず`gh`コマンドを使用する。

## 重要原則

- **GitHubのURLを直接参照しない**（404エラーの原因）
- **WebFetch toolでのGitHub URLアクセスは禁止**
- 必ず`gh`コマンドを使用
- エラー時は`gh auth status`で認証確認

## トリガー

| 操作 | トリガー例 |
|------|-----------|
| PR情報取得 | 「このPRを見て」「PRをレビューして」 |
| PR作成 | 「PRを作成して」「プルリクエストを出して」 |
| Issue確認 | 「Issueを見て」「Issue一覧を教えて」 |
| Issue作成 | 「Issueを作成して」「バグ報告して」 |

## 処理フロー

### PR情報取得（URLが提供された場合）

1. URLからオーナー、リポジトリ、PR番号を抽出
2. `gh pr view` で基本情報を取得
3. 必要に応じて `gh pr diff` で差分を取得

### PR作成

1. 現在のブランチとリモートを確認
2. `gh pr create` でPRを作成
3. タイトルと本文をユーザーに確認してから実行

### Issue操作

1. `gh issue list` で一覧取得
2. `gh issue view` で詳細取得
3. `gh issue create` で作成

## 技術仕様

詳細なコマンド例は `~/.claude/skills/github/reference.md` を参照。
