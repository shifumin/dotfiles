# CLAUDE.md

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

## Directory Structure

```
dot_zshrc, dot_zshrc.alias, dot_zshrc.custom  # Zsh configuration
dot_zprofile                                   # Zsh profile
dot_gitconfig, dot_gitignore                   # Git
dot_tigrc                                      # tig (Git UI)
dot_tmux.conf                                  # tmux
dot_pryrc, dot_gemrc, dot_rspec, dot_default-gems  # Ruby
dot_default-npm-packages                       # Node.js
dot_obsidian.vimrc                             # Obsidian vim keybindings
dot_config/
├── sheldon/       # Zsh plugin manager (sheldon)
├── nvim/          # Neovim (dein.vim plugin manager)
└── ghostty/       # Ghostty terminal
dot_tmuxinator/    # tmuxinator project configs
dot_claude/
├── CLAUDE.md      # Global Claude Code settings
├── commands/      # Custom slash commands
└── skills/        # Skills (creating-skill, frontend-design, github, gmail, google-calendar)
```

## Zsh Plugin Management

Zsh plugins are managed with Sheldon. Config: `dot_config/sheldon/plugins.toml`

```bash
sheldon lock           # Install/update plugins
sheldon lock --update  # Force update all plugins
```

Key plugins:
- **fzf** - Fuzzy finder (`Ctrl+R`, `Ctrl+T`, `Alt+C`)
- **forgit** - Git with fzf (`ga`, `gcb`, `glo`, `gd`)
- **fzf-zsh-plugin** - tmux, kill, etc. (`tm`, `fzf-kill`)
