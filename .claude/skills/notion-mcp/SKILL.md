---
description: Notion MCPツールを使ってNotionのページ・データベース・データソースを取得・検索・作成・更新する。
  「Notionに保存」「Notionから取得」「Notionページを更新」「notion-mcp」
  「Notion検索」「Notionページを作成」などのリクエストで使用。
  Notionリンク（`https://www.notion.so/...`）が会話に現れた時にも必ず使う。
  ページ高レベル操作は `mcp__claude_ai_Notion__notion-*` 名前空間、
  ブロック低レベルAPIは `mcp__notion__API-*` 名前空間に分かれている点に注意。
---

# Notion MCP

NotionのページやデータベースをMCPツール経由で操作する。

## ツール対応表

| 操作 | ツール | 備考 |
|------|--------|------|
| ページ・DB・データソース取得 | `mcp__claude_ai_Notion__notion-fetch` | プロパティと本文を返す。URL/UUIDどちらでもOK |
| ワークスペース検索 | `mcp__claude_ai_Notion__notion-search` | ページ・接続済みソース横断のセマンティック検索 |
| ページ作成 | `mcp__claude_ai_Notion__notion-create-pages` | 新規ページ追加時 |
| ページ更新 | `mcp__claude_ai_Notion__notion-update-page` | プロパティや本文の修正 |

ページ・DBの高レベル操作は `mcp__claude_ai_Notion__notion-*` 名前空間。
ブロック単位の低レベルAPI（block childrenのget/append/update等）は `mcp__notion__API-*` 名前空間を使う。
実行時に該当ツールが無ければ、同じ名前空間内で説明が一致するものを優先する（ツール名は変わり得るので、この表は契約ではなく参考）。

## Page IDの抽出

`notion-fetch` には可能な限りURLをそのまま渡す。UUIDが必要な場合は、URL末尾32文字（ハイフン無し）を取り出して `8-4-4-4-12` 形式に整形する。

例: `https://www.notion.so/WF-1000XM4-6199211160cd4d0d9211311a3229c58b`
→ Page ID: `61992111-60cd-4d0d-9211-311a3229c58b`

## Fetch before update

外部ドキュメント更新の鉄則: **更新前に必ず最新リモート状態を取得**し、それを基に編集する。並行する人手編集を上書きしてはならない。
