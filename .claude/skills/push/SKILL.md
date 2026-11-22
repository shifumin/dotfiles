---
name: push
description: "変更内容をcommitしてリモートにpushする。Conventional Commits形式でコミット粒度を判断し、リンター・秘匿情報チェックも行う。「pushして」「コミットしてpush」「変更をプッシュ」「push」「変更を送って」「リモートに反映」「コードを上げて」で使用。"
---

# Push

変更内容を commit してリモートに push する。`@{...}` 構文は zsh 対策のため必ずシングルクォートで囲む。

## 処理フロー

### 1. 状態確認

以下を並列で実行する:

| コマンド | 目的 |
|---------|------|
| `git status --porcelain` | 変更ファイル一覧 |
| `git diff` | unstaged 変更の内容 |
| `git diff --staged` | staged 変更の内容 |
| `git branch --show-current` | 現在のブランチ名（空なら detached HEAD） |
| `git log --oneline -5` | 直近のコミットメッセージ傾向 |
| `git fetch` | リモートの最新状態を取得 |

fetch 後、`git log --oneline '@{upstream}..HEAD'` で未 push コミットを確認する（追跡ブランチが無いと失敗するが、失敗自体を「追跡ブランチなし」のシグナルとしてステップ 5 で扱う）。

| 状況 | 対応 |
|------|------|
| detached HEAD（ブランチ名が空） | push を中止し、ブランチを作成するよう案内して終了 |
| ワーキングツリーまたはステージに変更あり | ステップ 2 へ進む |
| 変更なし + 未 push コミットあり（または追跡ブランチなし） | ステップ 5 へ進む |
| 変更なし + 未 push コミットなし | 「変更なし」と報告して終了 |

### 2. コミット前チェック

プロジェクトのリンター・テストを次の優先順で検出し、見つかれば実行する:

1. プロジェクトの `AGENTS.md` / `CLAUDE.md` / `README.md` に記載されたコマンド
2. 設定ファイル（`package.json` の scripts、`Gemfile` の rake/rspec、`pyproject.toml`、`Makefile` 等）
3. どちらも無ければスキップ

失敗した場合は修正して再実行し、パスしてからステップ 3 へ進む。

### 3. コミット粒度の判断

コミットメッセージ形式はプロジェクトの `AGENTS.md` / `CLAUDE.md` の指定を優先し、無ければ Conventional Commits と直近の `git log --oneline` に合わせる。

異なる種類の変更は git bisect / revert の粒度を保つため別コミットに分ける。迷う場合の既定値:
- コメント追加・既存挙動の明示化 → `fix` か `chore`（影響度が大きい方）
- 同 type で scope 違い → 1 コミットに統合

| 変更の分布 | 対応 |
|---|---|
| 単一種類 | 1 コミットにまとめる |
| 複数種類（別ファイル） | 種類ごとにファイルを分けて別コミット（例: `docs` → `feat`） |
| 複数種類（同一ファイル内・別ハンクまたは同一ハンク別行） | 下記のパッチ分割手順で種類ごとにステージして別コミット |
| 複数種類（同一行内） | 分離せず 1 コミットに統合（影響度が大きい type を採用。例: `fix`+`feat` → `feat`） |

#### 同一ファイル内のパッチ分割手順

`noclobber` や並行実行による衝突を避けるため、必ず `mktemp` の一時ファイルを使う:

1. `PATCH=$(mktemp "${TMPDIR:-/tmp}/push-split.XXXXXX.patch")` で一時ファイルを作り、`git diff -- <file> >| "$PATCH"` で全差分を書き出す
2. 今回のコミットに含める変更だけを残すよう `"$PATCH"` を編集する（同一ハンク内の行単位分割では、残した行数に合わせて `@@ -旧開始,旧行数 +新開始,新行数 @@` ヘッダも更新する）
3. `git apply --cached --check "$PATCH"` で検証後、`git apply --cached "$PATCH"` でステージし、`command rm -f "$PATCH"` で一時ファイルを削除してコミットする
4. 残りの変更を `git diff -- <file>` で確認し、単一種類になっていれば通常の `git add` でコミットする（まだ複数種類が残っていれば 1〜3 を繰り返す）

### 4. ステージ・秘匿情報チェック・コミット

コミットごとに以下を実行する:

1. **個別ステージ**: 意図しないファイル混入を避けるため `git add .` は使わず、対象パスを明示指定する。削除ファイルは `git rm -- <deleted-files>` を使い、`git add` には存在するファイルのみ渡す
2. **秘匿情報チェック**: 次のブロックでトークン・秘密鍵と、公開リポジトリでの個人情報・業務情報（`~/.config/push-denylist.txt`、1 行 1 語）を検査する（プロジェクトの `AGENTS.md` で明示承認された例外は除く）:

```bash
bash <<'SCRIPT'
set -euo pipefail
ADDED=$(git diff --staged --src-prefix=a/ --dst-prefix=b/ -U0 | grep '^+' | grep -vE '^\+\+\+ (b/|/dev/null)' || true)
FOUND=0

if printf '%s\n' "$ADDED" | grep -nE 'ghp_|gho_|github_pat_|CCIPAT_|xox[abprs]-|sk-[A-Za-z0-9]{20,}|PRIVATE KEY'; then
  echo "ERROR: potential secret token detected in staged diff" >&2
  FOUND=1
fi

VIS=$(gh repo view --json visibility -q .visibility 2>/dev/null || echo "UNKNOWN")
if [ "$VIS" = "PUBLIC" ] || [ "$VIS" = "UNKNOWN" ]; then
  DENYLIST="$HOME/.config/push-denylist.txt"
  if [ ! -f "$DENYLIST" ]; then
    echo "WARN: repository visibility=$VIS, denylist not found: $DENYLIST" >&2
  else
    PATTERNS=$(grep -v '^[[:space:]]*$' "$DENYLIST" || true)
    if [ -n "$PATTERNS" ]; then
      if printf '%s\n' "$ADDED" | grep -niF -f <(printf '%s\n' "$PATTERNS"); then
        echo "ERROR: denylist match detected in staged diff (visibility=$VIS)" >&2
        FOUND=1
      fi
    fi
  fi
fi

exit "$FOUND"
SCRIPT
```

- `WARN` が出た場合は、公開リポジトリで denylist 検査ができなかった旨を報告する（`UNKNOWN` で非公開と確定できる場合はその旨を判断材料として伝える）
- **検出時（exit 1）の対応**:
  - 該当ファイルのステージを解除し、コミットしない
  - 既に作成済みの別コミットがあっても Push（ステップ 5）は実行せずタスク全体を停止してユーザーに報告する（部分 push による漏洩防止）
  - 作成済みローカルコミットの `git reset` や、対象ファイルの編集・削除は行わずユーザーの判断に委ねる
3. **コミット作成**: チェック通過後、コミットメッセージを作成して `git commit` する

### 5. Push と検証

1. **リモート先行の確認（追跡ブランチあり時）**: `git rev-list --count 'HEAD..@{upstream}'` が `1` 以上なら、先に `GIT_EDITOR=true git pull --rebase --autostash` で取り込む。コンフリクトが発生した場合はユーザーに報告して中断する
2. **Push 実行**:
   - 追跡ブランチあり: `git push`（rejected 時は `GIT_EDITOR=true git pull --rebase --autostash` 後に再 push）
   - 追跡ブランチなし: `git push -u origin <branch>`
3. **結果検証**: パイプで終了コードを潰さず、`git push` の成功に加えて `git rev-parse HEAD` と `git rev-parse '@{u}'` の一致を確認してからコミット内容のサマリーを報告する

## エラー処理と安全策

| エラー | 対処 |
|--------|------|
| リモート先行でコンフリクト | 中断してユーザーに報告し、解消後に再 push |
| 認証エラー | 認証情報の確認を案内 |
| pre-commit / pre-push hook 失敗 | hook のエラー内容を報告し修正を提案 |

- `git push --force` は使わない（ユーザーから明示的に依頼された場合のみ、リスクを説明した上で実行する）。
