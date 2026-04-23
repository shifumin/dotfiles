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

| 操作 | トリガーとなる表現例 | 使用コマンド |
|------|---------------------|-------------|
| 検索 | 「メールを検索」「〜からのメール」「〜のメールを探して」 | `+triage` / `messages get` |
| 取得 | 「メールの詳細」「メールを開いて」「本文を見せて」 | `messages get` |
| スパム管理（削除） | 「迷惑メールを削除」「スパムを整理」「スパム消して」 | `messages list` + `messages trash` |
| スパム確認（件数のみ） | 「迷惑メール確認」「スパム何通来てる？」「迷惑メールどれくらい？」 | `+triage` のみ（trashしない） |
| カテゴリタブ整理 | 「Socialタブを整理」「プロモーションを整理」「SNS通知を既読に」 | `+triage` + `messages batchModify` |
| カテゴリタブ確認（件数のみ） | 「Socialタブ何件？」「プロモいくつ来てる？」 | `+triage` のみ（batchModifyしない） |

### 意図解釈ルール（件数確認 vs 操作実行）

ユーザーの発話に **動詞が含まれない / 件数や状況を尋ねる疑問詞** がある場合は「確認のみ」と解釈し、**破壊的操作（trash / batchModify）を実行しない**。Step 1（一覧取得）と件数報告のみで停止する。確認質問（「削除しますか？」等）も出さない。

| 発話パターン | 解釈 | 出力 |
|------------|------|------|
| 「削除して」「整理して」「アーカイブして」「消して」 | 操作実行 | Step 1→2→3（確認後実行） |
| 「どれくらい？」「何通？」「ある？」「来てる？」「確認」 | 件数確認のみ | Step 1のみ→件数とテーブル表示で終了 |
| 判別不能 | 件数確認として扱う（安全側） | Step 1のみ→「削除する場合は明示してください」と補足 |

---

## 共通設定

Google Workspace CLI（`gws`）を使用:
```bash
gws gmail <subcommand> [options]
```

---

## メール検索

### 処理フロー

1. ユーザー入力から検索意図を解釈
2. 自然言語をGmail検索クエリに変換
3. gwsコマンドを実行
4. 出力をMarkdown形式に整形して表示

### 検索フローと件数確認モードの関係

検索フロー（このセクション）は **デフォルトで件数を冒頭に明示する** ため、「〜ある？」「何件？」のような疑問形検索もそのまま検索フローで処理して良い。バッチ操作系の「件数確認モード」（`category:` や `in:spam` 等のラベル/カテゴリ単位）とは独立に動作する。

| 発話パターン | 適用フロー |
|------------|-----------|
| 「Amazonからのメール何件？」「先月のメール一覧」「重要なメール何通？」 | 検索フロー（このセクション） |
| 「迷惑メール何件？」「Socialタブいくつ？」「プロモいくつ？」 | バッチ操作の「件数確認モード」 |

### 自然言語からGmail検索クエリへの変換

| 自然言語表現 | Gmail検索クエリ |
|-------------|----------------|
| 「〜からのメール」（送信元固有名詞） | `from:<語幹>`（**部分一致**：例 「Amazon」→ `from:amazon`、サブドメイン違いも拾う） |
| 「〜.co.jpからのメール」（明示的にドメイン指定） | `from:<完全ドメイン>`（例: `from:amazon.co.jp`） |
| 「〜さんへのメール」 | `to:email@example.com` |
| 「件名に請求書を含む」 | `subject:請求書` |
| 「最近」「最近の」「ここ最近」 | `newer_than:1m`（**デフォルト1ヶ月**） |
| 「最新」「直近」 | `newer_than:7d` |
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

### `--max` のデフォルト方針

| 用途 | `--max` |
|------|---------|
| 検索（件数明示なし） | `20`（デフォルト） |
| バッチ操作（件数明示なし） | `50` |
| 「全部見たい」「全件」「もっと」等の明示 | `200` |
| ユーザーが件数を明示（例: 「30件」） | 明示値 |

### 複合クエリの組み立て

複数の条件はスペースで連結（AND検索）:
- 「Amazonからの今月のメール」→ `from:amazon.co.jp newer_than:1m`
- 「添付ファイル付きの請求書」→ `subject:請求書 has:attachment`

### 実行コマンド

#### 概要のみ（本文不要 — デフォルト）

```bash
gws gmail +triage --query '<検索クエリ>' --max <N> --format json
```

#### 本文付き

Step 1: メッセージ一覧取得
```bash
gws gmail +triage --query '<検索クエリ>' --max <N> --format json
```

Step 2: 各メッセージの本文取得（必要な分だけ）
```bash
gws gmail users messages get --params '{"userId":"me","id":"<message_id>"}' --format json
```

### オプション

| オプション | 説明 |
|-----------|------|
| `--query` | **必須** Gmail検索クエリ |
| `--max` | 最大取得件数（デフォルト: 20） |
| `--format` | 出力形式: json / table / yaml / csv |
| `--labels` | ラベル名を出力に含める |

### 出力の整形

`+triage` のJSON出力を以下のMarkdown形式に変換:

```markdown
## メール検索結果（N件）

検索クエリ: `<query>`

### 1. 件名
- **From**: 送信者名 <email@example.com>
- **Date**: YYYY-MM-DD HH:MM
- **ID**: `message_id`

---
```

| 項目 | ルール |
|------|--------|
| 日付 | RFC2822 → `YYYY-MM-DD HH:MM`（**UTC→JST変換、+9時間** — reference.md準拠） |
| 送信者 | `"Name" <email>` 形式をそのまま表示 |
| 本文 | 要求時のみ `messages get` で取得して表示（500文字超は省略） |
| HTMLメール | `messages get` で取得したpayloadから抽出 |
| 0件 | 「該当するメールが見つかりませんでした」 |
| ラベル | 日本語表示（変換表はreference.md参照） |
| 件数表示 | 見出しは **実際に表示している件数** を使う（`## メール検索結果（20件）`）。サーバー側推定総数（`resultSizeEstimate`）が表示件数より大きい場合は **末尾に1行注記**（例: 「（全 N 件中、最新 M 件を表示）」） |

---

## メール取得

### 処理フロー

1. ユーザーからメッセージIDを取得（検索結果から選択）
2. `messages get` を実行
3. レスポンスから情報を抽出し、Markdown形式に整形して表示

### 実行コマンド

```bash
gws gmail users messages get --params '{"userId":"me","id":"<メッセージID>"}' --format json
```

### gws出力からの情報抽出

gws はGmail API の生レスポンスを返す。以下のフィールドを `payload.headers` から抽出:

| 表示項目 | ヘッダー名 |
|---------|-----------|
| 件名 | `Subject` |
| From | `From` |
| To | `To` |
| 日付 | `Date` |

本文は `payload.parts` または `payload.body` の `data` フィールドからBase64デコードして取得。
ラベルは `labelIds` フィールドから取得。

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

1. **一覧取得**: gwsコマンドで対象メールを一覧表示
2. **ユーザー確認**: テーブル形式で表示し、操作の同意を得る
3. **実行**: 確認後、操作に応じたgwsコマンドで処理

### 操作別パラメータ

| 操作 | 検索コマンド | 実行コマンド | 操作名（確認文に使う） |
|------|------------|-------------|----------------------|
| スパム管理 | `+triage --query 'in:spam'`（優先）/ `messages list`（フォールバック） | 各IDに `messages trash` | ゴミ箱に移動 |
| Socialタブ整理 | `+triage --query 'category:social is:unread'` | `messages batchModify` (removeLabelIds: INBOX,UNREAD) | アーカイブして既読に |
| Promotionsタブ整理 | `+triage --query 'category:promotions is:unread'` | `messages batchModify` (removeLabelIds: INBOX,UNREAD) | アーカイブして既読に |
| 汎用ラベル操作 | `+triage --query '<任意クエリ>'` | `messages batchModify` | （操作内容に応じて記述） |

他のカテゴリ（Updates、Forums）も同様に `category:<name> is:unread` で対応可能。
汎用ラベル操作では `addLabelIds` でラベル付与、`removeLabelIds` でラベル削除が可能（少なくとも一方は必須）。例: 特定メールに一括でラベルを付ける、特定条件のメールをまとめてアーカイブする等。

### Step 1: 一覧取得

**カテゴリタブ整理**:
```bash
gws gmail +triage --query '<検索クエリ>' --max 50 --format json
```

**スパム管理**:

優先: `+triage --query 'in:spam'`（件名・送信者・日時を一括取得できる）
```bash
gws gmail +triage --query 'in:spam' --max 50 --format json
```

フォールバック（`+triage`で取得できない場合）: `messages list` + `messages get`
```bash
# Step 1-1: メッセージID一覧を取得
gws gmail users messages list --params '{"userId":"me","q":"label:spam","maxResults":50,"includeSpamTrash":true}' --format json

# Step 1-2: 各IDのメタデータを取得（件名・送信者・日時の表示用）
gws gmail users messages get --params '{"userId":"me","id":"<message_id>","format":"metadata","metadataHeaders":["Subject","From","Date"]}' --format json
```

`format: metadata` + `metadataHeaders` で必要なヘッダーのみ取得し、本文ダウンロードを回避する。
レスポンスの `payload.headers` から Subject / From / Date を抽出してテーブル表示に使用する。

### Step 2: ユーザーへの表示と確認

JSON出力をテーブル形式に変換して表示。**「件数確認のみ」と「操作実行」で出力フォーマットを変える**:

#### 操作実行モード（「削除して」「整理して」等）

```markdown
## <操作名>一覧（N件）

| # | 送信者 | 件名 | 日時 |
|---|--------|------|------|
| 1 | sender@example.com | Subject line | 2026-02-10 15:30 |

これらのメール（N件）を<操作名>しますか？
```

#### 件数確認モード（「何件？」「ある？」「来てる？」等）

```markdown
## <ラベル/カテゴリ名>のメール（N件）

| # | 送信者 | 件名 | 日時 |
|---|--------|------|------|
| 1 | sender@example.com | Subject line | 2026-02-10 15:30 |
```

確認質問は出さない（Step 3に進まないため）。

#### 共通ルール

| 項目 | ルール |
|------|--------|
| 全件表示 | **全メールを1件ずつテーブルに表示する。「〜等」「〜など」で要約・省略しない** |
| 日付 | RFC2822 → `YYYY-MM-DD HH:MM` |
| 確認 | 操作実行モードでは **必ずユーザーの明示的な同意を得てから Step 3 に進む** |
| 0件 | 見出しを **省略** し、「対象のメールはありません。」の1行のみで終了（モードに関係なく確認質問は出さない） |
| 操作名 | 操作別パラメータ表の「操作名」列を使う |
| 50件超 | デフォルト `--max 50` を超える可能性がある場合は `--max 200` 等に拡張するか、ユーザーに件数上限を確認する |
| ラベル名表記（件数確認モードの見出し） | ユーザーの発話で使われた語彙を優先（「迷惑メール」「Social」「プロモーション」等）。発話に該当語彙がなければreference.mdの日本語表（「ソーシャル」「プロモーション」「迷惑メール」）を使う |

### Step 3: 実行

**スパム管理** — 各メッセージをゴミ箱に移動:

Claude CodeのBashツールはzshの`eval`で実行されるため、`for...do...done`ループはパースエラーになる。`bash`ヒアドキュメントでラップすること:

```bash
bash <<'SCRIPT'
for id in <id1> <id2> <id3>; do
  gws gmail users messages trash --params "{\"userId\":\"me\",\"id\":\"$id\"}" 2>/dev/null
done
SCRIPT
```

**カテゴリタブ整理** — ラベル一括変更:

Step 3-1: +triageの出力から全メッセージIDを収集

Step 3-2: batchModifyでラベル変更
```bash
gws gmail users messages batchModify --params '{"userId":"me"}' --json '{"ids":["id1","id2",...],"removeLabelIds":["INBOX","UNREAD"]}'
```

**注意**: batchModifyの `ids` にはメッセージIDの配列を渡す。+triageの出力からIDを収集する。`addLabelIds` が必要な場合は JSON に追加。

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
- **失敗**: K件
- **結果**: 一部失敗（失敗したメッセージIDを報告）
```

---

## 認証エラー時

認証トークンエラー（403 insufficientPermissions）が発生した場合:

### Step 1: 再認証

```bash
gws auth login -s gmail
```

ブラウザが開くので、ユーザーにOAuth認証を完了してもらう。

### Step 2: トークンキャッシュクリア（再認証後も403が続く場合）

`gws auth status`でスコープが正しいのに403が出る場合、トークンキャッシュが古い可能性がある:

```bash
rm -f ~/.config/gws/token_cache.json
```

キャッシュ削除後にコマンドを再実行すると、新しいトークンが自動生成される。

認証状態の確認:
```bash
gws auth status
```

---

## 重要な制限事項

1. **送信可能**: `gws gmail +send` で送信可能（必要に応じて別途スキル化）
2. **完全削除不可**: スパム管理はゴミ箱への移動のみ。完全削除（expunge）はできない
3. **添付ファイルダウンロード不可**: ファイル情報の表示のみ
4. **本文取得は2ステップ**: `+triage` は概要のみ。本文が必要な場合は `messages get` で個別取得
5. **スコープ一元管理**: readonly/modifyの区別なし。`gws auth login -s gmail` で全操作対応

---

## 技術仕様

詳細な技術仕様（JSON出力構造、検索演算子など）は `~/.claude/skills/gmail/reference.md` を参照。
