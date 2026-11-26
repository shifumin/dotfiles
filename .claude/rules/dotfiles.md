# Dotfiles Symlinks

Dotfiles under `~/` (e.g. `~/.claude/*`, `~/.zshrc`) are symlinked from `~/ghq/github.com/shifumin/dotfiles/`.

Write/Edit tools refuse symlinks (`Refusing to write through symlink`), even though Read succeeds. Check `ls -l` before editing linked paths and target the repo path directly (e.g. `~/ghq/github.com/shifumin/dotfiles/.claude/settings.json`).
