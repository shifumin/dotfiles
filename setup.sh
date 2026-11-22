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
  ".tmuxinator"
)

# ── ファイル単位のシンボリックリンク ──
file_links=(
  ".codex/AGENTS.md"
  ".config/git/ignore"
  ".config/herdr/config.toml"
  ".default-gems"
  ".default-npm-packages"
  ".gemrc"
  ".gitconfig"
  ".obsidian.vimrc"
  ".pryrc"
  ".rspec"
  ".tigrc"
  ".tmux.conf"
  ".zprofile"
  ".zshrc"
  ".zshrc.alias"
  ".zshrc.custom"
  "Library/LaunchAgents/com.shifumin.herdr.plist"
)

# ── .claude/ 内の個別シンボリックリンク ──
# .claude/にはClaude Codeのランタイムデータ（cache, sessions等）があるため
# ディレクトリ丸ごとではなく管理対象のみ個別にリンクする
claude_links=(
  ".claude/CLAUDE.md"
  ".claude/settings.json"
  ".claude/statusline.py"
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

write_generated_file() {
  local target="$1"
  local content="$2"

  if [[ -f "$target" && ! -L "$target" ]] && [[ "$(cat "$target")" == "$content" ]]; then
    echo "OK:   $target"
    return
  fi

  mkdir -p "$(dirname "$target")"
  local tmp
  tmp="$(mktemp "${target}.XXXXXX")"
  printf '%s\n' "$content" >| "$tmp"
  chmod 644 "$tmp"
  command mv -f "$tmp" "$target"
  echo "GEN:  $target"
}

json_escape() {
  printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

render_t3_skills_json() {
  local paths=()
  if [[ -d "$DOTFILES_DIR/.gemini/skills" ]]; then
    paths+=("$DOTFILES_DIR/.gemini/skills")
  fi
  paths+=("$HOME/.agents/skills")

  printf '{\n  "entries": [\n'
  local i last=$((${#paths[@]} - 1))
  for i in "${!paths[@]}"; do
    local comma=","
    [[ "$i" -eq "$last" ]] && comma=""
    printf '    {\n      "path": "%s"\n    }%s\n' "$(json_escape "${paths[$i]}")" "$comma"
  done
  printf '  ]\n}'
}

# dotfiles 配下を指す壊れたシンボリックリンクだけ安全に削除する
prune_broken_links() {
  local dir="$1"
  [[ -d "$dir" ]] || return 0
  local entry target
  for entry in "$dir"/*; do
    [[ -L "$entry" && ! -e "$entry" ]] || continue
    target="$(readlink "$entry")"
    case "$target" in
      "$DOTFILES_DIR"/*)
        command rm -f "$entry"
        echo "PRUNE: $entry (broken link to $target)"
        ;;
    esac
  done
}

echo "=== dotfiles setup ==="

# ── エージェント用グローバル指示書の生成 ──
# 共有の AGENTS.md と persona 正本 (.claude/output-styles/emma.md) から
# .codex/AGENTS.md と .gemini/config/GEMINI.md を生成してからリンクする（冪等）
"$DOTFILES_DIR/.codex/build-agents.sh"

for item in "${dir_links[@]}" "${file_links[@]}" "${claude_links[@]}"; do
  link_item "$item"
done

# ── .claude/skills/ の自作スキル個別リンク ──
# skills/を丸ごとリンクすると gh skill install が置くサードパーティ実体と共存できないため
# 自作スキル（実ディレクトリ）のみ個別にリンクする
# Codex 等 universal (.agents/skills) 経由でスキルを読むツールにも見えるよう、
# .claude/skills と .agents/skills の両方にリンクする
mkdir -p "$HOME/.claude/skills"
mkdir -p "$HOME/.agents/skills"
for skill_dir in "$DOTFILES_DIR/.claude/skills"/*/; do
  skill_name="$(basename "$skill_dir")"
  # シンボリックリンク（サードパーティスキル）はスキップ
  if [[ -L "${skill_dir%/}" ]]; then
    echo "SKIP (third-party skill): $skill_name"
    continue
  fi
  link_path "$skill_dir" "$HOME/.claude/skills/$skill_name"
  link_path "$skill_dir" "$HOME/.agents/skills/$skill_name"
done

# ── T3 Code (Antigravity) 向け設定 ──
# T3 Code はグローバル設定ルートを ~/.t3/userdata/providers/antigravity/<hash>/ に隔離する一方、
# UI のスキル検出（AntigravitySkills.ts）は ~/.gemini/config/skills.json を参照し、
# 起動時の linkAntigravityUserConfig がそれをプロファイルの config/skills.json へ自動リンクする。
# - config/skills は linkAntigravityUserConfig が ~/.gemini/config/skills に同期（無ければ削除）
#   するため直接リンクしない
# - skills.json は Antigravity の customization.go が "~/" を展開できず絶対パスを要求するため、
#   リポジトリに実パスをコミットせず setup.sh で ~/.gemini/config/skills.json を生成する
t3_skills_json="$(render_t3_skills_json)"
write_generated_file "$HOME/.gemini/config/skills.json" "$t3_skills_json"

t3_ag_configs=()
for d in "$HOME/.t3/userdata/providers/antigravity"/*/config; do
  [[ -d "$d" ]] && t3_ag_configs+=("$d")
done
if [[ ${#t3_ag_configs[@]} -eq 0 ]]; then
  echo "WARN: T3 Code Antigravity config dir not found (~/.t3/userdata/providers/antigravity/*/config); launch T3 Code once and re-run setup.sh"
else
  for t3_config in "${t3_ag_configs[@]}"; do
    link_path "$DOTFILES_DIR/AGENTS.md" "$t3_config/AGENTS.md"
    link_path "$DOTFILES_DIR/.gemini/config/GEMINI.md" "$t3_config/GEMINI.md"
    # 旧 setup.sh が生成した実ファイルが残っていれば消してから ~/.gemini/config/skills.json へリンク
    if [[ -f "$t3_config/skills.json" && ! -L "$t3_config/skills.json" ]]; then
      command rm -f "$t3_config/skills.json"
    fi
    link_path "$HOME/.gemini/config/skills.json" "$t3_config/skills.json"
    # 旧 setup.sh が張った config/skills リンクが残っていれば掃除（skills.json 経由へ移行済み）
    if [[ -L "$t3_config/skills" ]]; then
      target="$(readlink "$t3_config/skills")"
      case "$target" in
        "$DOTFILES_DIR"/*)
          command rm -f "$t3_config/skills"
          echo "PRUNE: $t3_config/skills (migrated to skills.json)"
          ;;
      esac
    fi
  done
fi

# ── 自作スキルの YAML フロントマター検証 ──
# T3 Code (AntigravitySkills.ts) は厳格な YAML パーサでフロントマターを読み、
# クォートなしの ": " や name 欠落があるとスキル一覧から静かに落とすため事前検証する
if command -v ruby &>/dev/null; then
  ruby -ryaml -e '
    errors = 0
    ARGV.each do |root|
      next unless Dir.exist?(root)
      Dir.glob(File.join(root, "*", "SKILL.md")).sort.each do |p|
        dir = File.basename(File.dirname(p))
        txt = File.read(p, encoding: "UTF-8")
        s = txt.index("---")
        e = s ? txt.index("---", s + 3) : nil
        if !s || !e
          warn "SKILL FRONTMATTER ERROR: #{p}: missing frontmatter"
          errors += 1
          next
        end
        begin
          doc = YAML.safe_load(txt[(s + 3)...e].strip)
          name = doc.is_a?(Hash) ? doc["name"] : nil
          desc = doc.is_a?(Hash) ? doc["description"] : nil
          if !name.is_a?(String) || name.strip.empty? || name != dir
            warn "SKILL FRONTMATTER ERROR: #{p}: name (#{name.inspect}) must match dir (#{dir})"
            errors += 1
          end
          if !desc.is_a?(String) || desc.strip.empty?
            warn "SKILL FRONTMATTER ERROR: #{p}: missing description"
            errors += 1
          end
        rescue => ex
          warn "SKILL FRONTMATTER ERROR: #{p}: #{ex.message.lines.first.strip}"
          errors += 1
        end
      end
    end
    exit(errors == 0 ? 0 : 1)
  ' "$DOTFILES_DIR/.claude/skills" "$DOTFILES_DIR/.gemini/skills"
fi

# ── サードパーティスキルのインストール ──
# .claude/skills.txt に定義されたスキルを gh skill install でインストール
# claude-code（~/.claude/skills）と universal（~/.agents/skills）の両方に実体を配置し、
# 更新は gh skill update が両配置をまとめて扱う
# スキップ条件（冪等）:
#   - ピン無しエントリ: 両配置先に SKILL.md が存在すればスキップ
#   - ピン付きエントリ(@タグ/SHA): 加えて導入済み ref がピンと一致すればスキップ
# 存在だけで判定すると skills.txt のピンを更新しても再インストールされず、
# 手元が古いまま取り残されるため、ピン付きは ref まで突き合わせる
skills_file="$DOTFILES_DIR/.claude/skills.txt"
if [[ -f "$skills_file" ]]; then
  if command -v gh &>/dev/null && gh skill --help &>/dev/null; then
    # 導入済みスキルの ref を一度だけ取得（"<install path>\t<version>" の行）
    # 取得できなかった場合、ピン付きは ref 不一致とみなして再インストールされる
    # （毎回 INSTALL 行が出るので気付ける。黙って古いまま残るより安全）
    installed_refs="$(gh skill list --scope user --json path,version --jq '.[] | "\(.path)\t\(.version)"' 2>/dev/null)"

    while IFS= read -r line || [[ -n "$line" ]]; do
      line="${line%%#*}"
      line="$(echo "$line" | xargs)"
      [[ -z "$line" ]] && continue

      source_repo="${line%% *}"
      skill_ref="${line##* }"
      # skill_ref は名前 / リポジトリ内パス(…/SKILL.md) / @タグ・SHA付き のいずれにも対応
      skill_base="${skill_ref%@*}"
      skill_base="${skill_base%/SKILL.md}"
      skill_name="$(basename "$skill_base")"

      want_ref=""
      [[ "$skill_ref" == *@* ]] && want_ref="${skill_ref##*@}"

      install_reason=""
      if [[ ! -e "$HOME/.claude/skills/$skill_name/SKILL.md" || ! -e "$HOME/.agents/skills/$skill_name/SKILL.md" ]]; then
        install_reason="not installed"
      elif [[ -n "$want_ref" ]]; then
        for install_path in "$HOME/.claude/skills/$skill_name" "$HOME/.agents/skills/$skill_name"; do
          have_ref="$(printf '%s\n' "$installed_refs" | awk -F'\t' -v p="$install_path" '$1 == p { print $2; exit }')"
          if [[ "$have_ref" != "$want_ref" ]]; then
            install_reason="ref ${have_ref:-unknown} -> $want_ref"
            break
          fi
        done
      fi

      if [[ -z "$install_reason" ]]; then
        echo "SKIP (already installed): $skill_name"
      else
        echo "INSTALL: $skill_name from $source_repo ($install_reason)"
        gh skill install "$source_repo" "$skill_ref" --agent claude-code --scope user --force
        gh skill install "$source_repo" "$skill_ref" --agent universal --scope user --force
      fi
    done < "$skills_file"
  else
    echo "WARN: gh skill not available (requires GitHub CLI >= 2.90.0), skipping third-party skill installation"
  fi
fi

# ── herdr スキルをインストール済みバイナリ同梱版に同期 ──
# herdr 更新後に setup.sh を流せば SKILL.md が追従する（差分が出たら commit する）
"$DOTFILES_DIR/.claude/sync-herdr-skill.sh" || echo "WARN: herdr skill sync failed"

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

# ── 削除・移行済みリンクの自動掃除 ──
# 旧 ~/.gitignore symlink（.config/git/ignore へ分離済み）
if [[ -L "$HOME/.gitignore" && "$(readlink "$HOME/.gitignore")" == "$DOTFILES_DIR/.gitignore" ]]; then
  command rm -f "$HOME/.gitignore"
  echo "PRUNE: $HOME/.gitignore (migrated to ~/.config/git/ignore)"
fi
# 旧 ~/.gemini/ 配下の dotfiles 管理リンク（T3 Code の Antigravity config へ移行済み）
# 注: ~/.gemini/config/skills.json は T3 Code のスキル検出先として生成するため対象外
for entry in \
  "$HOME/.gemini/config/AGENTS.md" \
  "$HOME/.gemini/config/GEMINI.md" \
  "$HOME/.gemini/config/skills"/* \
  "$HOME/.gemini/skills"/*; do
  [[ -L "$entry" ]] || continue
  target="$(readlink "$entry")"
  case "$target" in
    "$DOTFILES_DIR"/*)
      command rm -f "$entry"
      echo "PRUNE: $entry (migrated to T3 Code Antigravity config)"
      ;;
  esac
done
for empty_dir in \
  "$HOME/.gemini/config/skills" \
  "$HOME/.gemini/config" \
  "$HOME/.gemini/skills"; do
  rmdir "$empty_dir" 2>/dev/null || true
done
for prune_dir in \
  "$HOME/.claude" \
  "$HOME/.claude/skills" \
  "$HOME/.agents/skills"; do
  prune_broken_links "$prune_dir"
done

# ── 権限設定 ──
karabiner_json="$DOTFILES_DIR/.config/karabiner/karabiner.json"
if [[ -f "$karabiner_json" ]]; then
  chmod 600 "$karabiner_json"
fi
echo ""
echo "=== done ==="
