# review-pr [PR URL]

引数で渡されたPRのURLに対して、以下の内容を分かりやすくまとめてください：

## 前提

- PRのURLから `gh` コマンドを使用してPR情報を取得すること
- PR番号とリポジトリ情報をURLから抽出すること
- 以下のコマンドでPR情報を網羅的に取得すること：
  1. `gh pr view <PR番号> --repo <オーナー/リポジトリ名> --json title,body,state,author,createdAt,url,headRefName,baseRefName`
  2. `gh pr view <PR番号> --repo <オーナー/リポジトリ名> --json files,additions,deletions,changedFiles`
  3. `gh pr diff <PR番号> --repo <オーナー/リポジトリ名>`

## ⚠️ 重要：ファイルの実読み込み必須

**diffの出力が切れている場合や、レビュー対象の重要なファイルは必ずReadツールで実際のファイルを読み込むこと**

### 必ずReadで確認すべきファイル
- 新規追加されたファイル（特に100行以上）
- N+1問題を確認する必要があるファイル（Worker, Service, Controllerなど）
- migration ファイル
- コアロジックを含むファイル

### 禁止事項
- **diffが `[XXX lines truncated]` で切れている場合、切れた部分について推測で書かない**
- **実際にReadツールで確認していないコードの行番号を書かない**
- **存在しないメソッドやコードについて言及しない**

## PRの変更内容のまとめ

PRの差分とファイル変更を確認して、各変更について以下の情報を含めてください：
- ファイルpath（相対path）
- 変更行（**Readツールで確認した実際の行番号のみ記載**）
- 変更概要

## レビューまとめ

以下の観点でレビューを実施してください：

### 対象
- 修正した方がいいところ
- 改善できるところ

### 含める情報
- ファイルとその行数（相対pathで、**Readツールで実際に確認した行番号のみ**）
- なぜ修正した方が良いか
- どのように修正すべきか（具体的なコード例を含める）

### レビュー手順
1. **まず変更ファイル一覧を確認**（`gh pr view --json files`の結果から）
2. **重要なファイルをReadツールで読み込む**（Worker, Service, Controller, Modelなど）
3. **実際のコードを確認してからレビューコメントを書く**
4. **確認していないファイルについては推測で書かない**

## PRのdescriptionとの整合性確認

コードの変更内容が、PRのdescriptionの内容に沿っているかを確認してください。

## 必須確認項目

### migrationファイルの確認
migrationファイルが含まれる場合は、以下を確認すること：
- migration内容の妥当性
- up/downの整合性
- インデックスやカラムの適切性

### N+1問題の確認
**必ず該当ファイルをReadツールで読み込んでから確認すること**

N+1問題が発生していないかを確認すること。特に以下の点に注意：
- ActiveRecordのアソシエーション呼び出し
- ループ内でのクエリ実行（`map`, `each`, `filter`などの中での`find_by`, `where`呼び出し）
- `includes`, `preload`, `eager_load`の適切な使用
- Workerでの一括処理における繰り返しクエリ

**確認対象ファイル**：
- `app/workers/**/*_worker.rb`
- `app/services/**/*.rb`
- `app/controllers/**/*_controller.rb`
- `app/models/**/*.rb`（特にループ処理を含むもの）

---

**使用例**: `/review-pr https://github.com/owner/repo/pull/12345`
