---
description: Claude Codeのペルソナ（Output Style）をトグルする（ON/OFF切り替え）。
  「outputStyleトグル」「output style切り替え」「ペルソナ切り替え」「ペルソナをオフ」「ペルソナをオン」
  「キャラをオフ」「キャラ設定をオフ」「素のClaude Codeに戻して」「言語設定トグル」
  「languageトグル」「language切り替え」「toggle language」「toggle output style」などのリクエストで使用。
  ペルソナを一時的に無効化して素のClaude Codeに戻したい場合、または再度有効化したい場合に必ずこのスキルを使う。
---
# Output Style トグル

`~/.claude/settings.json`の`outputStyle`キーをON/OFFでトグルする。
OFFにする際は現在の値をバックアップし、ONに戻す際はバックアップから復元する。

`language`キー（例: `"日本語"`）はペルソナとは別の役割（応答言語の指定）を持つため触らない。
これにより、ペルソナをOFFにしても日本語応答は維持される。

## 処理フロー

以下のbashスクリプトを実行する:

```bash
bash <<'SCRIPT'
set -euo pipefail

SETTINGS_FILE="${HOME}/.claude/settings.json"
BACKUP_FILE="${HOME}/.claude/.outputstyle_backup"

if [[ ! -f "${SETTINGS_FILE}" ]]; then
  echo "ERROR: SETTINGS_NOT_FOUND"
  exit 1
fi

# outputStyle キーの値を取得（存在しなければ null）
CURRENT=$(jq -r '.outputStyle // empty' "${SETTINGS_FILE}")

if [[ -n "${CURRENT}" ]]; then
  # ON -> OFF: バックアップしてからキーを削除
  printf '%s' "${CURRENT}" > "${BACKUP_FILE}"
  jq 'del(.outputStyle)' "${SETTINGS_FILE}" > "${SETTINGS_FILE}.tmp" \
    && mv "${SETTINGS_FILE}.tmp" "${SETTINGS_FILE}"
  echo "TOGGLED: OFF (backup: ${CURRENT})"
else
  # OFF -> ON: バックアップから復元
  if [[ ! -f "${BACKUP_FILE}" ]]; then
    echo "ERROR: NO_BACKUP"
    exit 1
  fi
  RESTORED=$(cat "${BACKUP_FILE}")
  jq --arg style "${RESTORED}" '.outputStyle = $style' "${SETTINGS_FILE}" > "${SETTINGS_FILE}.tmp" \
    && mv "${SETTINGS_FILE}.tmp" "${SETTINGS_FILE}"
  echo "TOGGLED: ON (restored: ${RESTORED})"
fi
SCRIPT
```

## 結果報告

bashスクリプトの出力をパースして報告する:

| 出力 | 対応 |
|------|------|
| `TOGGLED: OFF (backup: {value})` | outputStyleをOFFにした。バックアップ値を含めて報告 |
| `TOGGLED: ON (restored: {value})` | outputStyleをONに戻した。復元値を含めて報告 |
| `ERROR: SETTINGS_NOT_FOUND` | エラー処理へ |
| `ERROR: NO_BACKUP` | エラー処理へ |

成功時の報告フォーマット:

```
TOGGLED: OFF の場合 → "outputStyle ({value}) をOFFにしました。次のセッションから素のClaude Codeに戻ります。"
TOGGLED: ON の場合  → "outputStyle ({value}) をONに戻しました。次のセッションから反映されます。"
```

## エラー処理

| エラーパターン | 対処 |
|---------------|------|
| `SETTINGS_NOT_FOUND` | `~/.claude/settings.json`が見つからない。Claude Codeの初期設定を案内 |
| `NO_BACKUP` | バックアップが存在しないため復元できない。先にoutputStyle設定がある状態でOFFにして保存する必要がある旨を案内 |
| `jq: error` | settings.jsonの形式が不正。ファイルの確認を案内 |

## 補足

- `language`キーはこのスキルの対象外。応答言語のみを切り替えたい場合は`settings.json`を直接編集する
- バックアップは`~/.claude/.outputstyle_backup`に保存される（プレーンテキスト1行）
- 反映タイミング: 次のClaude Codeセッションから（現在のセッションには影響しない）
