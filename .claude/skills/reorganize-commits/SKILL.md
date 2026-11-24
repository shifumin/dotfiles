---
name: reorganize-commits
description: "ブランチのコミット履歴をレビューしやすい「独立して revert できる意図」単位へ再構成し、backup ブランチと tree 一致検証のうえ承認後に force-with-lease push する。「コミット整理/まとめ」「履歴を綺麗に」「squash」「分け直して」「reorganize-commits」等で使用。対象外: 未コミット変更の新規コミットや既存履歴のそのまま push（push スキル）。"
---

# コミット履歴の再構成

作業ログとして散らばったブランチのコミット群を、最終ツリーを 1 バイトも変えずに意図単位の履歴へ組み直す。計画テキストではなく**実物を先に組んで提示してから** push の承認を取る（backup ブランチでいつでも元へ戻せる）。

```text
事前チェック → base 決定 → レビュー確認 → backup 作成 → reset
  → 意図ごとに再コミット → tree 一致検証 → 実物提示・承認 → push
```

## 1. 事前チェック

```bash
BRANCH=$(git branch --show-current)
[ -n "$BRANCH" ] || { echo "detached HEAD のため中断"; exit 1; }
git status --porcelain -uno 2>/dev/null
```

- 追跡済みファイルに出力があれば中断し、`git stash` またはコミット後に再実行してもらう（`-uno` は無関係な未追跡ファイル無視、`2>/dev/null` は読み取り不可ファイル `.pem`/`.key` のエラー抑止）。
- 引数で別 PR 番号・URL が渡された場合は勝手に切り替えず、`gh pr checkout <番号>` で切り替えてよいか確認する。

## 2. base を決める

PR があればその base、無ければデフォルトブランチとの merge-base を起点にする。

```bash
BASE_REF=$(gh pr view --json baseRefName -q .baseRefName 2>/dev/null || true)
if [ -z "$BASE_REF" ]; then
  BASE_REF=$(git symbolic-ref --quiet refs/remotes/origin/HEAD 2>/dev/null | sed 's|refs/remotes/origin/||')
fi
if [ -z "$BASE_REF" ]; then
  BASE_REF=$(gh repo view --json defaultBranchRef -q .defaultBranchRef.name 2>/dev/null || true)
fi
if [ -z "$BASE_REF" ]; then
  for cand in main master; do
    if git show-ref --verify --quiet "refs/remotes/origin/$cand"; then BASE_REF="$cand"; break; fi
  done
fi
[ -n "$BASE_REF" ] || { echo "base ブランチを特定できません"; exit 1; }

git fetch origin "$BASE_REF"
BASE=$(git merge-base HEAD "origin/$BASE_REF")
echo "base: $BASE_REF ($BASE)"
git log --oneline --no-merges "$BASE..HEAD"
```

- 対象コミット数と base を提示する。件数が不自然に多い（3 桁等）場合は base 誤判定を疑って止める。
- `git log --merges "$BASE..HEAD"` に出力があれば、再構成後に履歴が直線になる旨を先に伝える。

## 3. レビューコメントの確認

```bash
gh pr view --json reviews,comments,reviewThreads -q \
  '"reviews: \(.reviews | length) / threads: \(.reviewThreads | length) / comments: \(.comments | length)"' 2>/dev/null || true
```

（PR 読み取り専用ツールがある環境ではそれを使ってもよい。）1 件以上あれば「force push でインラインコメントの行紐付きが崩れ得るが進めるか」を確認する。

## 4. backup を作り lease を固定する

```bash
BACKUP="backup/${BRANCH}-$(date +%Y%m%d-%H%M%S)"
git branch "$BACKUP"
LEASE=""
if git ls-remote --exit-code --heads origin "$BRANCH" >/dev/null 2>&1; then
  git fetch origin "$BRANCH"
  LEASE=$(git rev-parse "origin/$BRANCH")
  echo "lease: $LEASE"
  if ! git merge-base --is-ancestor "$LEASE" "$BACKUP"; then
    echo "リモートにローカル未取り込みのコミットがあります。取り込み方針を確認してください"
    exit 1
  fi
else
  echo "リモート未登録の新規ブランチ（通常 push -u 対象）"
fi
```

- リモートに未取り込みのコミットがある場合は止めてユーザーに確認する。
- `$BACKUP` は検証と復旧に使い、最後にブランチ名を伝えて削除（`git branch -D "$BACKUP"`）はユーザーに任せる。

## 5. index を解除して変更一覧を得る

```bash
git reset "$BASE"
while IFS= read -r -d '' f; do
  git add -N -- "$f"
done < <(git diff -z --name-only --diff-filter=A "$BASE" "$BACKUP")
git diff --name-status "$BASE" "$BACKUP"
```

- `git reset "$BASE"` で作業ツリーを最終状態のまま残し、ブランチで新規追加されたファイルだけを `-z` 経由で `git add -N` する（`git add -N .` は無関係な未追跡ファイルを巻き込むため禁止）。
- 途中で打ち消し合った変更はこの時点で差分に現れず自動除去される。

## 6. 分割単位を決める

プロジェクトに `.agents/skills/commit/SKILL.md` または `.claude/skills/commit/SKILL.md` があれば**必ず読んで**その規約を優先する。無ければ Conventional Commits と「1 コミット = 独立して revert できる 1 つの意図」を基準にする。

**再構成の 3 原則**:
1. **リファクタと振る舞いの変更は必ず分ける**（振る舞い不変の確認と仕様確認を混ぜない）
2. **実装とその spec は同じコミットに入れる**（プロジェクト規約が分離を求める場合を除く）
3. **機械的差分は独立させて末尾に置く**（`rubocop -a`、`schema.rb`、`package_todo.yml`、生成物、フォーマッタ差分）

**並び順（読む順）**: 土台（マイグレーション・スキーマ・定数・型） → 中核ロジック＋spec → 呼び出し側・配線 → 付随（i18n・docs・設定） → 機械的差分。

**数**: 先に目標数を決めず、意図の数に合わせる。12 を超えたら作業の時系列が残っていないか見直す。

## 7. 意図ごとに再コミットする

```bash
git add -- path/to/a path/to/b
git commit -m "..."
```

- **本文付きコミットメッセージ**: 一時ファイルに書いて渡し、コミット後に消す（zsh で heredoc + `&&` するとタイトル行が壊れるため）。
  ```bash
  MSG=$(mktemp)
  cat >| "$MSG" <<'EOF'
  feat: ...

  Why ...
  EOF
  git commit -F "$MSG" && command rm -f "$MSG"
  ```
- 元メッセージは意図を拾うヒントに留め、まとめた後の diff を見て「なぜそうしたか」を新しく書く。
- **1 ファイルに複数意図が混在するとき**: そのコミット時点であるべき内容へ編集して `git add` する。互いに依存する hunk は引き離さず、迷えばファイル単位に寄せる。hunk 分割したファイルは最後に `git checkout "$BACKUP" -- <file>` で最終状態へ戻し、`git status --porcelain -uno 2>/dev/null` で取りこぼしが無いか確認する。
- **pre-commit フック（husky / lint-staged + mise）**: `node` 不在等で失敗したら `mise exec -- git commit ...` へ切り替える（サンドボックス制約がある環境では解除して実行）。

## 8. tree 一致を検証する（必須）

```bash
git diff --stat "$BACKUP" HEAD
git diff --quiet "$BACKUP" HEAD || { echo "最終ツリーに差分あり"; exit 1; }
```

差分が 1 バイトでもあれば修正するか `git reset --hard "$BACKUP"` でやり直す。一致するまで先へ進まない。

## 9. 実物を提示して承認を取る

```bash
git log --stat --oneline "$BASE..HEAD"
```

出力をそのまま提示し、以下を添えて push の承認を取る（**承認なしに push しない**）:
- 元のコミット数 → 新しいコミット数
- tree 一致検証 OK
- backup ブランチ名（気に入らなければ `git reset --hard "$BACKUP"` で元に戻せる旨も併記）
- 既存レビューコメント件数（1 件以上の場合）

## 10. push と一致確認

- **既存リモートブランチ（`LEASE` あり）**: 履歴書き換えの安全策として、手順 4 で固定した SHA を使ったコマンドをユーザーへ提示し実行してもらう（`!` シェル実行に対応した環境では先頭に `! ` を付けて提示可。素の `--force` や push 直前の再 `fetch` は他者の先行 push を消す恐れがあるため禁止）。
  ```bash
  git push --force-with-lease="<branch>:<LEASE>" origin "<branch>"
  ```
- **新規ブランチ（`LEASE` 空）**: 承認後、通常の `git push -u origin "<branch>"` を行う。

push 完了後、一致を確認して完了報告する:

```bash
[ "$(git rev-parse HEAD)" = "$(git rev-parse '@{u}')" ] && echo "OK: $(git rev-parse --short HEAD)"
```

失敗時はリモートに別変更が入った可能性を伝え、勝手に押し切らない。

## 失敗時の復旧

どの段階でも backup ブランチから 1 コマンドで戻せる（force push 後も同じ手順＋再度 `--force-with-lease`）:

```bash
git reset --hard "$BACKUP"
```
