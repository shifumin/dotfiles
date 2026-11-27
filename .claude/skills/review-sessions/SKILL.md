---
name: review-sessions
description: "直近のClaude Code・Codex・Antigravity全セッション（既定7日）を並列分析し、自作スキルの改善点と新規スキル候補を抽出・承認後に反映する。「セッション振り返り」「1週間のセッション精査」「スキル改善点」「新規スキル候補」「review-sessions」等で使用。単一セッション振り返り（k）とは別。"
---

# 期間内の全セッションからスキルの改善点を探す

期間内の全セッションからユーザーの訂正・スキル実行中の躓き・繰り返される手作業を横断抽出し、承認された改善点だけを自作スキルへ反映する。

## 引数

| 引数 | 意味 |
|------|------|
| なし | 直近 7 日（`7d`） |
| `14d` 等 | 直近 N 日 |
| `2026-11-01` | その日の 0:00 以降 |

## scope と扱い

| scope | 対象 | 扱い |
|-------|------|------|
| `own-global` / `new-global` | dotfiles の `.claude/skills/` | 承認後に作成・改善まで反映 |
| `own-vault` / `new-vault` | 個人 vault（`my-vault`）の `.claude/skills/` | 承認後に作成・改善まで反映 |
| `vendored` | 上流コピーのスキル | 直接編集せず上流報告 or 自作上書きを提案 |
| `team` / `new-team` / `external` | 業務・他リポジトリ・`~/.agents/skills`・有効なプラグイン | 提案のみ |
| `rules` / `hook` / `memory` | `AGENTS.md`・`.claude/rules/`・hooks・auto memory | スキルより適切なときに提案 |

## Phase 1 — 抽出

`SINCE` に引数（既定 `7d`）を入れて実行する。`python3` のシェル関数ラップを避けるため `/usr/bin/env python3 -B -I` で呼ぶ。

```bash
SINCE="7d" bash <<'SCRIPT'
set -eu
SKILL_DIR="$(/usr/bin/env python3 -B -I -c '
import os
for base in ("~/.claude/skills/review-sessions", "~/.agents/skills/review-sessions"):
    p = os.path.expanduser(base + "/SKILL.md")
    if os.path.exists(p):
        print(os.path.dirname(os.path.realpath(p)))
        break
')"
test -n "$SKILL_DIR"
OUT="$(mktemp -d "${TMPDIR:-/tmp}/review-sessions-XXXXXX")"
/usr/bin/env python3 -B -I "$SKILL_DIR/scripts/extract_sessions.py" --since "$SINCE" --out "$OUT"
/usr/bin/env python3 -B -I "$SKILL_DIR/scripts/list_skills.py" --index "$OUT/index.tsv" --out "$OUT/skills.tsv"
echo "SKILL_DIR=$SKILL_DIR"
echo "OUT=$OUT"
SCRIPT
```

- `extract_sessions.py` は会話のないセッション・サブエージェント（Codex / Antigravity）・`review-sessions` 自身の実行を除き、1 バッチ約 120KB で `OUT/batches.tsv` へ分割する
- 出力されたセッション数・プロジェクト内訳を 1 行でユーザーへ報告する（セッション 0 件なら `command rm -rf "$OUT"` で片付けて終了）

## Phase 2 — 並列分析

`OUT/batches.tsv` の 1 行につきサブエージェントを 1 体、全バッチ一括で並列起動する（Claude Code は Agent ツール `general-purpose`、他エージェントは対応するサブエージェント起動ツール）。プロンプトにダイジェストや `analyst.md` 本文を埋め込まず、次だけを渡す:

```
Read <SKILL_DIR>/references/analyst.md and follow the brief below its separator line.
BATCH_FILES=<その行のファイル名（カンマ区切り）>
SESSIONS_DIR=<OUT>/sessions
SKILLS_TSV=<OUT>/skills.tsv
```

親エージェントはダイジェストも `analyst.md` も読まない（コンテキストを集約・検証に残す）。

## Phase 3 — 集約と検証

全サブエージェントの完了後に実施する:

1. **統合**: 同一対象・同一原因の所見をまとめ、複数バッチの evidence を合算する
2. **最新状態と照合**: `own-global` / `own-vault` の `skill-fix` は現行の `SKILL.md` を読み、すでに解消済みなら落とす（`git -C <repo> log --since=<セッション日> -- <skill dir>` も参考にする）
3. **既存スキルとの重複確認**: 新規スキル候補が `OUT/skills.tsv` の既存スキルでカバーできるなら `skill-fix` へ組み替える
4. **優先順位付け**: 根拠セッション数が多いもの・ユーザー訂正が絡むものを上位に置く。1 セッションのみかつ `confidence: low` は落とす

## Phase 4 — 報告（チャットのみ・ファイル出力なし）

```
## 対象
期間・セッション数（ツール別・プロジェクト別）・バッチ数

## 反映する提案（dotfiles / personal vault）
| # | 種類 | 対象 | 内容 | なぜ（根拠） |
（優先度順に上へ。種類: 既存改善 / 新規スキル / ルール・hook）

## 提案のみ（チーム・組織・上流）
対象ごとに 1〜2 行＋提出先

## 見送ったもの
件数と理由の要約
```

所見がなければ、読んだセッション数とともにその旨を報告し、`command rm -rf "$OUT"` で一時ディレクトリを削除して終了する。

## Phase 5 — 承認と反映

判断は修正コストではなく効果で行う（`AGENTS.md` Principle 3）。「反映する提案をすべて反映していいか」を **1 回だけ**確認し、除外したい番号があれば受ける。

承認分を反映する手順:
1. 既存改善・新規作成は簡潔な文言を保つ（`AGENTS.md`「Rules and skills」）。評価ループや before/after は依頼時のみ
2. 編集・配置ルール:
   - シンボリックリンク先の `~/.claude/skills/...` ではなく、`OUT/skills.tsv` にあるリポジトリ実体パスを編集する
   - dotfiles で新規スキル追加時: `.claude/skills/<name>/` 作成後、`./setup.sh`（サンドボックス外）でリンク
   - 個人 vault で追加・改名・削除時: `.claude/skills/<name>/` 変更後、`.agents/sync-skills.sh` を実行して `.agents/` も一緒にコミット
3. 反映完了後、`command rm -rf "$OUT"` で一時ディレクトリを削除する（反映対象なしで終了するときも同様）
4. コミット前にユーザー確認を取り、今回変えたファイルだけを明示パスでステージ・Conventional Commits でコミットし、push は `push` スキルで行う

最後に反映結果を「対象・変えたこと・なぜ」の表で報告し、見送り分とユーザー側対応事項を添える。
