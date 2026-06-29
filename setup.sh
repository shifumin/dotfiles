#!/bin/bash
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── mise shims を PATH に追加（npx 等の検出のため） ──
# .zshrc.custom と同じパスを参照（新規シェルセッション前でも npx を見つけられる）
if [[ -d "$HOME/.local/share/mise/shims" ]]; then
  export PATH="$HOME/.local/share/mise/shims:$PATH"
fi

# ── ディレクトリ単位のシンボリックリンク ──
# 内容が全てdotfiles管理のディレクトリ
dir_links=(
  ".config/nvim"
  ".config/ghostty"
  ".config/sheldon"
  ".config/karabiner"
  ".config/cmux"
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
  ".claude/hooks"
  ".claude/rules"
  ".claude/output-styles"
)

link_path() {
  local source="${1%/}"
  local target="$2"

  if [[ ! -e "$source" ]]; then
    echo "SKIP (source not found): $source"
    return
  fi

  # 既に正しいシンボリックリンクならスキップ
  if [[ -L "$target" && "$(readlink "$target")" == "$source" ]]; then
    echo "OK:   $target"
    return
  fi

  # 既存の実ファイル/ディレクトリをバックアップ（既存 .bak はタイムスタンプで退避）
  if [[ -e "$target" && ! -L "$target" ]]; then
    local backup="$target.bak"
    if [[ -e "$backup" ]]; then
      backup="$target.bak.$(date +%Y%m%d-%H%M%S)"
    fi
    mv "$target" "$backup"
    echo "BACKUP: $target -> $backup"
  fi

  mkdir -p "$(dirname "$target")"
  ln -sfn "$source" "$target"
  echo "LINK: $target -> $source"
}

link_item() {
  local item="$1"
  link_path "$DOTFILES_DIR/$item" "$HOME/$item"
}

echo "=== dotfiles setup ==="

for item in "${dir_links[@]}" "${file_links[@]}" "${claude_links[@]}"; do
  link_item "$item"
done

# ── .claude/skills/ の自作スキル個別リンク ──
# skills/を丸ごとリンクすると npx skills add の相対シンボリックリンクが壊れるため
# 自作スキル（実ディレクトリ）のみ個別にリンクする
mkdir -p "$HOME/.claude/skills"
for skill_dir in "$DOTFILES_DIR/.claude/skills"/*/; do
  skill_name="$(basename "$skill_dir")"
  # シンボリックリンク（サードパーティスキル）はスキップ
  if [[ -L "${skill_dir%/}" ]]; then
    echo "SKIP (third-party skill): $skill_name"
    continue
  fi
  link_path "$skill_dir" "$HOME/.claude/skills/$skill_name"
done

# ── サードパーティスキルのインストール ──
# .claude/skills.txt に定義されたスキルを npx skills add でインストール
# ~/.claude/skills/<name>/SKILL.md が存在すればスキップ（冪等）
skills_file="$DOTFILES_DIR/.claude/skills.txt"
if [[ -f "$skills_file" ]]; then
  if command -v npx &>/dev/null; then
    while IFS= read -r line || [[ -n "$line" ]]; do
      line="${line%%#*}"
      line="$(echo "$line" | xargs)"
      [[ -z "$line" ]] && continue

      source_repo="${line%% *}"
      skill_name="${line##* }"

      if [[ -e "$HOME/.claude/skills/$skill_name/SKILL.md" ]]; then
        echo "SKIP (already installed): $skill_name"
      else
        echo "INSTALL: $skill_name from $source_repo"
        npx skills add "$source_repo" --skill "$skill_name" -g -a claude-code -y
      fi
    done < "$skills_file"
  else
    echo "WARN: npx not found, skipping third-party skill installation"
  fi
fi

# ── Cursor エディタのシンボリックリンク ──
# Cursor設定は ~/Library/Application Support/ にあるため
# 標準のlink_itemパターンに合わないので個別にリンク
cursor_source="$DOTFILES_DIR/Cursor"
cursor_target="$HOME/Library/Application Support/Cursor/User"
if [[ -d "$cursor_source" ]]; then
  mkdir -p "$cursor_target"
  for f in "$cursor_source"/*; do
    link_path "$f" "$cursor_target/$(basename "$f")"
  done
fi

# ── 権限設定 ──
karabiner_json="$DOTFILES_DIR/.config/karabiner/karabiner.json"
if [[ -f "$karabiner_json" ]]; then
  chmod 600 "$karabiner_json"
fi
echo ""
echo "=== done ==="
