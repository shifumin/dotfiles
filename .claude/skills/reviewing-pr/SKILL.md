---
name: reviewing-pr
description: "PR をレビューし、変更内容の要約・問題点・Before/After 修正案を報告する。「PRレビュー」「PRを見て」「review-pr」「PRをレビューして」等で使用。対象外: 指摘への対応・返信（review-pr-comments）。"
---

# PR レビュー

PR URL（省略時は現在ブランチの PR、無ければユーザーへ確認）を受け取り、変更内容を分析してレビュー結果を報告する。

## 1. PR 情報・diff・既存コメントの取得

PR 操作用 MCP ツール（`pull_request_read`）が使える環境ではそちらを優先する。CLI 環境では以下を並列実行する:

```bash
gh pr view <number> --repo <owner>/<repo> \
  --json title,body,state,author,createdAt,url,headRefName,baseRefName,files,additions,deletions,changedFiles
gh pr diff <number> --repo <owner>/<repo>
gh api --paginate "repos/<owner>/<repo>/pulls/<number>/comments" \
  --jq '.[] | {user: .user.login, path, line, body, html_url}'
gh api --paginate "repos/<owner>/<repo>/pulls/<number>/reviews" \
  --jq '.[] | select(.body != "") | {user: .user.login, state, body, html_url}'
```

- diff が途中で切れた場合は `gh api` で個別ファイルの差分を取る
- 既存コメント（人間・bot）と同じ指摘は新規の指摘として数えない

## 2. 変更ファイルとプロジェクト規約の確認

ローカルクローン（`~/ghq/github.com/<owner>/<repo>` または `ghq list | grep <repo>`）があれば以下をファイル読み取りツールで読む（無ければ diff のみでレビューし、その旨を報告する）:

- 新規追加ファイル・変更 100 行以上のファイル・diff が途切れたファイルの全文
- リポジトリの `AGENTS.md` / `CLAUDE.md`（固有の規約・レビュー観点をチェック対象に追加）

## 3. レビュー観点

### 全 PR 必須

- **description 整合性**: PR の意図と実装差分が一致しているか
- **ロジック**: 条件分岐・境界値・エッジケースの正確性
- **セキュリティ**: SQLi・XSS・CSRF・認証/認可漏れ・秘密情報のハードコード
- **エラーハンドリング**: 異常系の漏れ・握りつぶし

### 言語別（該当時のみ）

- **Ruby / Rails**: N+1（eager load 漏れ）、クエリ定義の `scope` 使用、migration の up/down・インデックス・不可逆変更
- **TypeScript / React**: 不要な `any` や型アサーション、hooks 依存配列・無限レンダリング、セマンティック HTML・a11y

### 推奨

- 責務分離（SRP）、パフォーマンス（不要な再計算・非効率クエリ・リーク）、変更に対応するテストの有無
- 改善提案を AI 実装コストを理由に省かない。スコープ外・既存の気づきは「不要」ではなく未判断の参考情報として分ける

## 4. 出力フォーマット

```markdown
## PR情報
- **タイトル**: {タイトル}
- **作成者**: @{author}
- **状態**: {OPEN/MERGED/CLOSED}
- **ブランチ**: {head} → {base}

## やりたいこと / やったこと
{description からの要約}

## 変更内容のまとめ
### `{path/to/file}`
- **変更行**: L{start}-L{end}
- **変更概要**: {概要}

## 良い点
- {優れている点}

## 指摘事項
### 1. [{must/imo/nits/ask}] {問題の概要}
- **ファイル**: `{path/to/file}:{line}`（PR diff 上でコメントする位置）
- **問題点**: {影響}
- **必要な理由**: {直さない場合に起きること}
- **発生経路**: {変更行 → 経由する呼び出し → 失敗箇所}（差分外のファイルが絡む場合は必須）
- **区分**: 本 PR で新規発生 / 既存の問題

**Before**:
```{lang}
{実ファイルから正確に引用した現在コード}
```

**After**:
```{lang}
{修正案}
```

## description整合性
✅ 整合性あり / ⚠️ 差異あり（詳細）

## チェック実施状況
- [x] description整合性
- [x] ロジック正確性
- [x] セキュリティ
- [ ] N+1問題（該当なし）

## 総評
{評価・重要度別の指摘件数}
**承認推奨**: ✅ 承認可 / ⚠️ 条件付き / ❌ 要修正（「本 PR で新規発生」の must の有無で判定）
```

- 重要度は must / imo / nits / ask（`review-pr-comments` と共通）を使い、must 以外は任意の提案だと分かるように書く
- 問題なしの項目は「指摘事項」に書かない
- 既存コメントと重複する指摘は「指摘事項」から外し、末尾に「既存コメントと重複」として投稿者とリンクだけ並べる
- 行番号は実ファイルで確認した値のみ使い、パスはリポジトリルート相対にする
- コード修正案は Before / After の両方を記載する（設計方針・テスト戦略などコード外の指摘は文章で説明）

## エラー処理・使い分け

- PR 未発見 / 404: URL 形式と `gh auth status` を案内
- レビュー指摘への対応・返信は `review-pr-comments`、commit + push は `push` を使う
