# dotfiles

Personal dotfiles managed with symlinks.

## Quick Start

```bash
ghq get shifumin/dotfiles
cd ~/ghq/github.com/shifumin/dotfiles
./setup.sh
```

Or manually:

```bash
git clone https://github.com/shifumin/dotfiles.git
cd dotfiles
./setup.sh
```

## Contents

### Shell

- `.zshrc`, `.zshrc.alias`, `.zshrc.custom` - Zsh configuration
- `.zprofile` - Zsh environment
- `.config/sheldon/` - Zsh plugin manager ([Sheldon](https://sheldon.cli.rs/))
  - `sheldon lock` — Install/update plugins
  - `sheldon lock --update` — Force update all plugins
  - [fzf](https://github.com/junegunn/fzf) - Fuzzy finder
  - [forgit](https://github.com/wfxr/forgit) - Git with fzf
  - [fzf-zsh-plugin](https://github.com/unixorn/fzf-zsh-plugin) - fzf integrations

### Git

- `.gitconfig` - Git configuration
- `.gitignore` - Global gitignore

### Editor

- `.config/nvim/` - Neovim configuration
- `.obsidian.vimrc` - Obsidian vim mode

### Terminal

- `.config/ghostty/` - Ghostty terminal configuration
- `.tmux.conf` - tmux configuration
- `.tmuxinator/` - tmuxinator project configs
- `.tigrc` - tig configuration

### Ruby

- `.pryrc` - Pry console configuration
- `.gemrc` - RubyGems configuration
- `.rspec` - RSpec defaults
- `.default-gems` - Default gems for rbenv

### Claude Code

- `.claude/CLAUDE.md` - Global settings (symlinked to `~/.claude/CLAUDE.md`, applied to all projects)
- `.claude/rules/` - Context-specific rules (coding, git, dotfiles, notion)
- `.claude/commands/` - Custom slash commands
- `.claude/skills/` - Custom skills
- `.claude/skills.txt` - Third-party skill manifest (auto-installed on setup)
- `.claude/settings.json` - Permissions and hooks configuration

> `.claude/CLAUDE.md` serves a dual role: it is a file in this repo AND the user's global Claude Code settings. Changes here affect behavior across all projects.

### Other

- `.default-npm-packages` - Default npm packages

## Directory Structure

```
.config/
├── karabiner/   # Karabiner-Elements key remapping
├── sheldon/     # Zsh plugin manager
├── nvim/        # Neovim (dein.vim)
└── ghostty/     # Ghostty terminal
.claude/
├── CLAUDE.md    # Global Claude Code settings (→ ~/.claude/CLAUDE.md)
├── commands/    # Custom slash commands
├── rules/       # Context-specific rules
├── skills/      # Custom skills
└── skills.txt   # Third-party skill manifest
```

## Workflow

Edit dotfiles directly — symlinks keep the repo and home directory in sync:

```bash
vim ~/.zshrc          # edit via symlink (repo file is updated)
cd ~/ghq/github.com/shifumin/dotfiles
git add .zshrc
git commit -m "update zshrc"
git push
```

Add new dotfiles:

1. Create the file in the repo at the correct relative path
2. Add the path to `setup.sh`
3. Run `./setup.sh`
4. Commit
