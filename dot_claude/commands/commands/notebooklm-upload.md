---
name: notebooklm-upload
instruction: Upload a file to NotebookLM and create an audio overview
system_prompt: |
  You are helping the user upload a file to NotebookLM and create an audio overview using Playwright MCP.
  
  Follow these steps:
  1. Navigate to https://notebooklm.google.com/
  2. Check if the user is logged in (look for account info in the top right)
  3. If not logged in, inform the user they need to log in first
  4. Create a new notebook by clicking "ノートブックを新規作成" or similar button
  5. Click "ファイルを選択" or similar button to open file dialog
  6. Use browser_file_upload with the provided file path
  7. Wait for the file to upload and the notebook to be created
  8. Click on "Studio" tab
  9. Click on "音声概要" button to start audio generation
  10. Inform the user that audio generation has started and typically takes 2-5 minutes
  
  Important notes:
  - The file path must be absolute, not relative
  - Supported file formats: PDF, .txt, Markdown, audio (e.g., mp3), .png, .jpg, .jpeg
  - Audio generation can take several minutes depending on file size and complexity
  - The generated audio will be a podcast-style conversation between two AI hosts
arguments:
  file_path:
    description: Absolute path to the file to upload to NotebookLM
    required: true
examples:
  - description: Upload a PDF file
    arguments:
      file_path: /Users/username/Documents/example.pdf
  - description: Upload a text file
    arguments:
      file_path: /Users/username/notes/meeting-notes.txt
---

1. Navigate to NotebookLM
2. Check login status
3. Create new notebook
4. Upload the file from: {{ file_path }}
5. Navigate to Studio tab
6. Generate audio overview
7. Wait for completion and notify user