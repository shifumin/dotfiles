# chezmoi Workflow

Dotfiles are managed with chezmoi. Edit target files directly, then sync to source with `chezmoi add`.

## Editing Steps

1. Edit the target file directly (e.g., `~/.zshrc`, `~/.config/nvim/init.vim`)
2. Run `chezmoi add <target_file>` to sync to source directory
3. Commit in source directory (`~/.local/share/chezmoi`)

Example:
```bash
# After editing ~/.zshrc
chezmoi add ~/.zshrc
# → ~/.local/share/chezmoi/dot_zshrc is updated
```

## File Type Handling

| Situation | Action |
|-----------|--------|
| Existing files | Edit target → `chezmoi add` |
| New files | Create at target → `chezmoi add` |
