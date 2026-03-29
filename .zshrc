# Sheldon - Plugin Manager
# Guard against re-sourcing (zsh-defer does not support reload)
# Use PID to allow new subshells to load plugins
if [[ "${_SHELDON_LOADED_PID:-}" != "$$" ]]; then
  eval "$(sheldon source)"
  _SHELDON_LOADED_PID=$$
fi

# Source additional configuration
[ -f $HOME/.zshrc.custom ] && source $HOME/.zshrc.custom
[ -f $HOME/.zshrc.alias ] && source $HOME/.zshrc.alias

# bun completions
[ -s "/Users/shifumin/.bun/_bun" ] && source "/Users/shifumin/.bun/_bun"

# bun
export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"
# The following lines have been added by Docker Desktop to enable Docker CLI completions.
fpath=(/Users/shifumin/.docker/completions $fpath)
autoload -Uz compinit
compinit
# End of Docker CLI completions
