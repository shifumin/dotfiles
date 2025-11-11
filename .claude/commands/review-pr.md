# review-pr [PR URL]

引数で渡されたPRのURLをレビューし、変更内容と改善点を分かりやすくまとめます。

---

## 実行フロー

### STEP 1: PR URLのパースと基本情報の取得

#### 1-1. URLから情報を抽出

**URL形式**: `https://github.com/<オーナー>/<リポジトリ>/pull/<PR番号>`

**抽出方法**:
- 正規表現パターン: `github\.com/([^/]+)/([^/]+)/pull/(\d+)`
- 抽出例: `https://github.com/owner/repo/pull/12345`
  - オーナー/リポジトリ: `owner/repo`
  - PR番号: `12345`

#### 1-2. PR情報の取得（並列実行）

以下の3つのコマンドを**並列実行**してPR情報を網羅的に取得：

```bash
# 基本情報
gh pr view <PR番号> --repo <オーナー>/<リポジトリ> --json title,body,state,author,createdAt,url,headRefName,baseRefName

# ファイル統計
gh pr view <PR番号> --repo <オーナー>/<リポジトリ> --json files,additions,deletions,changedFiles

# 差分
gh pr diff <PR番号> --repo <オーナー>/<リポジトリ>
```

#### 1-3. エラー時の対処

**エラーメッセージ別の対処法**:
- `Could not resolve to a PullRequest` → PR番号が間違っている
- `Could not resolve to a Repository` → リポジトリ名が間違っているか、アクセス権限がない
- `HTTP 404: Not Found` → プライベートリポジトリで認証が必要
  - `gh auth status`で認証状態を確認
  - ユーザーに権限の確認を依頼

---

### STEP 2: 変更ファイルの読み込み

#### 2-1. 必須読み込み対象ファイルの判定

以下の条件に**いずれか該当するファイル**は必ずReadツールで読み込む：

**条件A: ファイル特性**
- 新規追加されたファイル（全て）
- 変更行数が100行以上のファイル
- diffが `[XXX lines truncated]` で切れているファイル

**条件B: ファイルパターン（N+1問題チェック対象）**
- `app/workers/**/*_worker.rb`
- `app/services/**/*.rb`
- `app/controllers/**/*_controller.rb`
- `app/models/**/*.rb`

**条件C: 重要ファイル**
- `db/migrate/**/*.rb` (migrationファイル)
- `client/src/**/*.tsx` (フロントエンドファイル)
- `client/src/**/*.ts` (フロントエンドファイル)

#### 2-2. Readツールで読み込む理由

- diffが途中で切れている場合がある
- 前後のコンテキストを理解するため
- 正確な行番号を特定するため（推測での行番号記載を防ぐ）

---

### STEP 3: 条件付き外部リソースの確認

#### 3-1. 確認が必要なリソースの判定

**判定フロー**:
```
変更ファイルに client/src/** が含まれる？
├─ YES → SmartHR Design System確認を実行
└─ NO → STEP 4へスキップ
```

#### 3-2. SmartHR Design Systemリポジトリの確認（フロントエンド変更時のみ）

**リポジトリパス**:
- 絶対パス: `~/ghq/github.com/kufu/smarthr-design-system`

**確認対象**:
- コンポーネントガイドライン: `src/content/`
- 実装例: `src/components/`
- デザイントークン: `src/constants/`

**確認手順**:

1. **使用コンポーネントの特定**
   - 変更ファイルから使用されているコンポーネントを抽出（例: `Button`, `Stack`, `Cluster`）

2. **ガイドラインファイルの検索**
   - Grepツールを使用:
     - pattern: `<コンポーネント名>` （例: `Button`）
     - path: `~/ghq/github.com/kufu/smarthr-design-system/src/content/`
     - output_mode: `files_with_matches`

3. **ガイドラインの読み込み**
   - 検索結果のファイルパスをReadツールで読み込む
   - 正しい使用方法と推奨パターンを確認

**参考リソース**:
- 公式サイト: [https://smarthr.design](https://smarthr.design)

---

### STEP 4: レビュー観点のチェック

#### 4-1. チェック実行の判定

**判定フロー**:
```
変更ファイルの確認
├─ db/migrate/** 含む → Migrationチェックを追加
├─ client/src/** 含む → Design Systemチェックを追加
└─ app/models/** 含む → Railsベストプラクティスチェックを追加
```

#### 4-2. 優先度A：全PRで必須のチェック（MUST）

##### A-1. N+1問題のチェック

**対象ファイル**:
- `app/workers/**/*_worker.rb`
- `app/services/**/*.rb`
- `app/controllers/**/*_controller.rb`
- `app/models/**/*.rb`

**チェックポイント**:
- ❌ ループ内でのActiveRecord呼び出し（`map`, `each`, `filter`内での`find_by`, `where`）
- ❌ アソシエーション呼び出しで`includes`, `preload`, `eager_load`が未使用
- ❌ Workerでの一括処理における繰り返しクエリ

**検出例**:
```ruby
# ❌ N+1問題あり
users.each do |user|
  user.posts.count  # 各userごとにクエリが発生
end

# ✅ 解決策
users.includes(:posts).each do |user|
  user.posts.count  # 事前にロード済み
end
```

##### A-2. PRのdescriptionとの整合性確認

コードの変更内容が、PRのdescriptionの「やったこと」に沿っているか確認

**確認項目**:
- 記載された機能追加が実装されているか
- 記載されたバグ修正が含まれているか
- 記載されていない変更が含まれていないか

---

#### 4-3. 優先度B：条件付きチェック（該当する場合は必須）

##### B-1. Migrationファイルのチェック（db/migrate/** 変更時）

**対象ファイル**: `db/migrate/**/*.rb`

**チェックポイント**:
- migration内容の妥当性
- up/downの整合性（ロールバック可能か）
- インデックスの適切性（外部キーにインデックスがあるか）
- カラム追加時のデフォルト値や制約の妥当性

##### B-2. SmartHR Design System準拠チェック（client/src/** 変更時）

**対象ファイル**: `client/src/**/*.tsx`, `client/src/**/*.ts`

**B-2-1. スタイリング**
- ❌ `styled-components`で不要なスタイル指定をしていないか
- ✅ SmartHR UIコンポーネントのpropsで対応可能な場合はpropsを優先
- ✅ レイアウトは適切なコンポーネントを使用：
  - 縦並び → `Stack`
  - 横並び → `Cluster`
- ⚠️ カスタムCSSが必要な場合、その理由が妥当か

**B-2-2. コンポーネント使用**
- ✅ SmartHR UIの標準コンポーネントを適切に使用しているか
- ❌ 独自実装で代替可能な既存コンポーネントがないか
- ✅ デザイントークン（色、間隔、フォントサイズ等）を使用しているか

**B-2-3. アクセシビリティ**
- ✅ セマンティックなHTMLを使用しているか
- ✅ フォーム要素に適切なラベルがあるか
- ✅ キーボード操作に対応しているか

##### B-3. Railsベストプラクティスチェック（app/models/** 変更時）

**対象ファイル**: `app/models/**/*.rb`

**B-3-1. スコープの適切な使用**
- ✅ クエリを返すロジックは `scope` を使用
- ❌ クラスメソッドで単純なクエリ定義をしていないか

**検出例**:
```ruby
# ❌ 避けるべき
def self.confirmed
  where.not(confirmed_at: nil)
end

# ✅ 推奨
scope :confirmed, -> { where.not(confirmed_at: nil) }
```

**理由**: scopeの方がチェーン可能で、nilを返してもエラーにならない安全性がある

---

#### 4-4. 優先度C：推奨チェック（SHOULD）

##### C-1. コード品質のチェック

- 単一責任の原則（SRP）違反
- 適切なエラーハンドリング
- セキュリティ上の問題（SQL injection, XSS, CSRF等）
- パフォーマンス上の問題

---

### STEP 5: レビュー結果の出力

以下の形式でレビュー結果をまとめる

---

## 出力フォーマット

### PR情報

- **タイトル**: [PRタイトル]
- **作成者**: [作成者名]
- **状態**: [OPEN/MERGED/CLOSED]
- **ブランチ**: [headブランチ] → [baseブランチ]
- **関連チケット**: [チケット番号（descriptionから抽出）]

### やりたいこと

[PRのdescriptionから抽出]

### やったこと

[PRのdescriptionから抽出]

---

### 変更内容のまとめ

**形式**:
```markdown
#### `path/to/file.rb`
**変更行**: L123-L145
**変更概要**: メソッドXXXを追加し、N+1問題を解消
```

**注意事項**:
- 相対パスを使用
- 行番号はReadツールで確認した実際の値を使用
- ❌ diffから推測した行番号は使用禁止

---

### ✅ 良い点

実装の優れている点や評価すべき点を列挙

**例**:
- テストカバレッジが十分
- エッジケースを考慮したエラーハンドリング
- コードの可読性が高い

---

### ⚠️ 修正が必要な点

**重要**: 実際に修正が必要な項目のみ記載すること

#### [連番]. [問題の概要]

**ファイル**: `[相対パス]:[行番号]`

**問題点**:
[なぜ修正が必要か、どのような影響があるか]

**修正案**:
```[言語]
[具体的なコード例]
```

---

### PRのdescriptionとの整合性

✅ 整合性あり / ⚠️ 差異あり

[差異がある場合は詳細を記載]

---

### チェック実施状況

**実施したチェック項目**:
- [x] N+1問題のチェック
- [x] PRのdescriptionとの整合性確認
- [ ] Migrationファイルのチェック（該当なし）
- [ ] SmartHR Design System準拠の確認（該当なし）
- [ ] Railsベストプラクティスの確認（該当なし）

---

### 総評

[全体的な評価と承認推奨度]

**承認推奨**: ✅ 承認可 / ⚠️ 条件付き承認 / ❌ 要修正

---

## 制約事項（MUST NOT）

以下の行為は**禁止**：

- ❌ diffが切れている部分について**推測で書く**
- ❌ Readツールで確認していないコードの**行番号を書く**
- ❌ 存在しないメソッドやコードについて**言及する**
- ❌ 修正不要な項目を「⚠️ 修正が必要な点」に**含める**
- ❌ 「結論: 問題なし」のような**無意味な項目を書く**
- ❌ `~`を使ったパス表記（必ず絶対パス `~/...` を使用）

---

## 使用例

```bash
/review-pr https://github.com/owner/repo/pull/12345
```
