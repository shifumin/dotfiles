# CLAUDE.md

## Repository Overview

Personal dotfiles managed with symlinks. The repository (`~/ghq/github.com/shifumin/dotfiles/`) is the single source of truth — files here are symlinked to the home directory.

## Workflow

Dotfiles are managed with symlinks. Editing files in the repo directly updates the target (home directory).

```bash
vim ~/.zshrc                  # edit via symlink (repo file is updated)
cd ~/ghq/github.com/shifumin/dotfiles && git commit
```

New machine setup:

```bash
ghq get shifumin/dotfiles
cd ~/ghq/github.com/shifumin/dotfiles
./setup.sh
```

Adding new dotfiles:

1. Create the file in the repo at the correct relative path
2. Add the path to `setup.sh` (in the appropriate array: `dir_links`, `file_links`, or `claude_links`)
3. Run `./setup.sh` to create the symlink
4. Commit both the new file and the updated `setup.sh`

## Key Directories

```
.config/
├── karabiner/   # Karabiner-Elements key remapping
├── sheldon/     # Zsh plugin manager
├── nvim/        # Neovim (dein.vim)
└── ghostty/     # Ghostty terminal
.claude/
├── CLAUDE.md    # Global Claude Code settings
├── commands/    # Custom slash commands
└── skills/      # Skills (planning-implementation, researching-codebase, ...)
```

## Zsh Plugin Management

Zsh plugins are managed with [Sheldon](https://sheldon.cli.rs/). Config: `.config/sheldon/plugins.toml`

```bash
sheldon lock           # Install/update plugins
sheldon lock --update  # Force update all plugins
```

Key plugins:
- **fzf** - Fuzzy finder (`Ctrl+R`, `Ctrl+T`, `Alt+C`)
- **forgit** - Git with fzf (`ga`, `gcb`, `glo`, `gd`)
- **fzf-zsh-plugin** - tmux, kill, etc. (`tm`, `fzf-kill`)
