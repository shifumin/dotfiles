# Dotfiles Workflow

Dotfiles are symlinked from `~/ghq/github.com/shifumin/dotfiles/`.

## Editing

**Write/Edit tools refuse symlinks** (`Refusing to write through symlink`), even though Read succeeds through them. Check `ls -l` before editing anything under `~/.claude/`, `~/.zshrc`, or other linked paths, and target the repo path directly:

```
~/.claude/settings.json  ->  ~/ghq/github.com/shifumin/dotfiles/.claude/settings.json
```

## Adding New Files

1. Create the file in `~/ghq/github.com/shifumin/dotfiles/` at the target relative path
2. Register it in `setup.sh` (`dir_links` for directories, `file_links` for single `$HOME`-relative files, `claude_links` for paths under `.claude/`)
3. Run `./setup.sh` to create the symlink
4. Commit both the new file and `setup.sh`

Exception: skills under `.claude/skills/<name>/` are auto-linked individually by `setup.sh` (do not add them to an array; just run `./setup.sh`). Third-party skills are listed in `.claude/skills.txt`.
