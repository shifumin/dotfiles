#!/bin/bash
# Validate SKILL.md YAML frontmatter strictly (T3 Code's AntigravitySkills.ts
# drops skills silently on YAML errors, unquoted ": ", or missing/mismatched name).
#
# Usage:
#   scripts/validate-skill-frontmatter.sh [DIR_OR_SKILL_MD ...]
#   (defaults to <dotfiles>/.claude/skills and <dotfiles>/.gemini/skills)
set -euo pipefail

DOTFILES_DIR="$(cd "$(dirname "$0")/.." && pwd)"

if ! command -v ruby &>/dev/null; then
  echo "SKILL FRONTMATTER ERROR: ruby command not found" >&2
  exit 1
fi

targets=("$@")
if [[ ${#targets[@]} -eq 0 ]]; then
  targets=("$DOTFILES_DIR/.claude/skills" "$DOTFILES_DIR/.gemini/skills")
fi

ruby -ryaml -e '
  errors = 0
  files = []
  ARGV.each do |arg|
    if File.file?(arg)
      files << arg
    elsif File.directory?(arg)
      direct = File.join(arg, "SKILL.md")
      if File.file?(direct)
        files << direct
      else
        files.concat(Dir.glob(File.join(arg, "*", "SKILL.md")).sort)
      end
    end
  end
  files.uniq.each do |p|
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
  exit(errors == 0 ? 0 : 1)
' "${targets[@]}"
