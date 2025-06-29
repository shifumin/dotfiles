---
label: Gemini 2.5 Pro Web Search Execution
icon: 🔍
---

# Gemini 2.5 Pro Web Search Execution

## Overview
Uses Playwright MCP to execute a specified prompt on Gemini web interface (https://gemini.google.com/app) with Gemini 2.5 Pro model.

## Steps

### 1. Create TodoList
```javascript
const todos = [
  { id: "1", content: "Navigate to Gemini web interface", status: "pending", priority: "high" },
  { id: "2", content: "Select Gemini 2.5 Pro model if available", status: "pending", priority: "high" },
  { id: "3", content: "Execute prompt and wait for response", status: "pending", priority: "high" },
  { id: "4", content: "Capture and report the response content", status: "pending", priority: "high" }
];
```

### 2. Navigate to Gemini Web Interface
```javascript
// Navigate to Gemini web interface
await mcp__playwright__browser_navigate({ url: "https://gemini.google.com/app?hl=ja" });
```

### 3. Check and Select Model (if model selector is available)
```javascript
// Take snapshot to check current state
const snapshot = await mcp__playwright__browser_snapshot();

// If model selector is visible, select Gemini 2.5 Pro
// Note: Model selection UI may vary or not be available
```

### 4. Execute Prompt
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
```

### 5. Wait for Response
```javascript
// Wait for response generation (max 90 seconds)
let waitTime = 0;
while (waitTime < 90) {
  await mcp__playwright__browser_wait_for({ time: 5 });
  waitTime += 5;
  
  // Take snapshot to check status
  const snapshot = await mcp__playwright__browser_snapshot();
  
  // Check if generation is complete
  // Look for indicators that response is still being generated
  if (!snapshot.includes("生成中") && !snapshot.includes("入力中") && !snapshot.includes("考え中")) {
    break;
  }
}
```

### 6. Capture Response
```javascript
// Take final snapshot to capture the complete response
const finalSnapshot = await mcp__playwright__browser_snapshot();

// Optional: Take a screenshot for visual record
await mcp__playwright__browser_take_screenshot({ 
  filename: "gemini-response.png" 
});
```

### 7. Report Results
Once the response is complete:
1. Capture the full original response from Gemini 2.5 Pro
2. Get the URL from the browser if a shareable link is available
3. Report the original response as-is without any summarization or modification
4. Include the URL to the chat if available

## Notes
- Google account login may be required
- The Gemini web interface may change, requiring adjustments to the interaction flow
- Response generation time varies based on prompt complexity
- The interface language is set to Japanese (?hl=ja) but can be adjusted
- Model selection may not always be available in the web interface
- **IMPORTANT**: The original Gemini 2.5 Pro response must be returned as-is without any summarization or modification
- The URL to the chat should be included in the report if available

ARGUMENTS: {{prompt}}