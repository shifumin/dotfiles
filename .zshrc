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
