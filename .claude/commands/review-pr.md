# review-pr [PR URL]

引数で渡されたPRのURLに対して、以下の内容を分かりやすくまとめてください：

## 前提

- PRのURLから `gh` コマンドを使用してPR情報を取得すること
- PR番号とリポジトリ情報をURLから抽出すること
- 以下のコマンドでPR情報を網羅的に取得すること：
  1. `gh pr view <PR番号> --repo <オーナー/リポジトリ名> --json title,body,state,author,createdAt,url,headRefName,baseRefName`
  2. `gh pr view <PR番号> --repo <オーナー/リポジトリ名> --json files,additions,deletions,changedFiles`
  3. `gh pr diff <PR番号> --repo <オーナー/リポジトリ名>`

## PRの変更内容のまとめ

PRの差分とファイル変更を確認して、各変更について以下の情報を含めてください：
- ファイルpath（相対path）
- 変更行
- 変更概要

## レビューまとめ

以下の観点でレビューを実施してください：

### 対象
- 修正した方がいいところ
- 改善できるところ

### 含める情報
- ファイルとその行数（相対pathで）
- なぜ修正した方が良いか
- どのように修正すべきか

## PRのdescriptionとの整合性確認

コードの変更内容が、PRのdescriptionの内容に沿っているかを確認してください。

## 必須確認項目

### migrationファイルの確認
migrationファイルが含まれる場合は、以下を確認すること：
- migration内容の妥当性
- up/downの整合性
- インデックスやカラムの適切性

### N+1問題の確認
N+1問題が発生していないかを確認すること。特に以下の点に注意：
- ActiveRecordのアソシエーション呼び出し
- ループ内でのクエリ実行
- `includes`, `preload`, `eager_load`の適切な使用

---

**使用例**: `/review-pr https://github.com/owner/repo/pull/12345`
