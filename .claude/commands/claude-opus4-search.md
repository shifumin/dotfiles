---
label: Claude Opus 4 Web Search Execution
icon: 🔍
---

# Claude Opus 4 Web Search Execution

## Overview
Uses Playwright MCP to execute a specified prompt on Claude.ai with Opus 4 model and web search enabled.

## Steps

### 1. Create TodoList
```javascript
const todos = [
  { id: "1", content: "Navigate to Claude.ai new chat", status: "pending", priority: "high" },
  { id: "2", content: "Select Claude Opus 4 model", status: "pending", priority: "high" },
  { id: "3", content: "Enable web search functionality", status: "pending", priority: "high" },
  { id: "4", content: "Execute prompt and wait for response", status: "pending", priority: "high" },
  { id: "5", content: "Capture and report the response content with permanent link", status: "pending", priority: "high" }
];
```

### 2. Navigate to Claude
```javascript
// Navigate to Claude new chat
await mcp__playwright__browser_navigate({ url: "https://claude.ai/new" });
```

### 3. Select Opus 4 Model
```javascript
// Take snapshot to check current state
const snapshot = await mcp__playwright__browser_snapshot();

// Click model selector if Opus 4 is not selected
if (!snapshot.includes("Opus 4")) {
  // Click model selector button
  await mcp__playwright__browser_click({ 
    element: "Model selector button", 
    ref: "dynamic-ref" // actual ref will be determined from snapshot
  });
  
  // Wait for model menu to appear
  await mcp__playwright__browser_wait_for({ time: 1 });
  
  // Select Opus 4 model
  await mcp__playwright__browser_click({ 
    element: "Claude Opus 4 option", 
    ref: "dynamic-ref" // actual ref will be determined from snapshot
  });
}
```

### 4. Enable Web Search
```javascript
// Look for web search toggle or button
// Note: The exact UI element may vary based on Claude's interface
await mcp__playwright__browser_click({ 
  element: "Web search toggle/button", 
  ref: "dynamic-ref" // actual ref will be determined from snapshot
});
```

### 5. Execute Prompt
```javascript
// Click on the message input area
await mcp__playwright__browser_click({ 
  element: "Message input field", 
  ref: "dynamic-ref" // actual ref will be determined from snapshot
});

// Clear any existing text
await mcp__playwright__browser_press_key({ key: "Control+a" });

// Type the prompt
await mcp__playwright__browser_type({ 
  element: "Message input field", 
  ref: "dynamic-ref", // actual ref will be determined from snapshot
  text: "{{prompt}}",
  submit: false // Don't submit yet
});

// Submit the prompt
await mcp__playwright__browser_press_key({ key: "Enter" });
// Or click send button if available
// await mcp__playwright__browser_click({ 
//   element: "Send button", 
//   ref: "dynamic-ref"
// });
```

### 6. Wait for Response
```javascript
// Wait for response generation (max 120 seconds for Opus 4)
let waitTime = 0;
while (waitTime < 120) {
  await mcp__playwright__browser_wait_for({ time: 5 });
  waitTime += 5;
  
  // Take snapshot to check status
  const snapshot = await mcp__playwright__browser_snapshot();
  
  // Check if generation is complete
  // Look for indicators that response is still being generated
  if (!snapshot.includes("Thinking") && !snapshot.includes("Searching") && !snapshot.includes("Writing")) {
    // Check that response content is visible
    if (snapshot.includes("paragraph") || snapshot.includes("text")) {
      break;
    }
  }
}

// Additional wait to ensure response is fully rendered
await mcp__playwright__browser_wait_for({ time: 2 });
```

### 7. Capture Response and URL
```javascript
// Take final snapshot to capture the complete response
const finalSnapshot = await mcp__playwright__browser_snapshot();

// Get the current URL which should contain the chat ID
const currentUrl = await mcp__playwright__browser_network_requests();
// Extract URL from page or browser state
```

### 8. Report Results
Once the response is complete:
1. Capture the full original response from Claude Opus 4
2. Get the permanent link URL from the browser (should be in format: https://claude.ai/chat/[chat-id])
3. Report the original response as-is without any summarization or modification
4. Include the permanent link to the chat in the report

## Notes
- Claude.ai login is required
- Access to Opus 4 model is required (may require subscription)
- Web search feature availability may depend on account settings
- Response generation may take longer with web search enabled (30 seconds to 2 minutes)
- **IMPORTANT**: The original Opus 4 response must be returned as-is without any summarization or modification
- The permanent link to the chat should be included in the report
- Interface elements may change; adjust selectors as needed

ARGUMENTS: {{prompt}}