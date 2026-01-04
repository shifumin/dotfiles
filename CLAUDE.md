# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

Personal dotfiles managed with [chezmoi](https://www.chezmoi.io/). This is the **source directory** (`~/.local/share/chezmoi/`), not the target home directory.

## Chezmoi File Naming Conventions

Chezmoi uses special prefixes to control file behavior:

| Prefix | Effect | Example |
|--------|--------|---------|
| `dot_` | Creates file starting with `.` | `dot_zshrc` → `~/.zshrc` |
| `private_` | Sets 0600 permissions | `private_default.yml` |
| `empty_` | Creates empty file | `empty_dot_zshenv` |
| `executable_` | Sets executable bit | `executable_script.sh` |

Directories use `dot_` prefix: `dot_config/` → `~/.config/`

## Common Commands

```bash
# Preview changes before applying
chezmoi diff

# Apply changes to home directory
chezmoi apply

# Add a new file to chezmoi
chezmoi add ~/.newfile

# Edit a managed file (opens source file)
chezmoi edit ~/.zshrc

# Pull and apply latest from remote
chezmoi update

# Go to this source directory
chezmoi cd
```

## Directory Structure

```
dot_zshrc, dot_zshrc.alias, dot_zshrc.custom  # Zsh configuration
dot_config/
├── nvim/          # Neovim (dein.vim plugin manager)
└── ghostty/       # Ghostty terminal
dot_tmuxinator/    # tmuxinator project configs
dot_claude/        # Claude Code settings and custom commands
```

## Workflow

1. Edit files in this source directory (files with `dot_` prefixes)
2. Run `chezmoi diff` to preview
3. Run `chezmoi apply` to apply to home directory
4. Commit and push changes
