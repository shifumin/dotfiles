変更内容をcommitしてpushしてください

## 手順

### 1. 現在の状態を確認
- `git status` で変更ファイルを確認
- 変更がない場合 → 「変更がありません」と報告して終了

### 2. 変更内容を分析
- `git diff` で未ステージの変更内容を確認
- `git diff --staged` でステージ済みの変更内容を確認

### 3. コミット粒度を判断
以下の基準で変更を論理的なまとまりに分ける:
- 機能追加 (feat)
- バグ修正 (fix)
- リファクタリング (refactor)
- ドキュメント (docs)
- スタイル修正 (style)
- テスト (test)
- その他 (chore)

複数の種類が混在する場合は、種類ごとに別コミットにする。
1種類の変更のみの場合は、1コミットにまとめる。

### 4. コミットを作成
- 各コミットに対して `git add` → `git commit` を実行
- コミットメッセージは Conventional Commits 形式（英語）:
  - `feat: add ...`
  - `fix: fix ...`
  - `refactor: refactor ...`
  - `docs: update ...`
  - `style: fix code style`
  - `test: add tests for ...`
  - `chore: update ...`

### 5. pushを実行
- `git push` を実行
- push失敗時はエラー内容を報告

## 注意事項
- 秘匿情報（APIキー、パスワード等）が含まれていないか確認
- push先ブランチが正しいか確認
