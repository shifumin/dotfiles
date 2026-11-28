eval "$(/opt/homebrew/bin/brew shellenv)"

# mise shims for non-interactive login shells (e.g. Tinycast custom commands run `zsh -lc`)
# .zshrc.custom still runs `mise activate zsh` for interactive shells
export PATH="$HOME/.local/share/mise/shims:$PATH"

# Added by Obsidian
export PATH="$PATH:/Applications/Obsidian.app/Contents/MacOS"
