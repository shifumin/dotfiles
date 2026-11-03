# Git Conventions (Claude Code)

## Commit Messages

Do not append a `Claude-Session:` trailer. The URL does not resolve for local CLI sessions, so it adds no value to shared history; the commit body carries the reasoning instead. This is not controlled by the `attribution` setting in `settings.json` (which only suppresses the `Co-Authored-By` / `Generated with Claude Code` footer), so it must be stated here.
