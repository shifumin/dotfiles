# Dotfiles Workflow

Dotfiles are managed with symlinks from `~/ghq/github.com/shifumin/dotfiles/`.

## Editing

Files in the repo are symlinked to the home directory. Editing either the symlink target or the repo file modifies the same file.

```bash
vim ~/.zshrc          # edit directly (symlinked to repo)
cd ~/ghq/github.com/shifumin/dotfiles && git commit
```

## Adding New Files

1. Create the file in the repo at the correct relative path
2. Add the path to `setup.sh` (`dir_links` = directories, `file_links` = single files linked at the same path relative to `$HOME`, `claude_links` = anything under `.claude/`)
3. Run `./setup.sh` to create the symlink
4. Commit both the new file and the updated `setup.sh`

Exception: skills under `.claude/skills/<name>/` are auto-linked individually by `setup.sh` — do not add them to any array; just create the directory and run `./setup.sh`. Third-party skills are managed via `.claude/skills.txt`, not the arrays.
