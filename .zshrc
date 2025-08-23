# Check if zplug is installed
if [[ ! -d ~/.zplug ]]; then
  git clone https://github.com/zplug/zplug ~/.zplug
  source ~/.zplug/init.zsh && zplug update --self
fi

# Essential
source ~/.zplug/init.zsh

# Load theme file
zplug 'dracula/zsh', as:theme

# Additional completion definitions for Zsh.
zplug 'zsh-users/zsh-completions'

# Fish-like autosuggestions for zsh
zplug 'zsh-users/zsh-autosuggestions'

# Fish shell like syntax highlighting for Zsh.
zplug 'zsh-users/zsh-syntax-highlighting', defer:2

# ZSH port of the FISH shell's history search 🐠
zplug 'zsh-users/zsh-history-substring-search', defer:3

# ZSH Completion script for curl
zplug 'Valodim/zsh-curl-completion'

# fzf-tmux の peco バージョン
zplug 'b4b4r07/dotfiles', as:command, use:bin/peco-tmux

# peco/percol/fzf wrapper plugin for zsh
zplug 'mollifier/anyframe'

# 🚀 A next-generation cd command with an interactive filter
zplug "babarot/enhancd", use:init.sh

# zsh plugin to cd to git repository root directory.
zplug 'mollifier/cd-gitroot'

# Install plugins if there are plugins that have not been installed
if ! zplug check; then
    printf "Install? [y/N]: "
    if read -q; then
        echo; zplug install
    fi
fi

# Then, source plugins and add commands to $PATH
zplug load --verbose

[ -f $HOME/dotfiles/.zshrc.custom ] && source $HOME/dotfiles/.zshrc.custom
[ -f $HOME/dotfiles/.zshrc.alias ] && source $HOME/dotfiles/.zshrc.alias
