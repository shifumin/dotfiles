# review-pr [PR URL]

引数で渡されたPRのURLをレビューし、変更内容と改善点を分かりやすくまとめます。

---

## 実行手順

### STEP 1: PR情報の取得

以下のコマンドを**並列実行**してPR情報を網羅的に取得：

```bash
gh pr view <PR番号> --repo <オーナー/リポジトリ名> --json title,body,state,author,createdAt,url,headRefName,baseRefName
gh pr view <PR番号> --repo <オーナー/リポジトリ名> --json files,additions,deletions,changedFiles
gh pr diff <PR番号> --repo <オーナー/リポジトリ名>
```

### STEP 2: ファイルの実読み込み（MUST）

**⚠️ diffだけに頼らず、重要ファイルは必ずReadツールで実際のコードを確認すること**

#### 必ずReadで確認すべきファイル

- **新規追加されたファイル**（とくに100行以上）
- **N+1問題の確認が必要なファイル**：
  - `app/workers/**/*_worker.rb`
  - `app/services/**/*.rb`
  - `app/controllers/**/*_controller.rb`
  - `app/models/**/*.rb`（とくにループ処理を含むもの）
- **migrationファイル**：`db/migrate/**/*.rb`
- **コアロジックを含むファイル**（ビジネスロジック、認証・認可など）
- **フロントエンドファイル**（SmartHR Design System準拠チェック用）：
  - `client/src/**/*.tsx`
  - `client/src/**/*.ts`

#### Readが必須な理由

- diffが `[XXX lines truncated]` で切れている場合がある
- 前後のコンテキストを理解するため
- 正確な行番号を特定するため

### STEP 2.5: SmartHR Design Systemの参照（該当する場合）

**フロントエンド変更がある場合のみ**、以下のリソースを確認：

#### SmartHR Design Systemリポジトリの確認手順

1. **コンポーネントガイドラインの確認**
   - `Grep`または`Read`ツールで`~/ghq/github.com/kufu/smarthr-design-system/src/content/`を検索
   - 使用しているコンポーネントの正しい使用方法を確認

2. **実装例の参照**
   - `~/ghq/github.com/kufu/smarthr-design-system/src/components/`で実装パターンを確認
   - 類似のユースケースがないか探す

3. **デザイントークンの確認**
   - `~/ghq/github.com/kufu/smarthr-design-system/src/constants/`でトークン定義を確認
   - カスタムスタイルの代わりにトークンが使えないか検討

**重要**: 判断に迷う場合や、PRで新しいパターンを導入している場合は必ず確認すること

### STEP 3: レビュー観点の確認

以下の観点で実際のコードをチェック：

#### 3-1. N+1問題のチェック（MUST）

以下のパターンがないか確認：
- ループ内でのActiveRecord呼び出し（`map`, `each`, `filter`内での`find_by`, `where`）
- アソシエーション呼び出しで`includes`, `preload`, `eager_load`が未使用
- Workerでの一括処理における繰り返しクエリ

#### 3-2. migrationファイルのチェック（該当する場合）

- migration内容の妥当性
- up/downの整合性
- インデックスやカラムの適切性

#### 3-3. コード品質のチェック（SHOULD）

- 単一責任の原則（SRP）違反
- 適切なエラーハンドリング
- セキュリティ上の問題（SQL injection, XSS, CSRF等）
- パフォーマンス上の問題

#### 3-4. SmartHR Design System準拠チェック（該当する場合）

**フロントエンド（`client/src/**`）の変更がある場合のみ**、以下を確認：

##### スタイリング
- ❌ `styled-components`で不要なスタイル指定をしていないか
- ✅ SmartHR UIコンポーネントのpropsで対応可能な場合はpropsを優先
- ✅ レイアウトは適切なコンポーネントを使用：
  - 縦並び → `Stack`
  - 横並び → `Cluster`
- ⚠️ カスタムCSSが必要な場合、その理由が妥当か

##### コンポーネント使用
- ✅ SmartHR UIの標準コンポーネントを適切に使用しているか
- ❌ 独自実装で代替可能な既存コンポーネントがないか
- ✅ デザイントークン（色、間隔、フォントサイズ等）を使用しているか

##### アクセシビリティ
- ✅ セマンティックなHTMLを使用しているか
- ✅ フォーム要素に適切なラベルがあるか
- ✅ キーボード操作に対応しているか

**重要**: 判断に迷う場合は、以下のリソースを確認：
- **SmartHR Design System公式サイト**: [https://smarthr.design](https://smarthr.design)
- **ローカルリポジトリ**: `~/ghq/github.com/kufu/smarthr-design-system`
  - コンポーネントガイドライン: `src/content/`
  - 実装例: `src/components/`
  - デザイントークン: `src/constants/`

#### 3-5. PRのdescriptionとの整合性確認（MUST）

コードの変更内容が、PRのdescriptionの「やったこと」に沿っているか確認

### STEP 4: 出力の作成

以下の形式でレビュー結果をまとめる

---

## 出力フォーマット

### PR情報

- **タイトル**: [PRタイトル]
- **作成者**: [作成者名]
- **状態**: [OPEN/MERGED/CLOSED]
- **ブランチ**: [headブランチ] → [baseブランチ]
- **関連チケット**: [チケット番号]

### やりたいこと

[PRのdescriptionから抽出]

### やったこと

[PRのdescriptionから抽出]

---

### 変更内容のまとめ

各変更ファイルについて以下を記載：

#### `[相対パス]`

**変更行**: [Readツールで確認した実際の行番号]

**変更概要**: [変更内容の説明]

---

### ✅ 良い点

実装の優れている点や評価すべき点を列挙

---

### ⚠️ 修正が必要な点

**重要**: 実際に修正が必要な項目のみ記載すること

#### [連番]. [問題の概要]

**ファイル**: `[相対パス]:[行番号]`

**問題点**:
[なぜ修正が必要か]

**修正案**:
```[言語]
[具体的なコード例]
```

---

### PRのdescriptionとの整合性

✅ 整合性あり / ⚠️ 差異あり

[差異がある場合は詳細を記載]

---

### 必須確認項目

- [ ] migrationファイルの確認（該当する場合）
- [ ] N+1問題の確認（該当する場合）
- [ ] SmartHR Design System準拠の確認（フロントエンド変更がある場合）

---

### 総評

[全体的な評価と承認推奨度]

**承認推奨**: ✅ / ⚠️条件付き / ❌要修正

---

## 制約事項（MUST NOT）

以下の行為は**禁止**：

- ❌ diffが切れている部分について**推測で書く**
- ❌ Readツールで確認していないコードの**行番号を書く**
- ❌ 存在しないメソッドやコードについて**言及する**
- ❌ 修正不要な項目を「⚠️ 修正が必要な点」に**含める**
- ❌ 「結論: 問題なし」のような**無意味な項目を書く**

---

## 使用例

```bash
/review-pr https://github.com/owner/repo/pull/12345
```
