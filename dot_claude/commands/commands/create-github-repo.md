# create-github-repo

GitHubのリポジトリを作成し、ghqでcloneするカスタムコマンド

## 実行内容

1. GitHubリポジトリの作成に必要な情報を収集
2. GitHubリポジトリを作成（README.mdと.gitignore付き）
3. `ghq get -p`でリポジトリをclone
4. 作業ディレクトリへの移動コマンドを表示

## 必要な情報

以下の情報をインタラクティブに収集します：

- **リポジトリ名** (必須)
  - 命名規則: 小文字とハイフンを使用（例: my-awesome-project）
  
- **description** (任意)
  - リポジトリの説明文
  
- **公開/非公開** (デフォルト: private)
  - public または private
  
- **.gitignoreテンプレート** (任意)
  - 使用する言語/フレームワーク（例: Node, Python, Ruby, Go等）

## 実行手順

```bash
# 1. 必要な情報の確認
echo "GitHubリポジトリを作成します。必要な情報を教えてください。"

# 2. リポジトリ作成
gh repo create [owner/]repo-name \
  --description "description" \
  --private/--public \
  --gitignore template \
  --add-readme

# 3. ghqでclone
ghq get -p github.com/[owner]/repo-name

# 4. 作業ディレクトリへの移動コマンドを表示
echo "✅ リポジトリの作成とcloneが完了しました。"
echo "作業ディレクトリに移動するには以下のコマンドを実行してください:"
echo ""
echo "cd $(ghq root)/github.com/[owner]/repo-name"
```

## 使用例

```
/create-github-repo

> リポジトリ名を教えてください: my-awesome-project
> descriptionを教えてください（任意）: This is an awesome project
> 公開設定（public/private）[private]: private
> .gitignoreテンプレート（Node, Python等）[なし]: Node

GitHubリポジトリを作成しています...
✓ リポジトリを作成しました: https://github.com/username/my-awesome-project
✓ ghqでcloneしました

✅ リポジトリの作成とcloneが完了しました。
作業ディレクトリに移動するには以下のコマンドを実行してください:

cd ~/ghq/github.com/username/my-awesome-project
```

## 注意事項

- GitHub CLIがインストールされ、認証されている必要があります
- ghqがインストールされている必要があります
- 不足している情報はインタラクティブに質問します
- Claude Codeのセッション上では作業ディレクトリの移動ができないため、移動コマンドをコピペ可能な形式で表示します