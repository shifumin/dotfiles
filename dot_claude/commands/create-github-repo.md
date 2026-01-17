# create-github-repo

GitHubリポジトリを作成し、ghqでcloneするコマンド。

## 収集する情報

| 項目 | 必須 | デフォルト | 例 |
|------|------|-----------|-----|
| リポジトリ名 | ✅ | - | `my-awesome-project` |
| description | - | なし | `This is an awesome project` |
| 公開設定 | - | private | `public` / `private` |
| .gitignoreテンプレート | - | なし | `Node`, `Python`, `Ruby`, `Go` |

**命名規則**: 小文字とハイフンを使用

## 実行手順

1. 上記の情報をインタラクティブに収集
2. `gh repo create`でリポジトリ作成（README.md付き）
3. `ghq get -p`でclone
4. 作業ディレクトリへの移動コマンドを表示

```bash
gh repo create owner/repo-name --description "説明" --private --gitignore Node --add-readme
ghq get -p github.com/owner/repo-name
```

## 注意事項

- GitHub CLIがインストールされ、認証されている必要がある
- ghqがインストールされている必要がある
- Claude Codeのセッション上ではディレクトリ移動ができないため、移動コマンドをコピペ可能な形式で表示
