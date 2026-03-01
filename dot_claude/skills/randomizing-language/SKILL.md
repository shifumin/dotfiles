---
description: Claude Codeのlanguage設定をランダムに変更する。
  「language変更」「language設定変更」「ランダムlanguage」などのリクエストで使用。
---
# language設定ランダム変更

Obsidian Vaultに保存されたlanguage設定からランダムに1つ選び、`~/.claude/settings.json`の`language`キーを更新する。

## 処理フロー

以下のbashスクリプトを実行し、ランダム選択からsettings.json更新・chezmoi同期まで一括で行う:

```bash
bash <<'SCRIPT'
set -euo pipefail

VAULT_DIR="/Users/shifumin/ghq/github.com/shifumin/my-vault"
INDEX_FILE="${VAULT_DIR}/001_note/Claude Codeのlanguage設定.md"
SETTINGS_FILE="${HOME}/.claude/settings.json"

# インデックスノートから [[...]] 内のノート名を配列に格納（bash 3.2互換）
NOTES=()
while IFS= read -r line; do
  NOTES+=("$line")
done < <(grep -o '\[\[[^]]*\]\]' "${INDEX_FILE}" | sed 's/\[\[//;s/\]\]//')

if [ ${#NOTES[@]} -eq 0 ]; then
  echo "ERROR: NO_NOTES_FOUND"
  exit 1
fi

# ランダムに1つ選択
RANDOM_INDEX=$((RANDOM % ${#NOTES[@]}))
SELECTED="${NOTES[$RANDOM_INDEX]}"

# 選択ノートからコードブロック内のテキストを抽出
NOTE_FILE="${VAULT_DIR}/001_note/${SELECTED}.md"
LANGUAGE_VALUE=$(sed -n '/^```$/,/^```$/{ /^```$/d; p; }' "${NOTE_FILE}")

if [ -z "${LANGUAGE_VALUE}" ]; then
  echo "ERROR: NO_CODEBLOCK: ${NOTE_FILE}"
  exit 1
fi

# settings.jsonのlanguageキーだけを更新
jq --arg lang "${LANGUAGE_VALUE}" '.language = $lang' "${SETTINGS_FILE}" > "${SETTINGS_FILE}.tmp" \
  && mv "${SETTINGS_FILE}.tmp" "${SETTINGS_FILE}"

# chezmoi管理ファイルのためソースに反映
chezmoi add "${SETTINGS_FILE}"

echo "SELECTED: ${SELECTED}"
SCRIPT
```

## 結果報告

bashスクリプトの出力をパースして報告する:

| 出力 | 対応 |
|------|------|
| `SELECTED: {ノート名}` | 成功。ノート名から「を模倣するClaude Codeのlanguage設定」を除去してキャラクター名を表示 |
| `ERROR: NO_NOTES_FOUND` | エラー処理へ |
| `ERROR: NO_CODEBLOCK: {path}` | エラー処理へ |

成功時の報告フォーマット:

```markdown
**{キャラクター名}** のlanguage設定に変更しました。次のセッションから反映されます。
```

## エラー処理

| エラーパターン | 対処 |
|---------------|------|
| `NO_NOTES_FOUND` | インデックスノートにリンクが見つからない。ファイルパスを確認してユーザーに報告 |
| `NO_CODEBLOCK` | 選択ノートにコードブロックがない。ノートの形式を確認するよう案内 |
| `jq: error` | settings.jsonの形式が不正。バックアップから復元を案内 |
| `settings.json が存在しない` | `~/.claude/settings.json`が見つからない。Claude Codeの初期設定を案内 |
