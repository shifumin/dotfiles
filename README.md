# dotfiles

Personal dotfiles managed with [chezmoi](https://www.chezmoi.io/).

## Quick Start

Install chezmoi and apply dotfiles in one command:

```bash
sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply shifumin
```

Or step by step:

```bash
brew install chezmoi
chezmoi init https://github.com/shifumin/dotfiles.git
chezmoi diff    # Preview changes
chezmoi apply   # Apply dotfiles
```

## Contents

### Shell

- `.zshrc`, `.zshrc.alias`, `.zshrc.custom` - Zsh configuration
- `.zprofile`, `.zshenv` - Zsh environment

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

### Other

- `.default-npm-packages` - Default npm packages
- `.ctags` - ctags configuration
- `.claude/` - Claude Code settings and custom commands

## Workflow

Edit dotfiles:

```bash
chezmoi edit ~/.zshrc
chezmoi diff
chezmoi apply
```

Commit and push:

```bash
chezmoi cd
git add .
git commit -m "update zshrc"
git push
```

Pull latest changes:

```bash
chezmoi update
```

## Common Commands

| Command | Description |
|---------|-------------|
| `chezmoi add <file>` | Add a file to chezmoi |
| `chezmoi edit <file>` | Edit source file |
| `chezmoi diff` | Show pending changes |
| `chezmoi apply` | Apply changes to home |
| `chezmoi update` | Pull and apply from remote |
| `chezmoi cd` | Go to source directory |
