---
description: Codex CLIを使用してコードの分析・提案・レビューを行う。
  「Codexで分析」「Codexに聞いて」「Codexでレビュー」「codex exec」「codex review」
  「Codexでコードレビュー」「Codexに質問」などのリクエストで使用。
---
# Codex CLI操作

Codex CLI (`codex`) を使用して、コードベースの分析・提案・コード生成・レビューを行う。

## 操作の判定

| 操作 | トリガーとなる表現例 | 使用コマンド |
|------|---------------------|-------------|
| exec | 「Codexで分析」「Codexに聞いて」「Codexでコード生成」「codex exec」 | `codex exec` |
| review | 「Codexでレビュー」「Codexでコードレビュー」「codex review」 | `codex review` |

---

## 共通設定

| 項目 | 内容 |
|------|------|
| CLIパス | `/opt/homebrew/bin/codex` |
| モデル | `~/.codex/config.toml`のデフォルトを使用 |
| タイムアウト | 600000ms（10分） |

---

## exec

### 処理フロー

1. ユーザー入力からCodexに送るプロンプトを構成
2. 作業ディレクトリを決定（ユーザー指定 > gitリポジトリルート > カレントディレクトリ）
3. プロンプト末尾に「具体的な提案・修正案・コード例まで自主的に出力してください。」を付加
4. `codex exec`をBashツールで実行（timeout: 600000）
5. 出力結果をユーザーに報告

### 実行コマンド

短いプロンプトの場合:
```bash
/opt/homebrew/bin/codex exec --full-auto --sandbox read-only --cd {ディレクトリパス} "{プロンプト} 具体的な提案・修正案・コード例まで自主的に出力してください。"
```

長いプロンプト・特殊文字を含む場合（stdinから渡す）:
```bash
/opt/homebrew/bin/codex exec --full-auto --sandbox read-only --cd {ディレクトリパス} - <<'PROMPT'
{プロンプト}
具体的な提案・修正案・コード例まで自主的に出力してください。
PROMPT
```

| オプション | 用途 |
|-----------|------|
| `--full-auto` | 非対話実行（承認不要 + サンドボックス） |
| `--sandbox read-only` | 読み取り専用 |
| `--cd {dir}` | 作業ディレクトリ指定 |

---

## review

### 処理フロー

1. レビュー対象を決定
2. 作業ディレクトリを決定
3. 対象ディレクトリに`cd`して`codex review`を実行（timeout: 600000）
4. レビュー結果をユーザーに報告

### レビュー対象の決定

| ユーザーの指示 | オプション |
|--------------|-----------|
| 「未コミットの変更をレビュー」 | `--uncommitted` |
| 「mainとの差分をレビュー」 | `--base main` |
| 「特定コミットをレビュー」 | `--commit {SHA}` |
| 指定なし | オプションなし |

### 実行コマンド

**注意**: `codex review`は`--cd`を受け付けないため、`cd`で移動してから実行する。

```bash
cd {ディレクトリパス} && /opt/homebrew/bin/codex review [--uncommitted] [--base {ブランチ名}] [--commit {SHA}] ["{カスタム指示}"]
```

---

## エラー処理

| エラーパターン | 原因 | 対処 |
|---------------|------|------|
| `Not authenticated` / `unauthorized` | 認証切れ | `codex login`の実行を案内 |
| タイムアウト（10分超過） | 処理が重い | プロンプトを分割して再実行を提案 |
| `not a git repository` | gitリポジトリ外 | 正しいリポジトリパスを指定 |
| `command not found` | CLI未インストール | パスを確認 |
| サンドボックスエラー | 書き込み操作の要求 | `--sandbox workspace-write`の使用を提案 |
| `rate limit` / `429` | レートリミット | 待ってからリトライ |
