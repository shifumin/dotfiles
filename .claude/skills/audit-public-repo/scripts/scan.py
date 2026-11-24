#!/usr/bin/env python3
"""Public repository privacy, business-info, and secret scanner.

Scans working tree (tracked + non-ignored untracked files) and Git history
(commits, diffs, messages, author/committer metadata, deleted sensitive paths,
branches, and tags) without external Python dependencies.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import math
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_DENYLIST = Path.home() / ".config" / "push-denylist.txt"
DEFAULT_ALLOWLIST = Path.home() / ".config" / "public-audit-allowlist.txt"

# Lockfiles / minified bundles where generic high-entropy checks produce noise.
ENTROPY_SKIP_BASENAMES = {
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "Gemfile.lock",
    "Cargo.lock",
    "poetry.lock",
    "composer.lock",
    "Podfile.lock",
    "go.sum",
    "flake.lock",
}
ENTROPY_SKIP_SUFFIXES = (".min.js", ".min.css", ".map", ".svg", ".woff", ".woff2")

# Clearly sensitive filenames (excluding safe template suffixes).
SAFE_ENV_SUFFIXES = (".example", ".sample", ".template", ".dist", ".schema")
SENSITIVE_FILENAMES = {
    ".env",
    ".netrc",
    ".pypirc",
    "id_rsa",
    "id_dsa",
    "id_ecdsa",
    "id_ed25519",
    "credentials.json",
    "token.json",
    "secrets.yml",
    "secrets.yaml",
    "secrets.json",
    "master.key",
    "cookies.txt",
}
SENSITIVE_EXTENSIONS = {".pem", ".key", ".p12", ".pfx", ".jks", ".keystore", ".kdbx", ".ovpn"}
SUSPICIOUS_HISTORY_EXTENSIONS = {".sqlite", ".sqlite3", ".dump", ".bak", ".orig"}
JUNK_FILENAMES = {".DS_Store", "Thumbs.db"}

# Regex patterns (split literal markers where needed to avoid self-matching).
PRIVATE_KEY_RE = re.compile(
    r"-----BEGIN "
    r"(?:RSA |DSA |EC |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY-----"
)

TOKEN_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("GitHub token", re.compile(r"\b(?:gh" r"[pousr]_[A-Za-z0-9]{20,}|github_" r"pat_[A-Za-z0-9_]{22,})\b")),
    ("AWS access key ID", re.compile(r"\b(?:A3T[A-Z0-9]|AKIA|ASIA|AGPA|AIDA|AROA|AIPA|ANPA|ANVA)[A-Z0-9]{16}\b")),
    ("Slack token", re.compile(r"\bxox" r"[abprs]-[A-Za-z0-9-]{10,}\b")),
    (
        "Slack webhook URL",
        re.compile(r"https://hooks\.slack\.com/services/T[A-Z0-9]{6,}/B[A-Z0-9]{6,}/[A-Za-z0-9]{16,}"),
    ),
    ("Anthropic API key", re.compile(r"\bsk-" r"ant-[A-Za-z0-9_-]{20,}\b")),
    ("OpenAI / generic sk- key", re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{24,}\b")),
    ("xAI API key", re.compile(r"\bxai-[A-Za-z0-9]{20,}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Stripe live key", re.compile(r"\b(?:sk|rk)_live_[0-9A-Za-z]{24,}\b")),
    ("npm token", re.compile(r"\bnpm_[A-Za-z0-9]{36}\b")),
    ("PyPI token", re.compile(r"\bpypi-[A-Za-z0-9_-]{40,}\b")),
    ("CircleCI PAT", re.compile(r"\bCCIPAT_[A-Za-z0-9_-]{16,}\b")),
    ("SendGrid API key", re.compile(r"\bSG\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b")),
    ("Discord webhook URL", re.compile(r"https://discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]{20,}")),
    ("JWT token", re.compile(r"\beyJ[A-Za-z0-9_-]{12,}\.eyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\b")),
]

AUTH_URL_RE = re.compile(r"https?://([^\s:/@\"'`<>]{2,}):([^\s/@\"'`<>]{6,})@([A-Za-z0-9._-]+)")
GENERIC_SECRET_ASSIGN_RE = re.compile(
    r"(?i)\b(?:api[_-]?key|api[_-]?secret|access[_-]?token|auth[_-]?token|secret[_-]?key|client[_-]?secret|private[_-]?key|password|passwd|db_pass(?:word)?)\b"
    r"\s*[:=]\s*[\"']([^\"'\s]{12,})[\"']"
)

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
SAFE_EMAIL_DOMAINS = {
    "users.noreply.github.com",
    "example.com",
    "example.org",
    "example.net",
    "localhost",
    "invalid",
    "test",
    "anthropic.com",
}
SAFE_EMAIL_LOCAL_PREFIXES = ("noreply", "no-reply", "donotreply", "do-not-reply", "bot", "dependabot", "renovate")

PRIVATE_IP_RE = re.compile(
    r"\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b"
)
INTERNAL_URL_RE = re.compile(
    r"https?://(?:[A-Za-z0-9-]+\.)*(?:internal|corp|intranet|localdomain)(?::\d+)?(?:/[^\s\"'`<>]*)?|"
    r"https?://[A-Za-z0-9-]+\.slack\.com/archives/[A-Z0-9]+|"
    r"https?://[A-Za-z0-9-]+\.atlassian\.net/(?:browse|wiki)/[^\s\"'`<>]+",
    re.IGNORECASE,
)

# Local absolute paths containing a username segment.
LOCAL_PATH_RE = re.compile(
    r"(?:/Users/([A-Za-z0-9._-]+)(?=/|\b)|/home/([A-Za-z0-9._-]+)(?=/|\b)|[A-Za-z]:\\Users\\([A-Za-z0-9._-]+)(?=\\|\b))"
)
GENERIC_USERNAMES = {
    "user",
    "username",
    "yourname",
    "your-name",
    "your_name",
    "alice",
    "bob",
    "example",
    "foo",
    "bar",
    "admin",
    "runner",
    "ubuntu",
    "vscode",
    "node",
    "app",
    "me",
    "name",
    "test",
    "Shared",
}

PLACEHOLDER_WORDS = (
    "example",
    "sample",
    "dummy",
    "placeholder",
    "changeme",
    "your_",
    "your-",
    "replace",
    "xxxxxx",
    "******",
    "test_",
    "fake_",
    "mock_",
    "redacted",
    "todo",
)

JP_PHONE_RE = re.compile(r"(?<!\d)0(?:70|80|90)-\d{4}-\d{4}(?!\d)")
HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")

SEVERITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


@dataclass(frozen=True)
class Finding:
    severity: str
    category: str
    scope: str  # "worktree" | "history" | "metadata" | "ref"
    location: str
    masked_value: str
    detail: str
    commit: str = ""


class Allowlist:
    def __init__(self, literals: list[str], regexes: list[re.Pattern[str]], path_globs: list[str]) -> None:
        self.literals = [s.lower() for s in literals]
        self.regexes = regexes
        self.path_globs = path_globs

    @classmethod
    def load(cls, path: Path) -> "Allowlist":
        literals: list[str] = []
        regexes: list[re.Pattern[str]] = []
        path_globs: list[str] = []
        if not path.is_file():
            return cls(literals, regexes, path_globs)
        for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("re:"):
                try:
                    regexes.append(re.compile(line[3:].strip()))
                except re.error:
                    pass
            elif line.startswith("path:"):
                path_globs.append(line[5:].strip())
            else:
                literals.append(line)
        return cls(literals, regexes, path_globs)

    def matches_path(self, rel_path: str) -> bool:
        return any(fnmatch.fnmatch(rel_path, g) for g in self.path_globs)

    def matches_value(self, value: str, line_text: str = "") -> bool:
        v_low = value.lower()
        l_low = line_text.lower()
        for lit in self.literals:
            if lit in v_low or (line_text and lit in l_low):
                return True
        for rx in self.regexes:
            if rx.search(value) or (line_text and rx.search(line_text)):
                return True
        return False


def run_git(repo: Path, args: list[str], check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=check,
    )


def mask_value(value: str) -> str:
    s = value.strip()
    if not s:
        return "****"
    if "@" in s and not s.startswith("http") and " " not in s:
        local, _, domain = s.partition("@")
        m_local = (local[:2] + "****") if len(local) > 2 else "****"
        parts = domain.split(".")
        if len(parts) >= 2:
            m_dom = (parts[0][:2] + "****." + parts[-1]) if len(parts[0]) > 2 else ("****." + parts[-1])
        else:
            m_dom = "****"
        return f"{m_local}@{m_dom}"
    n = len(s)
    if n <= 4:
        return "****"
    if n <= 10:
        return f"{s[:2]}****{s[-1:]}"
    return f"{s[:4]}****{s[-4:]}"


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    length = len(s)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def is_placeholder(value: str) -> bool:
    low = value.lower()
    if any(w in low for w in PLACEHOLDER_WORDS):
        return True
    if value.startswith(("$", "${", "<", "{{", "%")):
        return True
    if len(set(low)) <= 3:
        return True
    return False


def is_safe_email(email: str) -> bool:
    low = email.lower()
    local, _, domain = low.partition("@")
    if domain in SAFE_EMAIL_DOMAINS or domain.endswith(".noreply.github.com"):
        return True
    if any(local == p or local.startswith(p + "+") or local.startswith(p + "-") or local.endswith("[bot]") for p in SAFE_EMAIL_LOCAL_PREFIXES):
        return True
    if is_placeholder(local):
        return True
    return False


def is_binary_bytes(sample: bytes) -> bool:
    return b"\x00" in sample


def should_skip_entropy(path: str) -> bool:
    name = os.path.basename(path)
    return name in ENTROPY_SKIP_BASENAMES or name.endswith(ENTROPY_SKIP_SUFFIXES)


def extract_public_handles(repo: Path) -> set[str]:
    handles: set[str] = set()
    res = run_git(repo, ["remote", "-v"])
    for line in res.stdout.splitlines():
        m = re.search(r"github\.com[:/]([A-Za-z0-9._-]+)/[A-Za-z0-9._-]+", line)
        if m:
            handles.add(m.group(1).lower())
    return handles


def get_visibility(repo: Path) -> tuple[str, str]:
    try:
        res = subprocess.run(
            ["gh", "repo", "view", "--json", "visibility,nameWithOwner"],
            cwd=str(repo),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        if res.returncode == 0:
            data = json.loads(res.stdout)
            return data.get("visibility", "UNKNOWN"), data.get("nameWithOwner", "")
    except (FileNotFoundError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass
    return "UNKNOWN", ""


def load_denylist(path: Path) -> tuple[list[str], bool]:
    if not path.is_file():
        return [], False
    terms: list[str] = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        terms.append(line)
    return terms, True


def check_filename(rel_path: str, scope: str, commit: str = "") -> list[Finding]:
    findings: list[Finding] = []
    base = os.path.basename(rel_path)
    low = base.lower()
    _, ext = os.path.splitext(low)

    if low == ".env" or (low.startswith(".env.") and not low.endswith(SAFE_ENV_SUFFIXES)):
        findings.append(
            Finding("Critical", "Sensitive file", scope, rel_path, base, "Environment file may contain secrets", commit)
        )
    elif low in SENSITIVE_FILENAMES or ext in SENSITIVE_EXTENSIONS or (
        low.startswith("service-account") and low.endswith(".json")
    ):
        findings.append(
            Finding("Critical", "Sensitive file", scope, rel_path, base, "Key/credential filename detected", commit)
        )
    elif base in JUNK_FILENAMES:
        findings.append(
            Finding("Low", "OS junk file", scope, rel_path, base, "OS metadata file committed/untracked", commit)
        )
    elif scope == "history" and ext in SUSPICIOUS_HISTORY_EXTENSIONS:
        findings.append(
            Finding("Medium", "Suspicious history file", scope, rel_path, base, "Backup/DB file existed in history", commit)
        )
    return findings


def scan_text_line(
    line: str,
    location: str,
    rel_path: str,
    scope: str,
    denylist: list[str],
    allowlist: Allowlist,
    public_handles: set[str],
    commit: str = "",
) -> list[Finding]:
    findings: list[Finding] = []
    if allowlist.matches_path(rel_path):
        return findings

    # 1. Private key header
    m = PRIVATE_KEY_RE.search(line)
    if m and not allowlist.matches_value(m.group(0), line):
        findings.append(Finding("Critical", "Private key", scope, location, mask_value(m.group(0)), "Private key header", commit))

    # 2. Known token patterns
    for label, rx in TOKEN_PATTERNS:
        for m in rx.finditer(line):
            val = m.group(0)
            if is_placeholder(val) or allowlist.matches_value(val, line):
                continue
            findings.append(Finding("Critical", label, scope, location, mask_value(val), f"Matched {label} pattern", commit))

    # 3. URL with embedded credentials
    for m in AUTH_URL_RE.finditer(line):
        user, pwd, host = m.group(1), m.group(2), m.group(3)
        if is_placeholder(user) or is_placeholder(pwd) or host in ("example.com", "localhost", "127.0.0.1"):
            continue
        full = m.group(0)
        if allowlist.matches_value(full, line):
            continue
        findings.append(
            Finding("Critical", "Credential in URL", scope, location, f"https://{mask_value(user)}:{mask_value(pwd)}@{host}", "Embedded password in URL", commit)
        )

    # 4. Generic secret assignment (skip lockfiles/minified)
    if not should_skip_entropy(rel_path):
        for m in GENERIC_SECRET_ASSIGN_RE.finditer(line):
            val = m.group(1)
            if is_placeholder(val) or allowlist.matches_value(val, line):
                continue
            ent = shannon_entropy(val)
            if ent >= 3.6:
                findings.append(
                    Finding("Critical", "High-entropy secret assignment", scope, location, mask_value(val), f"entropy={ent:.2f}", commit)
                )
            elif ent >= 2.8:
                findings.append(
                    Finding("Medium", "Potential secret assignment", scope, location, mask_value(val), f"entropy={ent:.2f}", commit)
                )

    # 5. Denylist (case-insensitive substring match)
    if denylist:
        line_low = line.lower()
        for term in denylist:
            if term.lower() in line_low and not allowlist.matches_value(term, line):
                findings.append(
                    Finding("High", "Denylist match", scope, location, mask_value(term), "Matched ~/.config/push-denylist.txt", commit)
                )

    # 6. Emails
    for m in EMAIL_RE.finditer(line):
        email = m.group(0)
        if is_safe_email(email) or allowlist.matches_value(email, line):
            continue
        findings.append(Finding("High", "Email address", scope, location, mask_value(email), "Non-noreply email address", commit))

    # 7. Japanese mobile phone number
    for m in JP_PHONE_RE.finditer(line):
        val = m.group(0)
        if allowlist.matches_value(val, line):
            continue
        findings.append(Finding("High", "Phone number", scope, location, mask_value(val), "Japanese mobile number pattern", commit))

    # 8. Internal URLs & Private IPs
    for m in INTERNAL_URL_RE.finditer(line):
        val = m.group(0)
        if allowlist.matches_value(val, line):
            continue
        findings.append(Finding("Medium", "Internal URL", scope, location, mask_value(val), "Internal/workspace URL pattern", commit))

    for m in PRIVATE_IP_RE.finditer(line):
        ip = m.group(0)
        if ip in ("192.168.0.1", "192.168.1.1", "10.0.0.1") or allowlist.matches_value(ip, line):
            continue
        findings.append(Finding("Medium", "Private IP", scope, location, ip, "Private network IPv4 address", commit))

    # 9. Local absolute paths (/Users/<name>, /home/<name>, C:\Users\<name>)
    for m in LOCAL_PATH_RE.finditer(line):
        uname = m.group(1) or m.group(2) or m.group(3) or ""
        if not uname or uname.lower() in GENERIC_USERNAMES or uname.startswith(("$", "<")):
            continue
        if allowlist.matches_value(m.group(0), line):
            continue
        if uname.lower() in public_handles:
            findings.append(
                Finding("Low", "Local path (public handle)", scope, location, f"/Users/{uname}/...", "Matches repo owner handle", commit)
            )
        else:
            findings.append(
                Finding("High", "Local path (non-public username)", scope, location, f"/Users/{mask_value(uname)}/...", "Username differs from repo owner handle", commit)
            )

    return findings


def list_worktree_files(repo: Path, mode: str) -> list[str]:
    if mode == "full":
        tracked = run_git(repo, ["ls-files", "-z"]).stdout.split("\0")
        untracked = run_git(repo, ["ls-files", "--others", "--exclude-standard", "-z"]).stdout.split("\0")
        return sorted({p for p in tracked + untracked if p})
    if mode in ("diff", "unpushed"):
        changed = run_git(repo, ["diff", "--name-only", "-z"]).stdout.split("\0")
        staged = run_git(repo, ["diff", "--cached", "--name-only", "-z"]).stdout.split("\0")
        untracked = run_git(repo, ["ls-files", "--others", "--exclude-standard", "-z"]).stdout.split("\0")
        return sorted({p for p in changed + staged + untracked if p})
    return []


def scan_worktree(
    repo: Path,
    files: list[str],
    denylist: list[str],
    allowlist: Allowlist,
    public_handles: set[str],
) -> tuple[list[Finding], list[dict[str, object]], list[str]]:
    findings: list[Finding] = []
    inventory: list[dict[str, object]] = []
    skipped_binary: list[str] = []

    for rel in files:
        if allowlist.matches_path(rel):
            continue
        full = repo / rel
        if full.is_symlink() or not full.is_file():
            continue
        findings.extend(check_filename(rel, "worktree"))
        try:
            raw = full.read_bytes()
        except OSError:
            continue
        if is_binary_bytes(raw[:8192]):
            skipped_binary.append(rel)
            continue
        text = raw.decode("utf-8", errors="replace")
        lines = text.splitlines()
        inventory.append({"path": rel, "lines": len(lines), "bytes": len(raw)})
        for idx, line in enumerate(lines, start=1):
            findings.extend(
                scan_text_line(line, f"{rel}:{idx}", rel, "worktree", denylist, allowlist, public_handles)
            )
    return findings, inventory, skipped_binary


def resolve_history_rev_args(repo: Path, mode: str, rev_range: str | None) -> tuple[list[str], str, list[str]]:
    warnings: list[str] = []
    if mode == "full":
        return ["--all"], "all branches/tags (--all)", warnings
    if mode == "diff":
        return [], "none (worktree diff only)", warnings
    if mode == "range":
        if not rev_range:
            raise SystemExit("--range is required when --mode range")
        return [rev_range], rev_range, warnings
    if mode == "unpushed":
        chk = run_git(repo, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"])
        if chk.returncode == 0 and chk.stdout.strip():
            up = chk.stdout.strip()
            return [f"{up}..HEAD"], f"{up}..HEAD", warnings
        warnings.append("No upstream tracking branch; scanning HEAD commit only for history.")
        return ["-n", "1", "HEAD"], "HEAD (no upstream)", warnings
    return [], "none", warnings


def scan_history(
    repo: Path,
    rev_args: list[str],
    denylist: list[str],
    allowlist: Allowlist,
    public_handles: set[str],
) -> tuple[list[Finding], dict[str, object]]:
    findings: list[Finding] = []
    stats: dict[str, object] = {"commits_scanned": 0, "unique_emails": []}
    if not rev_args:
        return findings, stats

    # 1. Commit metadata (author/committer emails) + commit messages
    sep = "\x1f"
    rec = "\x1e"
    fmt = f"%H{sep}%ad{sep}%an{sep}%ae{sep}%cn{sep}%ce{sep}%B{rec}"
    meta_res = run_git(repo, ["log", *rev_args, "--date=short", f"--format={fmt}"])
    seen_meta_emails: dict[str, list[str]] = defaultdict(list)
    commit_count = 0
    for entry in meta_res.stdout.split(rec):
        entry = entry.strip("\n")
        if not entry:
            continue
        parts = entry.split(sep, 6)
        if len(parts) < 7:
            continue
        commit_count += 1
        sha, date_s, an, ae, cn, ce, body = parts
        short = sha[:8]
        for role, email in (("author", ae.strip()), ("committer", ce.strip())):
            if email and not is_safe_email(email) and not allowlist.matches_value(email):
                seen_meta_emails[f"{role}:{email}"].append(short)

        for line_no, mline in enumerate(body.splitlines(), start=1):
            if not mline.strip():
                continue
            findings.extend(
                scan_text_line(
                    mline,
                    f"commit:{short} (msg:{line_no}, {date_s})",
                    "",
                    "history",
                    denylist,
                    allowlist,
                    public_handles,
                    commit=short,
                )
            )
    stats["commits_scanned"] = commit_count
    stats["unique_emails"] = sorted({k.split(":", 1)[1] for k in seen_meta_emails})
    for key, shas in sorted(seen_meta_emails.items()):
        role, email = key.split(":", 1)
        sample = ", ".join(shas[:3]) + (f" (+{len(shas) - 3} more)" if len(shas) > 3 else "")
        findings.append(
            Finding(
                "High",
                f"Git {role} email",
                "metadata",
                f"{len(shas)} commits ({sample})",
                mask_value(email),
                "Non-noreply email in Git commit metadata",
                shas[0],
            )
        )

    # 2. Historical file paths (including deleted files)
    paths_res = run_git(repo, ["log", *rev_args, "--name-status", "--format=__COMMIT__ %H"])
    current_sha = ""
    seen_hist_files: set[tuple[str, str]] = set()
    for line in paths_res.stdout.splitlines():
        if line.startswith("__COMMIT__ "):
            current_sha = line.split()[1][:8]
            continue
        if "\t" not in line:
            continue
        cols = line.split("\t")
        for p in cols[1:]:
            if not p or allowlist.matches_path(p):
                continue
            key = (p, current_sha)
            if key in seen_hist_files:
                continue
            seen_hist_files.add(key)
            for f in check_filename(p, "history", commit=current_sha):
                # Avoid duplicating same sensitive path across every commit; keep first (newest) occurrence.
                if not any(
                    ex.scope == "history" and ex.category == f.category and ex.location == f.location for ex in findings
                ):
                    findings.append(f)

    # 3. Streaming diff scan across all commits in scope (added lines only)
    cmd = ["git", "-C", str(repo), "log", *rev_args, "-p", "-U0", "--no-color", "--format=__AUDIT_COMMIT__ %H %ad", "--date=short"]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace")
    assert proc.stdout is not None
    cur_sha = ""
    cur_date = ""
    cur_file = ""
    for line in proc.stdout:
        line = line.rstrip("\r\n")
        if line.startswith("__AUDIT_COMMIT__ "):
            parts = line.split()
            cur_sha = parts[1][:8] if len(parts) > 1 else ""
            cur_date = parts[2] if len(parts) > 2 else ""
            cur_file = ""
            continue
        if line.startswith("+++ b/"):
            cur_file = line[6:]
            continue
        if line.startswith("+++ "):
            cur_file = ""
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        content = line[1:]
        if not content.strip():
            continue
        loc = f"commit:{cur_sha} {cur_file} ({cur_date})" if cur_file else f"commit:{cur_sha} ({cur_date})"
        findings.extend(
            scan_text_line(content, loc, cur_file, "history", denylist, allowlist, public_handles, commit=cur_sha)
        )
    proc.wait()

    # 4. Branch and tag names against denylist
    if denylist:
        refs = run_git(repo, ["for-each-ref", "--format=%(refname:short)"]).stdout.splitlines()
        for ref in refs:
            ref_low = ref.lower()
            for term in denylist:
                if term.lower() in ref_low and not allowlist.matches_value(term, ref):
                    findings.append(
                        Finding("High", "Denylist in ref name", "ref", ref, mask_value(term), "Branch or tag matches denylist")
                    )

    return findings, stats


def scan_staged(
    repo: Path,
    denylist: list[str],
    denylist_exists: bool,
    denylist_path: Path,
    allowlist: Allowlist,
    public_handles: set[str],
    visibility: str,
) -> tuple[list[Finding], list[str]]:
    """Fast pre-commit gate for staged changes.

    Blocks on Critical findings (secrets, private keys, credential URLs,
    sensitive filenames) in all repos, and on denylist matches when repository
    visibility is PUBLIC or UNKNOWN.
    """
    check_denylist = visibility in ("PUBLIC", "UNKNOWN")
    active_denylist = denylist if check_denylist else []
    warnings: list[str] = []
    if check_denylist and not denylist_exists:
        warnings.append(f"WARN: repository visibility={visibility}, denylist not found: {denylist_path}")

    findings: list[Finding] = []

    # 1. Check staged filenames (Added / Copied / Modified / Renamed)
    names = run_git(repo, ["diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"]).stdout.split("\0")
    for rel in names:
        if not rel or allowlist.matches_path(rel):
            continue
        for f in check_filename(rel, "staged"):
            if f.severity == "Critical":
                findings.append(f)

    # 2. Check staged added lines with accurate line numbers
    diff_res = run_git(repo, ["diff", "--cached", "--src-prefix=a/", "--dst-prefix=b/", "-U0", "--no-color"])
    cur_file = ""
    cur_line = 0
    for line in diff_res.stdout.splitlines():
        if line.startswith("+++ b/"):
            cur_file = line[6:]
            cur_line = 0
            continue
        if line.startswith("+++ "):
            cur_file = ""
            cur_line = 0
            continue
        if line.startswith("@@ "):
            m = HUNK_RE.match(line)
            if m:
                cur_line = int(m.group(1))
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        content = line[1:]
        loc = f"{cur_file}:{cur_line}" if cur_file and cur_line else (cur_file or "<staged>")
        if cur_line:
            cur_line += 1
        if not content.strip():
            continue
        for f in scan_text_line(content, loc, cur_file, "staged", active_denylist, allowlist, public_handles):
            if f.severity == "Critical" or f.category == "Denylist match":
                findings.append(f)

    return findings, warnings


def deduplicate_and_summarize(findings: list[Finding]) -> tuple[list[Finding], dict[str, int]]:
    seen: set[tuple[str, str, str, str, str]] = set()
    unique: list[Finding] = []
    for f in findings:
        key = (f.severity, f.category, f.scope, f.location, f.masked_value)
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)
    unique.sort(key=lambda x: (SEVERITY_ORDER.get(x.severity, 9), x.scope, x.location, x.category))
    counts = Counter(f.severity for f in unique)
    return unique, dict(counts)


def render_markdown(
    repo: Path,
    visibility: str,
    name_with_owner: str,
    mode: str,
    history_desc: str,
    denylist_path: Path,
    denylist_exists: bool,
    denylist_count: int,
    allowlist_path: Path,
    warnings: list[str],
    findings: list[Finding],
    counts: dict[str, int],
    history_stats: dict[str, object],
    inventory: list[dict[str, object]],
    skipped_binary: list[str],
    max_per_bucket: int,
) -> str:
    out: list[str] = []
    out.append("# Mechanical Scan Report")
    out.append("")
    out.append(f"- **Repository**: `{name_with_owner or repo.name}` (`{repo}`)")
    out.append(f"- **Visibility**: `{visibility}`")
    out.append(f"- **Mode**: `{mode}` (history: `{history_desc}`, commits scanned: `{history_stats.get('commits_scanned', 0)}`)")
    out.append(
        f"- **Denylist**: `{denylist_path}` "
        + (f"(loaded: {denylist_count} terms)" if denylist_exists else "(NOT FOUND — custom term check skipped)")
    )
    out.append(f"- **Allowlist**: `{allowlist_path}` ({'loaded' if allowlist_path.is_file() else 'not configured'})")
    out.append(
        f"- **Findings**: Critical={counts.get('Critical', 0)}, High={counts.get('High', 0)}, "
        f"Medium={counts.get('Medium', 0)}, Low={counts.get('Low', 0)}"
    )

    if warnings:
        out.append("")
        out.append("## Warnings")
        for w in warnings:
            out.append(f"- {w}")

    if not findings:
        out.append("")
        out.append("## Findings")
        out.append("No mechanical findings detected.")
    else:
        for sev in ("Critical", "High", "Medium", "Low"):
            bucket = [f for f in findings if f.severity == sev]
            if not bucket:
                continue
            out.append("")
            out.append(f"## {sev} ({len(bucket)})")
            # Group noisy Low findings (e.g., public handle paths) by category + scope
            if sev == "Low":
                grouped: dict[tuple[str, str], list[Finding]] = defaultdict(list)
                for f in bucket:
                    grouped[(f.category, f.scope)].append(f)
                for (cat, sc), items in grouped.items():
                    out.append(f"- **{cat}** [{sc}] — {len(items)} occurrence(s)")
                    for it in items[:max_per_bucket]:
                        out.append(f"  - `{it.location}` — `{it.masked_value}` ({it.detail})")
                    if len(items) > max_per_bucket:
                        out.append(f"  - ... and {len(items) - max_per_bucket} more")
            else:
                # Deduplicate identical category+masked_value across many history commits if noisy
                for f in bucket[:max_per_bucket * 3]:
                    out.append(f"- **[{f.scope}] {f.category}** | `{f.location}` | `{f.masked_value}` | {f.detail}")
                if len(bucket) > max_per_bucket * 3:
                    out.append(f"- ... and {len(bucket) - max_per_bucket * 3} more {sev} findings (use `--format json` for full list)")

    out.append("")
    out.append(f"## Worktree Text Inventory ({len(inventory)} files, {len(skipped_binary)} binary skipped)")
    for item in inventory:
        out.append(f"- `{item['path']}` ({item['lines']} lines)")
    if skipped_binary:
        out.append("")
        out.append("### Skipped Binary Files")
        for p in skipped_binary[:30]:
            out.append(f"- `{p}`")
        if len(skipped_binary) > 30:
            out.append(f"- ... and {len(skipped_binary) - 30} more")

    return "\n".join(out) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit a public Git repository for secrets, PII, and work info.")
    parser.add_argument("--repo", default=".", help="Path inside target Git repository (default: .)")
    parser.add_argument(
        "--mode",
        choices=("full", "unpushed", "diff", "range", "staged"),
        default="full",
        help="Audit scope (staged exits 1 on Critical or PUBLIC/UNKNOWN denylist match)",
    )
    parser.add_argument("--range", dest="rev_range", default=None, help="Git revision range when --mode range")
    parser.add_argument("--denylist", default=str(DEFAULT_DENYLIST), help="Path to denylist file")
    parser.add_argument("--allowlist", default=str(DEFAULT_ALLOWLIST), help="Path to optional allowlist file")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown", help="Output format")
    parser.add_argument("--max-per-bucket", type=int, default=15, help="Max items shown per section in markdown")
    args = parser.parse_args(argv)

    top = run_git(Path(args.repo), ["rev-parse", "--show-toplevel"])
    if top.returncode != 0:
        print(f"ERROR: not a git repository: {args.repo}", file=sys.stderr)
        return 2
    repo = Path(top.stdout.strip())

    denylist_path = Path(args.denylist).expanduser()
    allowlist_path = Path(args.allowlist).expanduser()
    denylist, denylist_exists = load_denylist(denylist_path)
    allowlist = Allowlist.load(allowlist_path)
    public_handles = extract_public_handles(repo)
    visibility, name_with_owner = get_visibility(repo)

    if args.mode == "staged":
        raw_findings, staged_warnings = scan_staged(
            repo, denylist, denylist_exists, denylist_path, allowlist, public_handles, visibility
        )
        findings, counts = deduplicate_and_summarize(raw_findings)
        for w in staged_warnings:
            print(w, file=sys.stderr)
        if args.format == "json":
            payload = {
                "repo": str(repo),
                "name_with_owner": name_with_owner,
                "visibility": visibility,
                "mode": "staged",
                "denylist_exists": denylist_exists,
                "warnings": staged_warnings,
                "counts": counts,
                "findings": [asdict(f) for f in findings],
            }
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            if findings:
                for f in findings:
                    print(f"[{f.severity}] {f.category} | {f.location} | {f.masked_value} | {f.detail}")
                print(
                    f"ERROR: {len(findings)} blocking finding(s) detected in staged diff (visibility={visibility})",
                    file=sys.stderr,
                )
            else:
                print(f"OK: staged diff clean (visibility={visibility})")
        return 1 if findings else 0

    warnings: list[str] = []
    if not denylist_exists:
        warnings.append(
            f"Denylist not found at {denylist_path}. Create it (one term per line: real name, employer, internal domains/projects) for stronger personal/work info checks."
        )

    rev_args, history_desc, rev_warnings = resolve_history_rev_args(repo, args.mode, args.rev_range)
    warnings.extend(rev_warnings)

    worktree_files = list_worktree_files(repo, args.mode)
    wt_findings, inventory, skipped_binary = scan_worktree(repo, worktree_files, denylist, allowlist, public_handles)
    hist_findings, hist_stats = scan_history(repo, rev_args, denylist, allowlist, public_handles)

    findings, counts = deduplicate_and_summarize(wt_findings + hist_findings)

    if args.format == "json":
        payload = {
            "repo": str(repo),
            "name_with_owner": name_with_owner,
            "visibility": visibility,
            "mode": args.mode,
            "history_scope": history_desc,
            "denylist_exists": denylist_exists,
            "denylist_terms": len(denylist),
            "warnings": warnings,
            "counts": counts,
            "history_stats": hist_stats,
            "findings": [asdict(f) for f in findings],
            "inventory": inventory,
            "skipped_binary": skipped_binary,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        print(
            render_markdown(
                repo=repo,
                visibility=visibility,
                name_with_owner=name_with_owner,
                mode=args.mode,
                history_desc=history_desc,
                denylist_path=denylist_path,
                denylist_exists=denylist_exists,
                denylist_count=len(denylist),
                allowlist_path=allowlist_path,
                warnings=warnings,
                findings=findings,
                counts=counts,
                history_stats=hist_stats,
                inventory=inventory,
                skipped_binary=skipped_binary,
                max_per_bucket=args.max_per_bucket,
            )
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
