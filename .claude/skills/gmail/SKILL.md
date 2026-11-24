---
name: gmail
description: "Gmailのメール検索・本文取得・迷惑メール削除・単一カテゴリ整理・ラベル変更を行う。「メール検索」「〜からのメール」「未読確認」「請求書メール探して」「迷惑メール確認/削除」「Social/プロモーションタブ整理」等で使用。複数カテゴリ一括整理は cleanup-inbox-mail が優先。"
---

# Gmail操作

Google Workspace CLI（`gws`）をラップする `scripts/gmail.py`（`<base>` は本 `SKILL.md` があるディレクトリの絶対パス）で Gmail の検索・詳細取得・スパム管理・ラベル操作を行う。

- 複数カテゴリの一括整理（迷惑メール＋購入＋ソーシャル＋プロモーション）は `cleanup-inbox-mail` を使う。
- 完全削除（expunge）と添付ファイルダウンロードは未対応（スパム管理はゴミ箱移動のみ）。

## 操作の判定と安全ルール

| 操作 | トリガー例 | サブコマンド |
|---|---|---|
| 検索 | 「〜からのメール」「未読メール」「請求書を探して」「Amazonから何件？」 | `search` |
| 詳細取得 | 「本文を見せて」「詳細を開いて」 | `get` |
| スパム・カテゴリ確認（件数のみ） | 「迷惑メール何通？」「Socialタブいくつ？」 | `search --format table`（変更しない） |
| スパム削除 | 「迷惑メールを削除」「スパム消して」 | `search --format table` → 確認 → `trash` |
| カテゴリ整理・ラベル操作 | 「Social/プロモを整理」「ラベルを付けて」 | `search --format table` → 確認 → `modify` |

**意図解釈（件数確認 vs 操作実行）**:
- 変更を指示する動詞（「削除して」「整理して」「アーカイブして」「消して」等）が無く、件数・状況を尋ねる疑問形または判別不能な発話は**件数確認のみ**（安全側）として扱い、確認質問を出さず一覧表示で終了する。
- 変更操作は必ず対象全件をテーブル表示し（`〜等` で省略禁止）、**ユーザーの明示的な同意を得てから**実行する。

## 1. メール検索

自然言語を Gmail 検索クエリへ変換して `search` を実行する:

| 自然言語 | Gmail クエリ |
|---|---|
| 「〜からのメール」（固有名詞） | `from:<語幹>`（部分一致。ドメイン明示時は `from:example.co.jp`） |
| 「〜さんへ」「件名に〜」 | `to:user@example.com` / `subject:<語>` |
| 「最近」「先月」 / 「最新」「直近」「今週」 | `newer_than:1m` / `newer_than:7d` |
| 「今年」「M/D以降」「M/Dまで」 | `after:YYYY/01/01` / `after:YYYY/MM/DD` / `before:YYYY/MM/DD` |
| 添付・状態 | `has:attachment` / `filename:pdf` / `is:unread` / `is:important` / `is:starred` / `label:<名>` |

**`--max` 既定**: 検索 `20` / バッチ操作 `50` / 「全件・全部見たい」 `200` / 件数明示時は明示値。

```bash
python3 -B "<base>/scripts/gmail.py" search --query '<クエリ>' --max <N> [--labels]
```

スクリプトが RFC2822→JST 変換・ラベル日本語化・`resultSizeEstimate` 注記を自動整形する。本文が必要なメールだけ `get` で取得する（概要リストに添える場合は `--max-body 500`）。

## 2. メール詳細取得

```bash
python3 -B "<base>/scripts/gmail.py" get "<message_id>" [--max-body 0]
```

ヘッダー（件名・From・To・JST 日時・日本語ラベル）・デコード済み本文（`text/plain` 優先、無ければ HTML テキスト抽出）・添付ファイル一覧を出力する。

## 3. バッチ操作（スパム管理・カテゴリ整理・汎用ラベル操作）

| 操作 | クエリ | 実行コマンド |
|---|---|---|
| スパム管理 | `in:spam` | `trash <id1> <id2> ...` |
| Social / Promotions / Updates / Forums 整理 | `category:<name> is:unread` | `modify --ids ... --remove INBOX --remove UNREAD --operation-name "アーカイブして既読に"` |
| 汎用ラベル操作 | `<任意クエリ>` | `modify --ids ... [--add <LABEL>] [--remove <LABEL>]` |

### Step 1: 一覧表示

```bash
python3 -B "<base>/scripts/gmail.py" search --query '<クエリ>' --max 50 --format table --heading '<見出し>'
```

- 0 件ならスクリプトが「対象のメールはありません。」のみ出力するので、確認質問を出さず終了する。
- **件数確認モード**: 出力テーブルをそのまま表示して終了（確認質問を出さない）。見出しはユーザー発話の語彙（「迷惑メール」「Social」等）を優先。
- **操作実行モード**: 全件テーブルを省略せず表示し、「これらのメール（N件）を<操作名>しますか？」と確認する。

### Step 2: 実行（明示同意後のみ）

```bash
# スパムをゴミ箱へ移動（IDごとに成功/失敗を集計）
python3 -B "<base>/scripts/gmail.py" trash <id1> <id2> ...

# ラベル一括変更（100件ずつ自動分割して batchModify）
python3 -B "<base>/scripts/gmail.py" modify --ids <id1> <id2> ... --remove INBOX --remove UNREAD --operation-name "アーカイブして既読に"
```

## 認証エラー時

認証エラー（`AUTH_ERROR` / exit 2：401 `Failed to get token` や 403 `insufficientPermissions`）が発生した場合、**エージェントは再認証コマンドを自動実行せず**、ユーザーへ以下の手順を提示して実行してもらう（対話ブラウザ OAuth が必要なため）。

```bash
gws auth logout
gws auth login --scopes https://www.googleapis.com/auth/spreadsheets,https://www.googleapis.com/auth/gmail.modify,https://www.googleapis.com/auth/calendar,https://www.googleapis.com/auth/drive
```

**なぜ必ず「logout → フルスコープ login」のセットか**:
- `gws auth login -s gmail` のような部分スコープ指定は他サービス（calendar / drive / spreadsheets）のスコープを上書きし、以後それらが 403 になるため禁止。
- `gws auth logout` を挟まず再ログインすると、`gws auth status` が `token_valid: true` を返しても実 API が 403 のまま残る stale token 現象が起きる。

読み取り専用の認証状態確認（参考。403 解消判定には使わない）:

```bash
python3 -B "<base>/scripts/gmail.py" auth-status
```
