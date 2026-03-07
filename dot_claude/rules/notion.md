# Notion Integration

When Notion link content (`https://www.notion.so/...`) is needed, use Notion MCP tools.

## Tools

| Operation | Tool | Purpose |
|-----------|------|---------|
| Get page | `mcp__notion__API-retrieve-a-page` | Retrieve properties |
| Get content | `mcp__notion__API-get-block-children` | Retrieve page body |
| Search | `mcp__notion__API-post-search` | Search by title |

## Page ID Extraction

Extract last 32 characters (without hyphens) from URL, convert to UUID format.

Example: `https://www.notion.so/WF-1000XM4-6199211160cd4d0d9211311a3229c58b`
→ Page ID: `61992111-60cd-4d0d-9211-311a3229c58b`
