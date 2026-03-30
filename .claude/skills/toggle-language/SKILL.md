---
description: Claude Codeのlanguage設定をトグルする（ON/OFF切り替え）。
  「languageトグル」「language切り替え」「languageをオフ」「languageをオン」「ペルソナ切り替え」
  「language OFF」「language ON」「toggle language」「言語設定トグル」などのリクエストで使用。
  language設定を一時的に無効にしたい、または元に戻したい場合に必ずこのスキルを使う。
---
# language設定トグル

`~/.claude/settings.json`の`language`キーをON/OFFでトグルする。
OFFにする際は現在の値をバックアップし、ONに戻す際はバックアップから復元する。

## 処理フロー

以下のbashスクリプトを実行する:

```bash
bash <<'SCRIPT'
set -euo pipefail

SETTINGS_FILE="${HOME}/.claude/settings.json"
BACKUP_FILE="${HOME}/.claude/.language_backup"

if [[ ! -f "${SETTINGS_FILE}" ]]; then
  echo "ERROR: SETTINGS_NOT_FOUND"
  exit 1
fi

# language キーの値を取得（存在しなければ null）
CURRENT=$(jq -r '.language // empty' "${SETTINGS_FILE}")

if [[ -n "${CURRENT}" ]]; then
  # ON -> OFF: バックアップしてからキーを削除
  printf '%s' "${CURRENT}" > "${BACKUP_FILE}"
  jq 'del(.language)' "${SETTINGS_FILE}" > "${SETTINGS_FILE}.tmp" \
    && mv "${SETTINGS_FILE}.tmp" "${SETTINGS_FILE}"
  echo "TOGGLED: OFF"
else
  # OFF -> ON: バックアップから復元
  if [[ ! -f "${BACKUP_FILE}" ]]; then
    echo "ERROR: NO_BACKUP"
    exit 1
  fi
  RESTORED=$(cat "${BACKUP_FILE}")
  jq --arg lang "${RESTORED}" '.language = $lang' "${SETTINGS_FILE}" > "${SETTINGS_FILE}.tmp" \
    && mv "${SETTINGS_FILE}.tmp" "${SETTINGS_FILE}"
  echo "TOGGLED: ON"
fi
SCRIPT
```

## 結果報告

bashスクリプトの出力をパースして報告する:

| 出力 | 対応 |
|------|------|
| `TOGGLED: OFF` | language設定をOFFにした。次のセッションから反映される |
| `TOGGLED: ON` | language設定をONに戻した。次のセッションから反映される |
| `ERROR: SETTINGS_NOT_FOUND` | エラー処理へ |
| `ERROR: NO_BACKUP` | エラー処理へ |

成功時の報告フォーマット:

```
TOGGLED: OFF の場合 → "language設定をOFFにしました。次のセッションから反映されます。"
TOGGLED: ON の場合  → "language設定をONに戻しました。次のセッションから反映されます。"
```

## エラー処理

| エラーパターン | 対処 |
|---------------|------|
| `SETTINGS_NOT_FOUND` | `~/.claude/settings.json`が見つからない。Claude Codeの初期設定を案内 |
| `NO_BACKUP` | バックアップが存在しないため復元できない。先にlanguage設定がある状態でOFFにして保存する必要がある旨を案内 |
| `jq: error` | settings.jsonの形式が不正。ファイルの確認を案内 |
