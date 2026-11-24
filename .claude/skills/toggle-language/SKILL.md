---
name: toggle-language
description: "Claude Code のペルソナ（Output Style）を ON/OFF トグルする。「outputStyleトグル」「ペルソナ切り替え/オフ/オン」「キャラ設定をオフ」「素のClaude Codeに戻して」「toggle language」等で使用。language キー（応答言語）は変更しない。"
---

# Output Style トグル

`~/.claude/settings.json` の `outputStyle` キーを ON/OFF で切り替える（`language` キーは変更しないため、日本語応答は維持される）。反映は次の Claude Code セッションから。

## 手順

1. 同梱スクリプトを実行する:
   ```bash
   bash <SKILL_DIR>/scripts/toggle.sh
   ```
   - symlink 保持のため `readlink -f` で実体を解決し、`mktemp` + `command mv -f` で原子的に書き換える
   - バックアップ先は `~/.claude/.outputstyle_backup`（1 行プレーンテキスト）
   - `ERROR: SETTINGS_NOT_FOUND` / `ERROR: NO_BACKUP` は仕様どおり exit 1 で終了するため、リトライせず標準出力の文字列で分岐して報告する

2. 標準出力に応じて報告する:

| 出力 | 報告内容 |
|---|---|
| `TOGGLED: OFF (backup: {value})` | `outputStyle ({value}) を OFF にしました。次のセッションから素の Claude Code に戻ります。` |
| `TOGGLED: ON (restored: {value})` | `outputStyle ({value}) を ON に戻しました。次のセッションから反映されます。` |
| `ERROR: SETTINGS_NOT_FOUND` | `~/.claude/settings.json` が見つからないため、Claude Code の初期設定を案内 |
| `ERROR: NO_BACKUP` | 下記の手順を案内 |
| その他のエラー（`jq` 失敗等） | `settings.json` の JSON 形式を確認するよう案内 |

### `ERROR: NO_BACKUP` 時の案内

1. `outputStyle` 未設定（OFF）状態から ON へ戻そうとしたがバックアップが存在しない旨を伝える
2. 元の設定値が分かる場合: `~/.claude/settings.json` に `outputStyle` を手動追加すれば次回以降トグル可能
3. 不要な場合: すでにペルソナなし状態のため追加操作は不要
