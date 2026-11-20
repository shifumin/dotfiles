---
description: PRレビューコメントを分析し、修正方針を提案する。承認されたら返信・resolve まで行う。
  「レビューコメント対応」「PRコメント対応」「review-pr-comments」「コメントに対応」
  「未解決の指摘を精査」「must/imo/ask を判定して」「レビュー結果を貼るので判断して」などのリクエストで使用。
---

# Reviewing PR Comments

PRレビューの指摘を分析し、修正必要性の判断と修正方針を提案する。

| 入力 | 対象 |
|------|------|
| コメント URL（`#discussion_r<id>` / `#issuecomment-<id>`） | そのコメント1件 |
| レビュー URL（`#pullrequestreview-<id>`） | そのレビューのコメント全件と、レビュー本文の中の指摘 |
| PR URL のみ | 未解決のレビュースレッド全件と、レビュー本文の中の未返信の指摘 |
| 貼り付けた指摘（must / imo / nits / ask などのラベル付き） | 貼られた指摘全件。ラベルが妥当かも判定する |

入力がなければAskUserQuestionで確認。複数件は1件ずつ手順2〜4を行い、最後に一覧表でまとめる。

---

## 処理フロー

### 1. コメント情報の取得

URL `https://github.com/<owner>/<repo>/pull/<number>#discussion_r<comment_id>` または `#issuecomment-<id>` からowner/repo/number/comment_idを抽出。

並列実行:

```bash
# PR基本情報
gh pr view <number> --repo <owner>/<repo> --json title,body,state,author,headRefName,baseRefName,url

# 全レビューコメント取得
gh api repos/<owner>/<repo>/pulls/<number>/comments --jq '.[] | {id, body, user: .user.login, path, line, original_line, original_commit_id, created_at, in_reply_to_id}'

# PRレベルのコメント（issue comment形式の場合）
gh api repos/<owner>/<repo>/issues/<number>/comments --jq '.[] | {id, body, user: .user.login, created_at}'

# PR diff
gh pr diff <number> --repo <owner>/<repo>
```

取得した全コメントから、対象コメントIDに一致するものを特定する。

レビュー URL と PR URL のときは、対象を次で取る。

```bash
# レビュー配下のコメント
gh api repos/<owner>/<repo>/pulls/<number>/reviews/<review_id>/comments

# 未解決のレビュースレッド（thread id は resolve で使う）
gh api graphql -F o=<owner> -F r=<repo> -F n=<number> -f query='query($o:String!,$r:String!,$n:Int!){repository(owner:$o,name:$r){pullRequest(number:$n){reviewThreads(first:100){nodes{id isResolved isOutdated comments(first:20){nodes{databaseId author{login} path line body}}}}}}}' \
  --jq '.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved | not)'

# レビュー本文（差分の外の指摘や Nitpick は行コメントにならず、ここにだけ載る）
gh api repos/<owner>/<repo>/pulls/<number>/reviews --paginate --jq '.[] | select(.body != "") | {id, user: .user.login, submitted_at, commit_id, body}'
```

スレッドだけを見ると、レビュー本文の中の指摘（「Outside diff range comments」「Nitpick comments」などの節）を取りこぼす。本文の指摘も1件ずつ対象にする。返信済みかは、その指摘の見出しを引用した PR へのコメントが後にあるかで判断する。

### 2. コメント内容の分析

対象コメントから以下を把握:

| 項目 | 確認内容 |
|------|---------|
| 対象ファイル・行番号 | `path`と`line`フィールド。`line`がnull（レビュー後にdiffが更新されoutdatedになった行コメント）の場合は`original_line`を使い、当時のコードは`original_commit_id`で取得する |
| 指摘の種類 | バグ指摘、設計改善、スタイル、質問、提案 |
| スレッド | `in_reply_to_id`で会話の流れを追跡（issue comment形式には`in_reply_to_id`フィールドが存在しないため、その場合は投稿時刻の前後関係で流れを追う） |
| リンク | コメント内URLを確認。GitHub PR/IssueのURLは`gh pr view`/`gh api`を優先し、それ以外はWebFetchで確認する |
| 画像 | コメント内の画像URLをcurlでダウンロードしReadで確認 |

### 3. 対象コードの調査

```bash
# 対象ファイルの確認（Readツール使用）
# コメントのpathフィールドが示すファイルを読む
```

対象リポジトリがローカルにクローンされている場合はReadツールで対象ファイルを読み込む。ローカルにない場合（自分の作業ディレクトリと異なるリポジトリのPRを分析する場合など）は`gh api repos/<owner>/<repo>/contents/<path>?ref=<commit_sha>`または`gh pr diff`のdiff hunkで代替する。`original_commit_id`が取得できていれば、レビュー時点のコードは`ref=<original_commit_id>`で取得する。必要に応じて関連ファイルも確認:

| 関連ファイル | 確認条件 |
|------------|---------|
| テストファイル | テスト追加・修正が必要そうな指摘 |
| 型定義・インターフェース | API変更に関する指摘 |
| 設定ファイル | 設定に関する指摘 |

Breaking Changesや影響範囲の確認にはGrepツールで使用箇所を検索する。

### 4. 修正必要性の判断

| 観点 | チェック内容 |
|------|------------|
| 指摘の妥当性 | 技術的に正しいか |
| PRの目的との整合性 | PR全体の変更意図と矛盾しないか |
| コーディング規約 | プロジェクトの規約に違反しているか |
| 影響範囲 | 他のコード・機能に影響するか |
| セキュリティ | 脆弱性に関わるか |

### 5. 結果の報告

---

## 出力フォーマット

```markdown
## レビューコメント分析

### PR概要
- **タイトル**: {PRタイトル}
- **ブランチ**: {head} → {base}

### 対象コメント
- **投稿者**: @{user}（PR作者本人による返信・自己コメントの場合はその旨を注記する）
- **対象**: {path}:{line}（issue comment等でpath/lineが存在しない場合は「PR全体」と記載。`line`がnullで`original_line`のみ取得できた場合は`{path}:{original_line}`とし、outdatedである旨を注記する）
- **指摘内容**: {コメントの要約}

### 修正必要性: {必要 / 不要 / 要検討}

**判断理由**:
- {根拠を箇条書き}

### 修正方針

| 修正必要性 | このセクションの扱い |
|-----------|------|
| 必要 | 方針を1つ以上記載する |
| 要検討 | 「検討中の選択肢」として方針を記載する（見出しは`### 修正方針（検討中の選択肢）`とする） |
| 不要 | セクション自体を省略する |

#### 方針1: {方針名}
- **変更内容**: {具体的な修正内容}
- **メリット**: {メリット}
- **デメリット**: {デメリット}

（複数方針がある場合は追加）

**推奨**: 方針{X}
**理由**: {推奨理由}

### 次のステップ
1. {具体的なアクション}
```

複数件のときは、上の形式を1件ずつ書く代わりに次の表にまとめ、必要・要検討のものだけ修正方針を書く。

```markdown
| # | 指摘（投稿者） | ラベル妥当性 | 修正必要性 | 根拠 file:line | 方針 |
```

ラベル妥当性の列は、貼り付けた指摘のときだけ埋める。

### 判断基準

| 修正必要性 | 条件 |
|-----------|------|
| 必要 | バグ指摘、セキュリティ問題、明確な規約違反 |
| 要検討 | 設計方針の相違、トレードオフがある提案 |
| 不要 | 既に対応済み、誤解に基づく指摘、前提が成り立たない |

判定に修正コスト（時間・変更量）を入れない。あるべき状態に近づく提案なら、「好みの範囲」「得が小さい」「後で対応」を不要の理由にしない。

**不要の場合は、根拠となるコード・spec・データを示す。** 示せなければ要検討にして、何を調べれば決まるかを書く。

**境界事例（対応済みかの判定、PRの状態を問わない）**: 対象コメントの提案が返信スレッド・最新diff（`gh pr diff`）・PR現在のmainのいずれかで既に反映されているか確認する（PRがOPENのまま後続コミットで対応済みのケースも含む）。

| 状況 | 判定 |
|------|------|
| 提案が反映済み | 不要（対応済み）。同一PR内・別PRのどちらで反映されたかを判断理由に明記する |
| 指摘者本人がスレッド内で撤回・誤解と判明（コード変更なしで解消） | 不要（誤解に基づく指摘）。撤回・反証の経緯を判断理由に記載する |
| 変更要求を含まない承認・確認コメント | 不要（変更要求なし） |
| 未反映だが議論が上位の設計判断や別PRに引き継がれている | 要検討 |
| 指摘は正しいが、原因がPRの差分の外にある | 要検討。差分の外であることを根拠に示し、このPRで直すか別チケットにするかを書く |

---

## 返信と resolve（承認後）

返信を頼まれたら、skill `draft-github-comment` の手順で文面を作り、承認を取って投稿する（本人の過去のコメントから文体を取り、投稿後に読み返すところまで含む）。「それぞれ返信」と言われたら全件に返信し、返さないものがあれば理由を確認する。

```bash
gh api graphql -F id=<thread_id> -f query='mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{isResolved}}}'
```

resolve は bot の指摘で対応を決めたものに限る。人間のレビュアーの指摘は本人に任せる。

---

## エラー処理

| エラーパターン | 対処 |
|---------------|------|
| コメントIDが見つからない | `gh api`で全コメントを再取得し、URL内のIDと照合 |
| PRがクローズ済み（MERGED含む） | 情報取得は可能。修正が必要な場合はその旨を報告 |
| リポジトリへのアクセス権なし | `gh auth status`で認証確認を案内 |
| コメント内リンクがアクセス不可 | リンク先を確認できなかった旨を報告し、指摘内容のみで判断 |

---

## 他スキルとの使い分け

| 操作 | 使用先 |
|------|--------|
| レビューコメントへの対応分析 | **このスキル** |
| 深いコードレビュー | `/reviewing-pr` |
| commit + push | `/push` |
