# GitHub連携

GitHubのURL参照やプルリクエスト操作は必ず`gh`コマンドを使用。

## 重要原則

- GitHubのURLを直接参照しない（404エラーの原因）
- WebFetch toolでのGitHub URLアクセスは禁止
- 必ず`gh`コマンドを使用
- エラー時は`gh auth status`で認証確認

## PR情報取得（URLが提供された場合）

```bash
# 基本情報
gh pr view <PR番号> --repo <owner/repo> --json title,body,state,author,url,headRefName,baseRefName

# ファイル変更情報
gh pr view <PR番号> --repo <owner/repo> --json files,additions,deletions,changedFiles

# 差分
gh pr diff <PR番号> --repo <owner/repo>
```

## その他のコマンド

```bash
gh pr list                    # PR一覧
gh pr create --title "" --body ""  # PR作成
gh issue list                 # Issue一覧
gh issue view [番号]           # Issue詳細
gh api repos/[owner]/[repo]/pulls/[番号]/comments  # PRコメント
```
