---
label: ChatGPT O3 Web Search Execution
icon: 🔍
---

# ChatGPT O3 Web Search Execution

## Overview
Uses Playwright MCP to execute a specified prompt on ChatGPT with O3 model and web search enabled.

## Steps

### 1. Create TodoList
```javascript
const todos = [
  { id: "1", content: "Navigate to ChatGPT and select O3 model", status: "pending", priority: "high" },
  { id: "2", content: "Enable web search functionality", status: "pending", priority: "high" },
  { id: "3", content: "Execute prompt and wait for response", status: "pending", priority: "high" },
  { id: "4", content: "Capture and report the response content with permanent link", status: "pending", priority: "high" }
];
```

### 2. Navigate to ChatGPT
```javascript
// Navigate to ChatGPT
await mcp__playwright__browser_navigate({ url: "https://chatgpt.com" });
```

### 3. Select O3 Model
```javascript
// Click model selector
await mcp__playwright__browser_click({ 
  element: "Model selector button", 
  ref: "e632" // actual ref is dynamic
});

// Select O3 model
await mcp__playwright__browser_click({ 
  element: "o3 model option", 
  ref: "e669" // actual ref is dynamic
});
```

### 4. Enable Web Search
```javascript
// Click tools button
await mcp__playwright__browser_click({ 
  element: "Choose tool button", 
  ref: "e548" 
});

// Select web search
await mcp__playwright__browser_click({ 
  element: "Search the web option", 
  ref: "e718" 
});
```

### 5. Execute Prompt
```javascript
// Click text area
await mcp__playwright__browser_click({ 
  element: "Message composer", 
  ref: "e532" 
});

// Select all existing text
await mcp__playwright__browser_press_key({ key: "Control+a" });

// Type prompt and submit
await mcp__playwright__browser_type({ 
  element: "Message composer", 
  ref: "e532",
  text: "{{prompt}}",
  submit: true 
});
```

### 6. Wait for Response
```javascript
// Wait for response generation (max 90 seconds)
let waitTime = 0;
while (waitTime < 90) {
  await mcp__playwright__browser_wait_for({ time: 10 });
  waitTime += 10;
  
  // Take snapshot to check status
  const snapshot = await mcp__playwright__browser_snapshot();
  
  // Check if "Thinking" or "Searching" is still displayed
  if (!snapshot.includes("Thinking") && !snapshot.includes("Searching the web")) {
    break;
  }
}
```

### 7. Report Results
Once the response is complete:
1. Capture the full original response from ChatGPT O3
2. Get the permanent link URL from the browser
3. Report the original response as-is without any summarization or modification
4. Include the permanent link to the chat in the report

## Notes
- ChatGPT login is required
- Access to O3 model is required
- Response generation may take time (30 seconds to 2 minutes)
- **IMPORTANT**: The original O3 response must be returned as-is without any summarization or modification
- The permanent link to the chat should be included in the report

ARGUMENTS: {{prompt}}
