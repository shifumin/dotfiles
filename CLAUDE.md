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

| Command | Description |
|---------|-------------|
| `chezmoi diff` | Preview changes |
| `chezmoi apply` | Apply to home directory |
| `chezmoi add <file>` | Add file to chezmoi |
| `chezmoi edit <file>` | Edit source file |
| `chezmoi update` | Pull and apply from remote |
| `chezmoi cd` | Go to source directory |

## Directory Structure

```
dot_zshrc, dot_zshrc.alias, dot_zshrc.custom  # Zsh configuration
dot_config/
├── sheldon/       # Zsh plugin manager (sheldon)
├── nvim/          # Neovim (dein.vim plugin manager)
└── ghostty/       # Ghostty terminal
dot_tmuxinator/    # tmuxinator project configs
dot_claude/        # Claude Code settings
├── commands/      # Custom slash commands
└── skills/        # Skills (google-calendar, github)
```

## Zsh Plugin Management

Zsh plugins are managed with [Sheldon](https://sheldon.cli.rs/).

```bash
sheldon lock           # Install/update plugins
sheldon lock --update  # Force update all plugins
```

Plugin configuration: `~/.config/sheldon/plugins.toml`

### Key Plugins

- **[fzf](https://github.com/junegunn/fzf)** - Fuzzy finder (`Ctrl+R`, `Ctrl+T`, `Alt+C`)
- **[forgit](https://github.com/wfxr/forgit)** - Git with fzf (`ga`, `gcb`, `glo`, `gd`)
- **[fzf-zsh-plugin](https://github.com/unixorn/fzf-zsh-plugin)** - tmux, kill, etc. (`tm`, `fzf-kill`)

## Workflow

1. Edit source files (with `dot_` prefixes)
2. `chezmoi diff` → `chezmoi apply`
3. Commit and push
