---
label: Multi-LLM Web Search Execution
icon: 🔍
---

# Multi-LLM Web Search Execution

## Overview
Executes a single prompt across three LLMs simultaneously: ChatGPT O3, Claude Opus 4, and Gemini 2.5 Pro, all with web search enabled.

## Steps

### 1. Create TodoList
```javascript
const todos = [
  { id: "1", content: "Execute prompt on ChatGPT O3 with web search", status: "pending", priority: "high" },
  { id: "2", content: "Execute prompt on Claude Opus 4 with Research", status: "pending", priority: "high" },
  { id: "3", content: "Execute prompt on Gemini 2.5 Pro", status: "pending", priority: "high" },
  { id: "4", content: "Collect and report all responses with permanent links", status: "pending", priority: "high" }
];
```

### 2. Execute on All Three LLMs in Parallel

Since we can only have one browser instance at a time with Playwright MCP, we'll execute them sequentially but efficiently.

#### 2.1 ChatGPT O3 Execution
```javascript
// Navigate to ChatGPT
await mcp__playwright__browser_navigate({ url: "https://chatgpt.com" });

// Wait for page load
await mcp__playwright__browser_wait_for({ time: 3 });

// Select O3 model if not already selected
const chatgptSnapshot = await mcp__playwright__browser_snapshot();
if (!chatgptSnapshot.includes("o3")) {
  // Click model selector and select O3
  // ... (follow chatgpt-o3-search.md steps)
}

// Enable web search
// ... (follow chatgpt-o3-search.md steps)

// Execute prompt
// ... (follow chatgpt-o3-search.md steps)

// Wait for response and capture
// ... (follow chatgpt-o3-search.md steps)

// Store ChatGPT response and URL
const chatgptResponse = "..."; // Extract from snapshot
const chatgptUrl = "..."; // Get current URL
```

#### 2.2 Claude Opus 4 Execution
```javascript
// Open new tab for Claude
await mcp__playwright__browser_tab_new({ url: "https://claude.ai/new" });

// Wait for page load
await mcp__playwright__browser_wait_for({ time: 3 });

// Select Opus 4 model if not already selected
// ... (follow claude-opus4-search.md steps)

// Enable Research
// ... (follow claude-opus4-search.md steps)

// Execute prompt
// ... (follow claude-opus4-search.md steps)

// Wait for response and capture
// ... (follow claude-opus4-search.md steps)

// Store Claude response and URL
const claudeResponse = "..."; // Extract from snapshot
const claudeUrl = "..."; // Get current URL
```

#### 2.3 Gemini 2.5 Pro Execution
```javascript
// Open new tab for Gemini
await mcp__playwright__browser_tab_new({ url: "https://gemini.google.com/app?hl=ja" });

// Wait for page load
await mcp__playwright__browser_wait_for({ time: 3 });

// Select 2.5 Pro model if not already selected
// ... (follow gemini-25pro-search.md steps)

// Execute prompt
// ... (follow gemini-25pro-search.md steps)

// Wait for response and capture
// ... (follow gemini-25pro-search.md steps)

// Store Gemini response and URL
const geminiResponse = "..."; // Extract from snapshot
const geminiUrl = "..."; // Get current URL
```

### 3. Report Combined Results

Once all three LLMs have completed their responses:

1. Report each LLM's original response without any summarization or modification
2. Include the permanent link for each chat
3. Present them in a clear, organized format:

```markdown
## ChatGPT O3 Response
[Original response as-is]
**URL**: [ChatGPT URL]

---

## Claude Opus 4 Response
[Original response as-is]
**URL**: [Claude URL]

---

## Gemini 2.5 Pro Response
[Original response as-is]
**URL**: [Gemini URL]
```

### 4. Optional: Take Screenshots
```javascript
// Take screenshots of each response for visual record
await mcp__playwright__browser_tab_select({ index: 0 });
await mcp__playwright__browser_take_screenshot({ filename: "chatgpt-o3-response.png" });

await mcp__playwright__browser_tab_select({ index: 1 });
await mcp__playwright__browser_take_screenshot({ filename: "claude-opus4-response.png" });

await mcp__playwright__browser_tab_select({ index: 2 });
await mcp__playwright__browser_take_screenshot({ filename: "gemini-25pro-response.png" });
```

## Notes
- Requires login to all three services (ChatGPT, Claude, Gemini)
- Requires appropriate subscriptions for premium models (O3, Opus 4, 2.5 Pro)
- Total execution time may be 3-5 minutes due to sequential execution
- **IMPORTANT**: All LLM responses must be returned as-is without any summarization or modification
- Permanent links to each chat should be included in the report
- Browser tabs are used to maintain all three sessions simultaneously
- Web search features may behave differently across platforms:
  - ChatGPT O3: Explicit web search tool selection
  - Claude Opus 4: Research feature (may ask clarifying questions)
  - Gemini 2.5 Pro: Integrated web search capabilities

## Error Handling
- If a model is not available, note it in the response
- If web search fails to activate, proceed with standard query
- If login is required, pause and notify user

ARGUMENTS: {{prompt}}