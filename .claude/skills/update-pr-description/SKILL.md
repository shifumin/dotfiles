---
name: update-pr-description
description: "既存 PR の説明文（body）を最新コードに合わせて人が読みやすく書き直し、承認後に更新する。「PRのディスクリプションを最新に」「説明文を見直して」「本文を変更内容に合わせて」「冗長なところを省いて」等で使用。対象外: 新規 PR 作成（リポジトリ専用スキル優先）。"
---

# PR 説明文の更新

PR の本文を最新の diff に合わせ、コードを読まない人にも一読で伝わる内容へ整える。**承認なしで更新しない**。

PR 操作用 MCP ツール（`pull_request_read` / `pull_request_update`）が使える環境ではそちらを優先し、CLI 環境では `gh` を使う。

## 手順

1. **現在の本文と差分を取得する**（PR 番号省略時は現在ブランチの PR。PR が見つからない・diff が空なら確認して終了）:
   ```bash
   BODY_FILE=$(mktemp "${TMPDIR:-/tmp}/pr-body.XXXXXX.md")
   gh pr view [<number>] --json title,body,commits,baseRefName,headRefOid
   gh pr diff [<number>]
   ```
   取得した現在本文を `"$BODY_FILE"` へ控えておく。
2. **食い違いを洗い出す**: 本文と diff を照合し、事実と異なる記述、抜けている変更、決着済みの「検討中」を拾う。
3. **本文を書き直す**
   - リポジトリの PR テンプレートや説明文用スキルがあればその構成に従う
   - コードを読まない人前提で書き、クラス名・メソッド名・内部処理名は利用者や運用者から見た挙動へ言い換える
   - 冗長な説明・感情表現・テスト実行結果は省き、頼まれていない節を足さない
   - 出力（CSV 列・通知文など）が変わる場合は変更前後を表で示す
4. **承認を取る**: 変わる箇所を before / after で提示し、承認を得る。
5. **最新本文を再取得して反映する**（同時編集保護: `AGENTS.md` Principle 2）:
   - 更新直前にリモート本文を再取得し、手順 1 から人手の編集が入っていればその差分を保ったまま今回の変更を統合する
   - 承認済み本文を `"$BODY_FILE"` に書いて更新し、読み返して一致を検証したあと一時ファイルを削除する（末尾改行の差は許容）:
     ```bash
     gh pr edit [<number>] --body-file "$BODY_FILE"
     gh pr view [<number>] --json body
     command rm -f "$BODY_FILE"
     ```
