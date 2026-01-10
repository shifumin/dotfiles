変更内容をcommitしてpushする。

---

## 手順

### 1. 状態確認

```bash
git status
git diff
git diff --staged
```

変更がない場合 → 「変更がありません」と報告して終了

### 2. コミット粒度を判断

| 種類 | prefix | 例 |
|------|--------|-----|
| 機能追加 | `feat` | `feat: add user search` |
| バグ修正 | `fix` | `fix: handle null input` |
| リファクタリング | `refactor` | `refactor: extract helper` |
| ドキュメント | `docs` | `docs: update README` |
| スタイル | `style` | `style: format code` |
| テスト | `test` | `test: add unit tests` |
| その他 | `chore` | `chore: update deps` |

**ルール**: 複数種類が混在 → 種類ごとに別コミット

### 3. コミット作成

```bash
git add <files>
git commit -m "<prefix>: <description>"
```

### 4. push

```bash
git push
```

失敗時はエラー内容を報告

---

## 🔴 必須チェック

コミット前に `git diff --staged` で秘匿情報がないか確認（詳細は CLAUDE.md「セキュリティ」セクション参照）
