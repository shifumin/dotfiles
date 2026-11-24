---
name: search-x-posts
description: "X (Twitter) のポストを xAI Grok API（xsearch CLI）で検索する。「Xで検索」「ポストを検索」「ツイートを探して」「〜のXのポスト」「x search」等で使用。"
---

# X ポスト検索

`xsearch` CLI を使って X (Twitter) のポストを検索し、結果を Markdown で整形して報告する。

## 実行コマンド

```bash
mise exec --cd ~/ghq/github.com/shifumin/xsearch -- ruby xsearch.rb \
  [--user @HANDLE ...] \
  [--exclude @HANDLE ...] \
  [--from YYYY-MM-DD] \
  [--to YYYY-MM-DD] \
  [--images] [--videos] \
  [--system-prompt 'PROMPT'] \
  [--model MODEL] \
  [QUERY]
```

## オプション変換ルール

- **ユーザー (`--user` / `--exclude`)**: 複数指定可（`@` は省略可）。`--user` と `--exclude` は同時指定不可のため、両方求められたらユーザーへ確認する
- **期間 (`--from` / `--to`)**: 相対日付（「今週」「先月」等）や年省略日付（「2/20」等）は必ず `date` コマンドで現在日付を確認してから `YYYY-MM-DD` へ変換する
- **メディア**: 画像・動画の内容も含める依頼時のみ `--images` / `--videos` を付与
- **出力指示 (`--system-prompt`)**: 時系列・箇条書き等の指定がある場合のみ付与（既定で日本語回答される）
- **クエリ (`QUERY`)**: フィルタ（`--user` / `--exclude` / `--from` / `--to`）が 1 つ以上あれば省略可。クエリもフィルタも無ければ確認する

## 出力フォーマット

`xsearch` の出力テキストと引用元 URL を次へ整形する（フィルタ未使用時は「フィルタ」行を省略、0 件時は該当なしを報告）:

```markdown
## Xポスト検索結果

**検索クエリ**: {QUERY}
**フィルタ**: ユーザー: @handle / 期間: YYYY-MM-DD 〜 YYYY-MM-DD

{検索結果テキスト}

### 引用元
1. [URL1](URL1)
```

## エラー処理

| エラー | 対処 |
|---|---|
| `XAI_API_KEY が設定されていません` | `~/ghq/github.com/shifumin/xsearch/mise.local.toml` への設定を案内 |
| `API error (401)` | `https://console.x.ai` で API キーの再確認を案内 |
| `API error (429)` | レートリミットのため少し待ってから再試行 |
| クエリ・フィルタ未指定 / `--user` と `--exclude` 併用 | ユーザーへ条件の確認を依頼 |
