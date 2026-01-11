# GitHub技術仕様

統合スキル `~/.claude/skills/github/SKILL.md` から参照される技術仕様。

## PR情報取得（URLが提供された場合）

```bash
# 基本情報
gh pr view <PR番号> --repo <owner/repo> --json title,body,state,author,url,headRefName,baseRefName

# ファイル変更情報
gh pr view <PR番号> --repo <owner/repo> --json files,additions,deletions,changedFiles

# 差分
gh pr diff <PR番号> --repo <owner/repo>
```

## PR操作

```bash
gh pr list                           # PR一覧
gh pr create --title "" --body ""    # PR作成
gh pr checkout <PR番号>               # PRのブランチをチェックアウト
gh pr merge <PR番号>                  # PRをマージ
```

## Issue操作

```bash
gh issue list                 # Issue一覧
gh issue view <番号>           # Issue詳細
gh issue create --title "" --body ""  # Issue作成
```

## その他

```bash
gh api repos/<owner>/<repo>/pulls/<番号>/comments  # PRコメント取得
gh auth status                # 認証状態確認
```
