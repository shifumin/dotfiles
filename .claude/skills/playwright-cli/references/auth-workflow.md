# Authentication Workflow

認証が必要なサイト（Amazon、Gmail等）にplaywright-cliでアクセスする際のパターン。

## 最短パス

### 初回（まだログインしていない場合）

```bash
# headed + persistent で開く（UIありで永続プロファイル使用）
playwright-cli open --headed --persistent "https://..."
# → ユーザーが手動ログイン
# → Cookieが永続プロファイルに自動保存
playwright-cli snapshot
playwright-cli close
```

### 2回目以降（永続プロファイルにCookieがある場合）

```bash
# persistent のみで十分（headedは不要、headlessでOK）
playwright-cli open --persistent "https://..."
# → 前回のCookieで自動ログイン
playwright-cli snapshot
playwright-cli close
```

### ログインページにリダイレクトされた場合

```bash
# headlessで開いてリダイレクトされた → 閉じてheadedで開き直す
playwright-cli close
playwright-cli open --headed --persistent "https://..."
# → ユーザーに手動ログインを依頼
```

## 判断フロー

1. 認証が必要なサイトか判断
2. `--persistent` で開く
3. ページURLを確認 → ログインページにリダイレクト？
   - No → そのまま操作続行
   - Yes → `close` → `--headed --persistent` で開き直し → ユーザーにログイン依頼

## 重要な注意点

- headedモードは `--headed` フラグのみ有効（環境変数 `PLAYWRIGHT_HEADED=1` やconfig JSONは効かない）
- `--persistent` のプロファイルは `~/Library/Caches/ms-playwright/daemon/*/` に保存される
- `state-save`/`state-load` はCookie/localStorageの明示的バックアップ用（通常は `--persistent` で十分）

## 認証済みサイト一覧

| サイト | URL例 | 備考 |
|--------|-------|------|
| Amazon | amazon.co.jp/your-orders/* | 注文詳細、配送状況 |
