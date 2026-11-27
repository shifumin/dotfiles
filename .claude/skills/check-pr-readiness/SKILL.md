---
name: check-pr-readiness
description: "PR のマージ前残タスク（未解決スレッド・レビュー本文・bot レビュー・コンフリクト・必須チェック・ラベル・approve）を全観点 1 パスで点検し表で返す。「このPRでやること残ってない？」「マージできる状態？」「マージを防いでいるものは？」「残タスク確認」等、PR の完了確認では必ず使う。対象外: 指摘の対応要否判断（review-pr-comments）、コードレビュー（reviewing-pr）。"
---

# PR マージ前の残タスク点検

1〜2 観点だけ見て「残りなし」と答えると、ユーザーが聞き直すたびに新しい残タスクが出てくる。毎回すべての観点を 1 パスで確かめ、まとめて返す。

## 手順

PR 番号省略時は現在ブランチの PR。以下を並列で取得する:

```bash
gh pr view [<number>] --json number,state,headRefOid,baseRefName,mergeable,mergeStateStatus,reviewDecision,labels,isDraft
python3 -B ~/.claude/skills/review-pr-comments/scripts/pr_comments.py fetch "<PR URL>"
gh api "repos/{owner}/{repo}/pulls/<number>/reviews" --paginate \
  -q '.[] | select(.user.type == "Bot") | {user: .user.login, commit: .commit_id, state, submitted_at}'
gh pr checks [<number>] --required
```

| # | 観点 | 確かめ方 |
|---|---|---|
| 1 | マージ可否・コンフリクト | `mergeable` / `mergeStateStatus`。`CONFLICTING` なら `git fetch origin <base>` → `git merge-tree --write-tree --name-only origin/<base> HEAD` で対象ファイルまで出す |
| 2 | 未解決スレッド | `unresolved_threads` のうち、最後の発言者が PR 作成者以外のもの |
| 3 | レビュー本文の指摘 | `reviews_with_body` の Outside diff / Nitpick 等に、`issue_comments` の返信がないもの |
| 4 | bot レビュー | 各 bot の最新レビューの `commit` が `headRefOid` と一致するか。本文やコメントに `Reviews paused` 等が出ていないか |
| 5 | 必須チェック | `--required` の失敗・pending（必須チェック未設定でエラーなら `gh pr checks` 全体で見る）。失敗は最新の実行か、古い実行の残骸か区別する |
| 6 | ラベル・approve・draft | リポジトリで必須のラベル（QA 結果、リリースノート等）、`reviewDecision`、`isDraft` |
| 7 | 本文と差分のずれ | 気づいた点だけ挙げ、直すなら `update-pr-description` に委ねる |

## 報告

```markdown
| # | 観点 | 状態 | 内容 |
|---|---|---|---|
| 1 | コンフリクト | ✅ / 要対応 / 他者待ち | ... |
```

要対応は「次に何をするか」まで書く。全観点が ✅ のときだけ「マージ可能」と言い切る。

## 失敗チェックへの対処

- ラベル付与や承認など、イベント起点の workflow を re-run すると元のイベントのペイロードで再判定される。ラベルの付け直しなど新しいイベントで起こし直す
- 同じ concurrency group の実行を同時に re-run しない（互いにキャンセルされる）
- 結果待ちは固定の `sleep` ではなく until ループ（Claude Code では Monitor）で行う
