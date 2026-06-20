# Notion Integration

When Notion link content (`https://www.notion.so/...`) is needed, use Notion MCP tools.

## Tools

| Operation | Tool | Notes |
|-----------|------|-------|
| Fetch page / database / data source | `mcp__claude_ai_Notion__notion-fetch` | Returns properties + body. Accepts URL or UUID directly |
| Search workspace | `mcp__claude_ai_Notion__notion-search` | Semantic search across pages and connected sources |
| Create page(s) | `mcp__claude_ai_Notion__notion-create-pages` | Use when adding new pages |
| Update page | `mcp__claude_ai_Notion__notion-update-page` | Use to modify properties or content |

High-level page/database operations use the `mcp__claude_ai_Notion__notion-*` namespace.
Low-level block operations (get/append/update block children, etc.) use the separate `mcp__notion__API-*` namespace.
If a listed tool is unavailable at runtime, prefer the closest tool in the same namespace whose description matches; tool names may evolve, so treat this table as a reference, not a fixed contract.

## Page ID Extraction

Pass the full URL directly to `notion-fetch` when possible. If a bare UUID is required, extract the last 32 characters (without hyphens) from the URL and reformat to `8-4-4-4-12`.

Example: `https://www.notion.so/WF-1000XM4-6199211160cd4d0d9211311a3229c58b`
→ Page ID: `61992111-60cd-4d0d-9211-311a3229c58b`
