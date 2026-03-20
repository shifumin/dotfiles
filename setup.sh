#!/bin/bash
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── ディレクトリ単位のシンボリックリンク ──
# 内容が全てdotfiles管理のディレクトリ
dir_links=(
  ".config/nvim"
  ".config/ghostty"
  ".config/sheldon"
  ".config/karabiner"
  ".tmuxinator"
)

# ── ファイル単位のシンボリックリンク ──
file_links=(
  ".zshrc"
  ".zprofile"
  ".zshrc.alias"
  ".zshrc.custom"
  ".gitconfig"
  ".gitignore"
  ".gemrc"
  ".pryrc"
  ".rspec"
  ".default-gems"
  ".default-npm-packages"
  ".obsidian.vimrc"
  ".tmux.conf"
  ".tigrc"
)

# ── .claude/ 内の個別シンボリックリンク ──
# .claude/にはClaude Codeのランタイムデータ（cache, sessions等）があるため
# ディレクトリ丸ごとではなく管理対象のみ個別にリンクする
claude_links=(
  ".claude/CLAUDE.md"
  ".claude/settings.json"
  ".claude/statusline.py"
  ".claude/commands"
  ".claude/rules"
  ".claude/skills"
)

link_item() {
  local item="$1"
  local target="$HOME/$item"
  local source="$DOTFILES_DIR/$item"

  if [[ ! -e "$source" ]]; then
    echo "SKIP (source not found): $source"
    return
  fi

  # 既存の実ファイル/ディレクトリをバックアップ
  if [[ -e "$target" && ! -L "$target" ]]; then
    mv "$target" "$target.bak"
    echo "BACKUP: $target -> $target.bak"
  fi

  mkdir -p "$(dirname "$target")"
  ln -sfn "$source" "$target"
  echo "LINK: $target -> $source"
}

echo "=== dotfiles setup ==="

for item in "${dir_links[@]}" "${file_links[@]}" "${claude_links[@]}"; do
  link_item "$item"
done

# ── 権限設定 ──
chmod 600 "$DOTFILES_DIR/.config/karabiner/karabiner.json"
echo ""
echo "=== done ==="
