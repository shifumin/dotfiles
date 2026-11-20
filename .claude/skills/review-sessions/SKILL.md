---
name: review-sessions
description: 直近の Claude Code と Codex の全セッション（全プロジェクト、既定は7日）を精査し、自作スキルの改善点と新規スキル候補を見つけて、承認されたものを反映する。ユーザーの訂正・不満、スキル実行中の躓き、繰り返される手作業を兆候として拾い、サブエージェントで並列に分析する。「セッションを振り返って」「1週間のセッションを精査」「スキルの改善点を探して」「新しく作るべきスキルある？」「review-sessions」などのリクエストで使用。1セッションだけの振り返り（`k`）ではなく、期間内の全セッションを横断して見たいときに使う。
---

# 期間内の全セッションからスキルの改善点を探す

セッションの記録には、スキルの指示が足りなかった箇所（ユーザーの訂正、実行中の躓き）と、まだスキルになっていない繰り返し作業が残っている。このスキルはそれを期間単位でまとめて拾い、ユーザーが承認したものだけをスキルに反映する。

`k`（Kaizen）は今のセッション1つが対象で、スキル以外も同じ重みで見る。こちらは期間内の全セッションが対象で、スキルが中心になる。

## 引数

| 引数 | 意味 |
|------|------|
| なし | 直近7日 |
| `14d` など | 直近 N 日 |
| `2026-11-01` | その日の 0:00 以降 |

## 置き場所と扱い

所見の扱いは、直す対象がどこにあるかで決まる。

| scope | 置き場所 | 扱い |
|-------|----------|------|
| own-global / new-global | `~/ghq/github.com/shifumin/dotfiles/.claude/skills/` | 承認されたら作成・改善まで行う |
| own-vault / new-vault | `~/ghq/github.com/shifumin/my-vault/.claude/skills/` | 承認されたら作成・改善まで行う |
| vendored | dotfiles / my-vault にある上流のコピー | 直接は直さない。上流への報告か、自作スキルでの上書きを提案する |
| team / new-team / external | 業務リポジトリのスキル、`~/.agents/skills`（組織配布のスキルほか）、プラグイン | 提案だけ |
| rules / hook / memory | AGENTS.md、`.claude/rules/`、hooks、auto memory | スキルより適切なときに提案する |

dotfiles と my-vault はユーザーの承認だけで変えられるので反映まで進める。チームや組織のスキルは他の人の合意が要るので、提案に留める。

## Phase 1 — 抽出

システムプロンプトの「Scratchpad directory」を `SP` に書き写し、`SINCE` に引数（なければ `7d`）を入れて実行する。`python3` はシェル関数でラップされていて失敗することがあるので、`/usr/bin/env python3` で呼ぶ。

```bash
SP="<システムプロンプトの Scratchpad directory>" SINCE="7d" bash <<'SCRIPT'
set -eu
SKILL_DIR="$HOME/ghq/github.com/shifumin/dotfiles/.claude/skills/review-sessions"
OUT="$SP/review-sessions-$(date +%Y%m%d-%H%M%S)"
/usr/bin/env python3 -I "$SKILL_DIR/scripts/extract_sessions.py" --since "$SINCE" --out "$OUT"
PROJECT_ARGS=()
while IFS= read -r project; do
  PROJECT_ARGS+=(--project-dir "$HOME/ghq/github.com/$project")
done < <(awk -F'\t' 'NR>1{print $(3)}' "$OUT/index.tsv" | sort -u)
/usr/bin/env python3 -I "$SKILL_DIR/scripts/list_skills.py" --out "$OUT/skills.tsv" ${PROJECT_ARGS[@]+"${PROJECT_ARGS[@]}"}
echo "OUT=$OUT"
SCRIPT
```

`extract_sessions.py` は、各セッションから兆候に関わる部分（ユーザー発言、アシスタントの文、ツール呼び出し、失敗・拒否された結果）だけを抜いたダイジェストを `OUT/sessions/` に書く。会話のないセッション、Codex の guardian とサブエージェントのスレッド、`review-sessions` 自身を実行したセッションは除く。ダイジェストはプロジェクト順に、1バッチ約120KBで `OUT/batches.tsv` にまとめられる。

出力のセッション数とプロジェクト内訳を、1行でユーザーに伝える。

## Phase 2 — 並列分析

`batches.tsv` の1行につきサブエージェントを1体（Claude Code では Agent ツール、`general-purpose`）起動する。全バッチを1つのメッセージでまとめて起動し、並列に走らせる。プロンプトには本文を埋め込まず、次だけを渡す。

```
Read <SKILL_DIR>/references/analyst.md and follow the brief below its separator line.
BATCH_FILES=<その行のファイル名（カンマ区切り）>
SESSIONS_DIR=<OUT>/sessions
SKILLS_TSV=<OUT>/skills.tsv
```

親はダイジェストも analyst.md の本文も自分で読まない。コンテキストを集約と検証に残すためだ。

## Phase 3 — 集約と検証

全員の結果がそろってから行う。

1. **統合する**: 同じ対象・同じ原因の所見を1件にまとめ、evidence を足し合わせる。複数バッチで出た繰り返し作業は、ここで初めて新規スキル候補の強さが分かる
2. **今の状態と照らす**: own-global / own-vault の skill-fix は、対象の SKILL.md を読み、所見がまだ当てはまるかを確かめる。セッションの後に直っていれば落とす（`git -C <repo> log --since=<セッション日> -- <skill dir>` が手がかりになる）
3. **新規スキル候補を確かめる**: skills.tsv に同じ仕事をするスキルがないかを見る。あれば既存スキルの skill-fix に組み替える
4. **並べる**: 根拠のセッション数が多いもの、ユーザーの訂正が絡むものを上に置く。根拠が1セッションだけで confidence が low のものは落とす

## Phase 4 — 報告（チャット）

出力はチャットだけにする。ファイルには残さない。

```
## 対象
期間・セッション数（ツール別・プロジェクト別）・バッチ数

## 反映できる提案（dotfiles / my-vault）
| # | 判断 | 種類 | 対象 | 内容 | なぜ（根拠） |
（判断は やる / 見送る。やるものを優先度順に上へ。種類は 既存改善 / 新規スキル / ルール・hook。根拠はセッション数と代表例1つ）

## 提案のみ（チーム・組織・上流）
対象ごとに1〜2行。どこに出せばよいか（リポジトリ、上流）も添える

## 見送ったもの
件数と理由の要約だけ（直っていた、一回限り、など）
```

所見がなければ、読んだセッション数とともにそう伝える。

## Phase 5 — 承認と反映

判断は修正コストではなく効果で決める（AGENTS.md の Principle 3）。ユーザーには「やると判断したものを全部反映していいか」を1回だけ確認し、外したいものがあれば番号で受ける。

承認されたものを、1件ずつ次の手順で反映する。

1. 既存スキルの改善も新規作成も skill-creator の書き方に従う（`k` と同じ）。評価ループと before/after は頼まれたときだけ行う。文言は短く保つ（AGENTS.md の「Rules and skills」）
2. 置き場所の規則に従う
   - dotfiles の新規スキル: `.claude/skills/<name>/` に作り、`./setup.sh` でリンクする（スキルはディレクトリを作るだけで自動リンクされる）。`~/.claude/skills/` はサンドボックスで書き込み不可なので、`setup.sh` はサンドボックス外で実行する
   - my-vault のスキル: `.claude/skills/<name>/` が唯一の正本。追加・改名・削除をしたら `.agents/sync-skills.sh` を実行し、`.agents/` も一緒にコミットする（my-vault の AGENTS.md「Skills」）
   - Write / Edit はシンボリックリンクを通して書けないので、`~/.claude/skills/...` ではなくリポジトリのパスを編集する
3. コミットは、ユーザーの確認を取ってから、今回変えたファイルだけをパス指定で行う。既存の未コミット差分には触れない。メッセージは Conventional Commits（例: `feat(skills): add <name>`）。push は push スキルで行う（公開リポジトリの検査が入る）

最後に、反映したものを「対象・変えたこと・なぜ」の表で報告する。見送ったものと、ユーザーに頼むこと（環境の修正など）も添える。
