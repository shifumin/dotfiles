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
| Normal files | Edit target → `chezmoi add` |
| Templates (`.tmpl`) | Edit source (`~/.local/share/chezmoi/`) directly → `chezmoi apply` |
| New files | Create at target → `chezmoi add` |
| After modifying chezmoi-managed files | Always run `chezmoi add <target_file>` |

Template files (currently only `google-calendar/SKILL.md.tmpl`): Do NOT use `chezmoi add` — it writes expanded values and breaks the template. Edit source directly.
