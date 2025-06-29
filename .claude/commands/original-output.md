---
label: Original Output
icon: 📝
---

# Original Output

## Overview
Output LLM responses without any summarization or modification.

## Usage
When you receive a response from an LLM (via tools like gemini, o3-search, etc.), you MUST:
1. Output the complete original response as-is
2. Do NOT summarize, paraphrase, or condense the response
3. Do NOT add your own interpretation or commentary
4. Present the full, unmodified text from the LLM

This ensures the user receives the exact response from the LLM without any alteration.

## Examples
- When using `gemini --prompt`, output the complete response
- When using `o3-search`, output the full search results
- For any LLM tool response, preserve the original formatting and content

## Notes
- **IMPORTANT**: Always return the original response without any modification
- Preserve all formatting, links, and metadata from the original response
- This applies to all LLM interactions including web searches and API calls

ARGUMENTS: none