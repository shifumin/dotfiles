---
description: X (Twitter) のポストをxAI Grok APIで検索する。
  「Xで検索」「ポストを検索」「ツイートを探して」「〜のXのポスト」
  「x search」などのリクエストで使用。
---

# Xポスト検索

xsearch CLIを使用してX (Twitter) のポストを検索する。

## 共通設定

スクリプトパス: `~/ghq/github.com/shifumin/xsearch/`

実行: `mise exec --cd ~/ghq/github.com/shifumin/xsearch -- ruby xsearch.rb [options] QUERY`

## 処理フロー

1. ユーザー入力から検索意図を解釈
2. 自然言語をxsearchのオプションとクエリに変換
3. xsearch.rbを実行
4. 出力をMarkdown形式に整形して表示

## 自然言語からオプションへの変換

### ユーザー指定

| 自然言語表現 | オプション |
|-------------|-----------|
| 「shifuminのポスト」「@userの投稿」 | `--user @handle` |
| 「shifuminとrubyistのポスト」 | `--user @shifumin --user @rubyist` |
| 「botを除外」「〜以外のポスト」 | `--exclude @handle` |
| 「bot1とbot2を除外」 | `--exclude @bot1 --exclude @bot2` |

注意: `--user`と`--exclude`は同時使用不可。両方指定された場合はユーザーに確認する。

ハンドル名の`@`は省略されていても補完する（「shifumin」→`@shifumin`）。

### 日付指定

| 自然言語表現 | オプション |
|-------------|-----------|
| 「今週のポスト」 | `--from`を今週月曜日のYYYY-MM-DDに変換 |
| 「先週のポスト」 | `--from`を先週月曜日、`--to`を先週日曜日に変換 |
| 「今月のポスト」 | `--from`を今月1日に変換 |
| 「先月のポスト」 | `--from`/`--to`を先月の期間に変換 |
| 「2月1日以降」「2/1から」 | `--from 2026-02-01` |
| 「2月14日まで」「〜2/14」 | `--to 2026-02-14` |
| 「2月1日〜2月14日」 | `--from 2026-02-01 --to 2026-02-14` |

**重要**: 相対日付（「今週」「先月」等）や年省略の日付（「2/20」）を変換する前に、`date`コマンドで現在日付を確認すること。

### メディア理解

| 自然言語表現 | オプション |
|-------------|-----------|
| 「画像付きで」「画像も含めて」 | `--images` |
| 「動画付きで」「動画も含めて」 | `--videos` |
| 「画像と動画を含めて」 | `--images --videos` |

### システムプロンプト

明示的に出力形式や追加の指示がある場合のみ使用:

| 自然言語表現 | オプション |
|-------------|-----------|
| 「時系列でまとめて」 | `--system-prompt '時系列でまとめてください。'` |
| 「箇条書きでまとめて」 | `--system-prompt '箇条書きでまとめてください。'` |

通常は指定不要（デフォルトで日本語回答される）。

### クエリ

オプション以外の検索意図がクエリ文字列になる。

| 入力例 | クエリ |
|--------|--------|
| 「RubyのポストをXで検索」 | `Ruby` |
| 「shifuminのRailsに関するポスト」 | `Rails`（`--user @shifumin`と組み合わせ） |
| 「今週のAI関連のXのポスト」 | `AI`（`--from`と組み合わせ） |

## 実行コマンド

```bash
mise exec --cd ~/ghq/github.com/shifumin/xsearch -- ruby xsearch.rb \
  [--user @HANDLE] \
  [--exclude @HANDLE] \
  [--from YYYY-MM-DD] \
  [--to YYYY-MM-DD] \
  [--images] \
  [--videos] \
  [--system-prompt 'PROMPT'] \
  'QUERY'
```

## 出力の整形

xsearchの出力はテキスト形式のため、以下のMarkdown形式に変換:

```markdown
## Xポスト検索結果

**検索クエリ**: QUERY
**フィルタ**: ユーザー: @handle / 期間: YYYY-MM-DD 〜 YYYY-MM-DD

{検索結果テキスト}

### 引用元
1. [URL1](URL1)
2. [URL2](URL2)
```

| 項目 | ルール |
|------|--------|
| 検索条件 | 使用したオプションを「フィルタ」行にまとめて表示 |
| 検索結果テキスト | xsearchの出力テキスト部分をそのまま表示 |
| 引用元 | URLをMarkdownリンクに変換 |
| フィルタなし | 「フィルタ」行を省略 |
| 結果なし | 「該当するポストが見つかりませんでした」 |

## エラー処理

| エラーパターン | 原因 | 対処 |
|---------------|------|------|
| `XAI_API_KEY が設定されていません` | 環境変数未設定 | `~/ghq/github.com/shifumin/xsearch/mise.local.toml`にAPIキーを設定するよう案内 |
| `検索クエリを指定してください` | クエリ未指定 | ユーザーに検索したい内容を確認 |
| `allowed_x_handles と excluded_x_handles は同時に使用できません` | --userと--excludeの同時指定 | どちらか一方を使うようユーザーに確認 |
| `API error (401)` | APIキーが無効 | APIキーの再確認を案内（https://console.x.ai） |
| `API error (429)` | レートリミット | しばらく待ってからリトライ |
