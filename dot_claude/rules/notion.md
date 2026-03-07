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

Example: `https://www.notion.so/Sample-Page-0123456789abcdef0123456789abcdef`
→ Page ID: `01234567-89ab-cdef-0123-456789abcdef`
