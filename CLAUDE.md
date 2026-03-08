# CLAUDE.md

## Repository Overview

Personal dotfiles managed with [chezmoi](https://www.chezmoi.io/).

This is the chezmoi **source directory** (`~/.local/share/chezmoi/`). Files here are NOT the actual dotfiles — chezmoi transforms and deploys them to the home directory (target). Editing source files directly does not update the target until `chezmoi apply` is run.

Chezmoi uses naming prefixes (`dot_`, `private_`, `executable_`, `empty_`) to control target file names and permissions.

## Workflow

Edit target files directly, then sync to source:

```bash
vim ~/.zshrc                  # edit target directly
chezmoi add ~/.zshrc          # sync to source (dot_zshrc)
cd ~/.local/share/chezmoi && git commit
```

Verify changes: `chezmoi diff` shows pending differences between source and target.

## Key Directories

```
dot_config/
├── private_karabiner/  # Karabiner-Elements key remapping
├── sheldon/            # Zsh plugin manager
├── nvim/               # Neovim (dein.vim)
└── ghostty/            # Ghostty terminal
dot_claude/
├── CLAUDE.md           # Global Claude Code settings
├── commands/           # Custom slash commands
└── skills/             # Skills (planning-implementation, researching-codebase, ...)
```

## Zsh Plugin Management

Zsh plugins are managed with [Sheldon](https://sheldon.cli.rs/). Config: `dot_config/sheldon/plugins.toml`

```bash
sheldon lock           # Install/update plugins
sheldon lock --update  # Force update all plugins
```

Key plugins:
- **fzf** - Fuzzy finder (`Ctrl+R`, `Ctrl+T`, `Alt+C`)
- **forgit** - Git with fzf (`ga`, `gcb`, `glo`, `gd`)
- **fzf-zsh-plugin** - tmux, kill, etc. (`tm`, `fzf-kill`)
