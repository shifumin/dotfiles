---
description: 会話中の調査結果・研究成果・分析内容をNotionプライベートページとして保存する。
  「Notionに保存」「調査結果をNotionに」「Notionページを作成」「save to Notion」
  「研究結果を保存」「分析をNotionに記録」などのリクエストで使用。
---

# Notionへの保存

会話中の調査結果・研究成果・分析内容をNotionのプライベートページとして保存する。

## 処理フロー

### Step 1: 保存内容の特定

会話コンテキストから保存すべき内容を特定する。

| 情報源 | 対象 |
|--------|------|
| 会話履歴 | 調査結果、分析、コードレビュー、技術検証の結論 |
| ユーザー指示 | 「さっきの調査結果を」「この分析を」等 |

ユーザーが保存範囲を明示していない場合、AskUserQuestionで確認:
- 保存する内容の範囲（会話全体 or 特定の部分）
- ページタイトル（提案してユーザーに確認）

### Step 2: Notion Markdown仕様の取得

**必須**: ページ作成前にMCPリソースを読み込む。

```
ReadMcpResourceTool: server=notion, uri=notion://docs/enhanced-markdown-spec
```

主要な変換ルールは `~/.claude/skills/saving-to-notion/reference.md` も参照。

### Step 3: コンテンツの構成

コンテンツの一番最初に、箇条書きで更新日時を記載する:

```
- updated_at: YYYY-MM-DD
```

日付は保存実行時の当日日付を使用する。

その後、会話内容を以下の構成でNotionページ向けに整理する:

| セクション | 内容 | 必須 |
|-----------|------|------|
| 背景・目的 | なぜこの調査/分析を行ったか | 推奨 |
| 調査内容・分析 | 本体（発見事項、コード例、比較等） | 必須 |
| 結論・まとめ | 要点の整理 | 推奨 |
| 参考リンク | 参照したURL、ドキュメント | 該当時 |

### Step 4: Markdown変換

標準MarkdownをNotion-flavored Markdownに変換する。

主な変換ポイント（詳細は `~/.claude/skills/saving-to-notion/reference.md` 参照）:

| 標準Markdown | Notion-flavored Markdown |
|-------------|--------------------------|
| パイプテーブル | `<table>` XML形式 |
| 複数行引用（`>`を並べる） | `> Line1<br>Line2` で1ブロック化 |
| 空行 | 削除（必要なら `<empty-block/>`） |
| コードブロック | 同じ（内部のエスケープ不要） |

**使用禁止の書式**:
- callout（`::: callout` 構文）: プレーンテキストとして表示される不具合あり

### Step 5: ページ作成

`mcp__notion__notion-create-pages` でプライベートページを作成する。

**重要**: `parent` パラメータに「調査メモ」ページのIDを指定し、サブページとして作成する。

```json
{
  "parent": {"page_id": "30c37b6398eb806c82fcc78cf00ff428"},
  "pages": [
    {
      "properties": {"title": "ページタイトル"},
      "content": "Notion-flavored Markdownコンテンツ"
    }
  ]
}
```

**注意**: ページタイトルは `properties.title` で設定し、`content` の先頭には含めない。

### Step 6: 結果の報告

ページ作成後、以下の情報をユーザーに報告する:

- ページタイトル
- ページURL（`mcp__notion__notion-create-pages` のレスポンスから取得）
- 保存した内容の概要

## エラー処理

| エラーパターン | 原因 | 対処 |
|---------------|------|------|
| Notion MCPツールが利用不可 | MCP未接続 | ToolSearchでNotionツールを検索。見つからない場合はユーザーにMCP接続を案内 |
| ページ作成失敗 | APIエラー | エラー詳細を報告し、コンテンツを通常Markdownで表示（手動コピー用） |
| コンテンツが長すぎる | Notion API制限 | 内容を要約するか、複数ページに分割を提案 |

## 制限事項

- 画像のアップロード不可（外部URL参照のみ可能）
- ファイル添付不可（テキストコンテンツのみ）
- デフォルトの保存先は「調査メモ」ページ（サブページとして作成）

## 技術仕様

Notion-flavored Markdownの変換ルール詳細は `~/.claude/skills/saving-to-notion/reference.md` を参照。
