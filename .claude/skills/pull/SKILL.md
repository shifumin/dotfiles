---
name: pull
description: "リモートの最新変更を現在のブランチに取り込む。未コミット変更を自動stash→pull→popで保護し、git config pull.rebaseを尊重してコンフリクトも可能な範囲で自動解決する。「pullして」「最新を取得」「リモートから引っ張って」「pull」「最新化して」「リモートを反映」「fetchして取り込んで」で使用。"
---

# Pull

リモートの最新変更を現在のブランチに取り込む。

## 処理フロー

### 1. 状態確認

以下を並列で実行する:

| コマンド | 目的 |
|---------|------|
| `git status --porcelain` | 未コミット変更の有無（ステップ 2 で再利用） |
| `git branch --show-current` | 現在のブランチ名（空なら detached HEAD） |
| `git rev-parse --abbrev-ref '@{upstream}'` | 追跡ブランチの確認（無ければエラー終了＝追跡なしシグナル） |
| `git config pull.rebase` | リポジトリ／ユーザーの rebase 設定確認 |
| `git fetch` | リモートの最新情報を取得 |

fetch 後、取り込む変更件数を `git rev-list --count 'HEAD..@{upstream}'` で確認し、次の通り分岐する:

| 状況 | 対応 |
|------|------|
| detached HEAD（ブランチ名が空） | pull を中止し、ブランチをチェックアウトするよう報告して終了 |
| 追跡ブランチなし | pull を中止。`origin/<branch>` が存在すれば `git branch --set-upstream-to=origin/<branch>` を提案、無ければ「pull 対象がない」と報告して終了 |
| 取り込む変更が `0` 件 | 「最新です」と報告して終了 |
| 取り込む変更が `1` 件以上 | ステップ 2 へ進む |

### 2. 未コミット変更の退避

ステップ 1 の `git status --porcelain` が空でなければ、untracked を含めてタイムスタンプ付きで退避する。既存の別 stash と混同しないよう、実行前後の `refs/stash` を比較して今回作成されたか判定する:

```bash
bash <<'SCRIPT'
set -euo pipefail
BEFORE=$(git rev-parse -q --verify 'refs/stash' || true)
git stash push -u -m "auto-stash before pull at $(date +%Y-%m-%dT%H:%M:%S)"
AFTER=$(git rev-parse -q --verify 'refs/stash' || true)
if [ -n "$AFTER" ] && [ "$AFTER" != "$BEFORE" ]; then
  echo "STASH_CREATED=1"
else
  echo "STASH_CREATED=0"
fi
SCRIPT
```

`STASH_CREATED=0`（`.gitignore` 対象のみの変更など）ならステップ 4 の `stash pop` はスキップする。

### 3. Pull 実行とコンフリクト処理

`git config pull.rebase` の設定を尊重して実行する:

| `pull.rebase` の値 | 実行コマンド |
|---|---|
| `true` / `interactive` | `git pull --rebase`（非対話環境でのエディタ停止を避けるため `interactive` も非対話で実行） |
| `merges` / `preserve` | `git pull --rebase=merges` |
| `false` / 未設定 | `git pull` |

コンフリクトなく完了したらステップ 4 へ進む。コンフリクト発生時は以下の順で自動解決を試みる:

1. `git status` でコンフリクト対象を確認する
2. 各ファイルを次の基準で解決する:
   - 片側のみ変更（add/add、modify/delete 等で意図が明確）→ 適切な側を採用
   - 両側の変更が論理的に矛盾しない（別関数・別セクションへの追加等）→ 両方を残して統合
   - import 文・lock ファイル等の機械的競合 → 両側を統合
3. 同一行の論理競合など自動解決できない箇所が残る場合は中断し、`git status` の結果と `git rebase --abort` / `git merge --abort` の選択肢をユーザーに報告する
4. 全ファイル解決できたら、`git add <resolved-files>` 後に現在の統合方式に応じて完了する:
   - rebase 中（`git rev-parse --git-path rebase-merge` または `rebase-apply` が存在）: `GIT_EDITOR=true git rebase --continue`（エディタ起動によるハング防止。後続コミットで再コンフリクトした場合は 1〜4 を繰り返す）
   - merge 中（`git rev-parse --git-path MERGE_HEAD` が存在）: `git commit --no-edit`

自動解決を行った場合は、各ファイルの判断内容をステップ 5 で必ず報告する。

### 4. stash 復元

ステップ 2 で `STASH_CREATED=1` だった場合のみ `git stash pop` を実行する。

- **成功**: ステップ 5 へ進む
- **コンフリクト発生**: **自動解決を試みず、stash を残したまま** ユーザーへ報告する（`git stash list` で残存を確認し、pull 自体は完了済みであること・`git stash pop` / `drop` はユーザー判断であることを伝える）
  - ユーザーが upstream 側の採用を承認したら `git checkout HEAD -- <file>` で戻す（stash pop では `--theirs` が stash 側を指すため使わない）。`git diff HEAD -- <file>` が空になったのを確認してから `git stash drop` する

### 5. 結果報告

`ORIG_HEAD`（merge・rebase 問わず pull 実行前の HEAD を指す。`HEAD@{1}` は rebase 経由で `HEAD` と一致するため使わない）を基準に以下を報告する:

- 取り込んだコミット数・概要（`git log ORIG_HEAD..HEAD --oneline`）
- 変更されたファイル数（`git diff ORIG_HEAD..HEAD --stat`）
- 自動 stash → pop を行った場合はその旨
- コンフリクトを自動解決した場合は対象ファイルと判断内容
- リポジトリの `CLAUDE.md` / `AGENTS.md` に pull 後の手順（dotfiles の `./setup.sh` 等）があれば従い、その結果

## エラー処理と安全策

| 状況 | 対処 |
|------|------|
| 認証エラー | 認証情報の確認を案内（`gh auth status`、SSH 鍵、credential helper 等） |
| ネットワークエラー | エラー内容を報告し再試行を提案 |
| pre-commit / pre-merge hook 失敗 | hook のエラー内容を報告し修正を提案 |
| `git stash push` が `Saved working directory...` 後に `Operation not permitted` で途中停止 | stash は保存済みで作業ツリーが中途半端な状態。stash を再実行せず `git stash list` と `git status` を報告する。残存差分が stash と同一（`git diff --quiet 'stash@{0}' -- <path>`）なら、その変更を戻してからサンドボックス外で pull → `git stash pop` で復旧可能 |

- `git pull --force` や `git reset --hard origin/<branch>` は使わない（ユーザーから明示的に依頼された場合のみ、リスクを説明した上で実行する）。
