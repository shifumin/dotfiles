---
description: Gmailのメール検索・取得・迷惑メール管理・カテゴリタブ一括整理を行う。
  ユーザーがメールに関する操作を求めたら必ずこのスキルを使用すること。
  「メールを検索」「〜からのメール」「〜のメールある？」「未読メール確認」「メール何通来てる？」
  「迷惑メールを削除」「スパムを整理」
  「Socialタブを整理」「プロモーションを整理」「ソーシャルメールをアーカイブ」「SNS通知を既読に」
  「最近Amazonで何か買ったっけ」「請求書のメール探して」のような間接的なメール確認リクエストにも対応。
---

# Gmail操作

## 操作の判定

| 操作 | トリガーとなる表現例 | 使用スクリプト |
|------|---------------------|---------------|
| 検索 | 「メールを検索」「〜からのメール」「〜のメールを探して」 | gmail_searcher.rb |
| 取得 | 「メールの詳細」「メールを開いて」「本文を見せて」 | gmail_fetcher.rb |
| スパム管理 | 「迷惑メールを削除」「スパムを整理」「迷惑メール確認」 | gmail_searcher.rb + gmail_spam_trasher.rb |
| カテゴリタブ整理 | 「Socialタブを整理」「プロモーションを整理」「SNS通知を既読に」 | gmail_searcher.rb + gmail_batch_modifier.rb |

---

## 共通設定

スクリプトパス: `~/ghq/github.com/shifumin/gmail-tools-ruby/`

実行: `mise exec --cd ~/ghq/github.com/shifumin/gmail-tools-ruby -- ruby <script>.rb [options]`

---

## メール検索

### 処理フロー

1. ユーザー入力から検索意図を解釈
2. 自然言語をGmail検索クエリに変換
3. gmail_searcher.rbを実行
4. JSON出力をMarkdown形式に整形して表示

### 自然言語からGmail検索クエリへの変換

| 自然言語表現 | Gmail検索クエリ |
|-------------|----------------|
| 「Amazonからのメール」 | `from:amazon.co.jp` |
| 「〜さんへのメール」 | `to:email@example.com` |
| 「件名に請求書を含む」 | `subject:請求書` |
| 「今週のメール」 | `newer_than:7d` |
| 「先月のメール」 | `newer_than:1m` |
| 「今年のメール」 | `after:YYYY/01/01`（現在年を使用） |
| 「1月1日以降」 | `after:YYYY/01/01` |
| 「12月31日まで」 | `before:YYYY/12/31` |
| 「添付ファイル付き」 | `has:attachment` |
| 「PDFが添付されている」 | `filename:pdf` |
| 「未読メール」 | `is:unread` |
| 「ラベル〜のメール」 | `label:ラベル名` |
| 「重要なメール」 | `is:important` |
| 「スター付き」 | `is:starred` |

### 複合クエリの組み立て

複数の条件はスペースで連結（AND検索）:
- 「Amazonからの今月のメール」→ `from:amazon.co.jp newer_than:1m`
- 「添付ファイル付きの請求書」→ `subject:請求書 has:attachment`

### 実行コマンド

```bash
mise exec --cd ~/ghq/github.com/shifumin/gmail-tools-ruby -- ruby gmail_searcher.rb \
  --query='<検索クエリ>' \
  [--max-results=N] \
  [--no-body] \
  [--include-html]
```

### オプション

| オプション | 説明 |
|-----------|------|
| `--query` | **必須** Gmail検索クエリ |
| `--max-results` | 最大取得件数（デフォルト: 10） |
| `--no-body` | 本文を除外（高速化） |
| `--include-html` | HTML本文を取得 |
| `--include-spam-trash` | スパム・ゴミ箱のメールを検索対象に含める |

### 出力の整形

JSON出力を以下のMarkdown形式に変換:

```markdown
## メール検索結果（N件）

検索クエリ: `<query>`

### 1. 件名
- **From**: 送信者名 <email@example.com>
- **Date**: YYYY-MM-DD HH:MM
- **ID**: `message_id`

> snippet（本文プレビュー）

---
```

| 項目 | ルール |
|------|--------|
| 日付 | RFC2822 → `YYYY-MM-DD HH:MM` |
| 送信者 | `"Name" <email>` 形式をそのまま表示 |
| snippet | blockquote（`>`）で表示 |
| 本文 | 要求時のみ表示（500文字超は省略） |
| HTMLメール | `plain_text`が空の場合、`--include-html`で再取得 |
| 0件 | 「該当するメールが見つかりませんでした」 |
| ラベル | 日本語表示（変換表はreference.md参照） |

---

## メール取得

### 処理フロー

1. ユーザーからメッセージIDを取得（検索結果から選択）
2. gmail_fetcher.rbを実行
3. JSON出力をMarkdown形式に整形して表示

### 実行コマンド

```bash
mise exec --cd ~/ghq/github.com/shifumin/gmail-tools-ruby -- ruby gmail_fetcher.rb \
  --message-id='<メッセージID>' \
  [--format=full|minimal|metadata|raw]
```

### オプション

| オプション | 説明 |
|-----------|------|
| `--message-id` | **必須** メッセージID |
| `--format` | 取得形式: full/minimal/metadata/raw（デフォルト: full） |

### 出力の整形

```markdown
## メール詳細

- **件名**: 件名
- **From**: 送信者
- **To**: 宛先
- **Date**: YYYY-MM-DD HH:MM
- **Labels**: ラベル1, ラベル2

### 本文

本文テキスト...

### 添付ファイル（N件）

| ファイル名 | 種類 | サイズ |
|-----------|------|-------|
| file.pdf | application/pdf | 1.2 MB |
```

---

## バッチ操作（スパム管理・カテゴリタブ整理）

### 処理フロー（共通）

1. **一覧取得**: `gmail_searcher.rb`で対象メールを一覧表示
2. **ユーザー確認**: テーブル形式で表示し、操作の同意を得る
3. **実行**: 確認後、操作に応じたスクリプトで処理

### 操作別パラメータ

| 操作 | 検索クエリ | 追加オプション | 実行スクリプト |
|------|-----------|---------------|---------------|
| スパム管理 | `label:spam` | `--include-spam-trash`**（必須）** | `gmail_spam_trasher.rb` |
| Socialタブ整理 | `category:social is:unread` | - | `gmail_batch_modifier.rb --remove-labels=INBOX,UNREAD` |
| Promotionsタブ整理 | `category:promotions is:unread` | - | `gmail_batch_modifier.rb --remove-labels=INBOX,UNREAD` |
| 汎用ラベル操作 | 任意のGmailクエリ | - | `gmail_batch_modifier.rb --remove-labels=... --add-labels=...` |

他のカテゴリ（Updates、Forums）も同様に `category:<name> is:unread` で対応可能。
汎用ラベル操作では `--add-labels` でラベル付与、`--remove-labels` でラベル削除が可能（少なくとも一方は必須）。例: 特定メールに一括でラベルを付ける、特定条件のメールをまとめてアーカイブする等。

### Step 1: 一覧取得

```bash
mise exec --cd ~/ghq/github.com/shifumin/gmail-tools-ruby -- ruby gmail_searcher.rb \
  --query='<検索クエリ>' \
  --no-body \
  --max-results=50 \
  [--include-spam-trash]
```

### Step 2: ユーザーへの表示と確認

JSON出力をテーブル形式に変換して表示:

```markdown
## <操作名>一覧（N件）

| # | 送信者 | 件名 | 日時 |
|---|--------|------|------|
| 1 | sender@example.com | Subject line | 2026-02-10 15:30 |

これらのメール（N件）を<操作（ゴミ箱に移動/アーカイブして既読に）>しますか？
```

| 項目 | ルール |
|------|--------|
| 日付 | RFC2822 → `YYYY-MM-DD HH:MM` |
| 確認 | **必ずユーザーの明示的な同意を得てから実行** |
| 0件 | 「対象のメールはありません。」と表示して終了 |

### Step 3: 実行

**スパム管理** — `gmail_spam_trasher.rb`:

```bash
mise exec --cd ~/ghq/github.com/shifumin/gmail-tools-ruby -- ruby gmail_spam_trasher.rb \
  [--max-results=N] [--dry-run] [--batch-size=N]
```

**カテゴリタブ整理** — `gmail_batch_modifier.rb`:

```bash
mise exec --cd ~/ghq/github.com/shifumin/gmail-tools-ruby -- ruby gmail_batch_modifier.rb \
  --query='<検索クエリ>' \
  --remove-labels=INBOX,UNREAD \
  [--max-results=N] [--dry-run]
```

両スクリプトともmodifyスコープが必要。readonlyトークンでは動作しない。

### 結果の表示

成功時:

```markdown
## <操作名>完了

- **対象件数**: N件
- **処理成功**: N件
- **結果**: 成功
```

一部失敗時:

```markdown
## <操作名>結果

- **対象件数**: N件
- **処理成功**: M件
- **失敗バッチ**: K件
- **結果**: 一部失敗

| バッチ | 件数 | エラー |
|--------|------|--------|
| 0 | 100 | Rate limit exceeded |
```

---

## 認証エラー時

認証はブラウザでのOAuth操作が必要なため、コマンドを自動実行せずユーザーに案内する。

| エラーパターン | 対処 |
|---------------|------|
| `No credentials found` | 初回認証が必要。authenticatorを実行 |
| `invalid_grant` | トークン期限切れ。トークン削除後、authenticatorを再実行 |
| `GOOGLE_CLIENT_ID is not set` | 環境変数の設定を案内 |

### 再認証コマンド

| スコープ | 用途 | トークンファイル | 認証コマンド |
|----------|------|-----------------|-------------|
| readonly | 検索・取得 | `~/.credentials/gmail-readonly-token.yaml` | `ruby gmail_authenticator.rb` |
| modify | スパム削除・バッチ変更 | `~/.credentials/gmail-modify-token.yaml` | `ruby gmail_authenticator.rb --scope=modify` |

手順（`mise exec --cd ~/ghq/github.com/shifumin/gmail-tools-ruby --` で実行）:
1. `invalid_grant`の場合のみ: `rm -f <トークンファイル>`
2. 認証コマンドを実行（ブラウザが開く）

---

## 重要な制限事項

1. **送信不可**: メールの送信はできない
2. **完全削除不可**: スパム管理はゴミ箱への移動のみ。完全削除（expunge）はできない
3. **添付ファイルダウンロード不可**: ファイル情報の表示のみ
4. **HTML本文**: `body.html`は存在確認のみ。表示はplain_textを優先
5. **スコープの違い**: 検索・取得はreadonly、スパム削除・バッチ変更はmodifyスコープが必要（トークンが別）

---

## 技術仕様

詳細な技術仕様（JSON出力構造、検索演算子など）は `~/.claude/skills/gmail/reference.md` を参照。
