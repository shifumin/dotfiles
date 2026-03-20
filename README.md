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

### Other

- `.default-npm-packages` - Default npm packages
- `.claude/` - Claude Code settings, custom commands, and skills

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
