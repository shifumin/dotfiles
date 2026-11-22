#!/usr/bin/env python3
"""Tests for scripts/inbox.py.

Run with: python3 -B .claude/skills/cleanup-inbox-mail/tests/test_inbox.py
"""
from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import inbox  # noqa: E402


def completed(returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["gws"], returncode, stdout, stderr)


def run_cli(*argv: str) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = inbox.main(list(argv))
    return code, out.getvalue(), err.getvalue()


class TestInbox(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.state = Path(tmp.name) / "last.json"
        patcher = mock.patch.object(inbox, "STATE", self.state)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_fetch_formats_tables_escapes_cells_and_saves_state(self) -> None:
        def fake_run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
            query = cmd[cmd.index("--query") + 1]
            if query == "in:spam":
                return completed(
                    0,
                    json.dumps(
                        {
                            "messages": [
                                {
                                    "id": "s1",
                                    "from": '"Spam | Co" <spam@example.com>',
                                    "subject": "Win\r\nBig | Now",
                                    "date": "Fri, 20 Nov 2026 01:00:00 +0000",
                                },
                                {
                                    "id": "s2",
                                    "from": "<raw@example.com>",
                                    "subject": None,
                                    "date": "Fri, 20 Nov 2026 03:00:00 +0000",
                                },
                            ]
                        }
                    ),
                )
            return completed(0, "No messages found for query")

        with mock.patch.object(inbox.subprocess, "run", side_effect=fake_run):
            code, out, err = run_cli("fetch", "spam", "promotions")

        self.assertEqual(code, 0, err)
        self.assertIn("## 削除対象（迷惑メール 2件）", out)
        # s2 (12:00 JST) sorted before s1 (10:00 JST)
        self.assertLess(out.index("s2"), out.index("s1"))
        self.assertIn("| 1 | raw@example.com | (件名なし) | 2026-11-20 12:00 | [開く](https://mail.google.com/mail/u/0/#trash/s2) |", out)
        self.assertIn("| 2 | Spam \\| Co | Win Big \\| Now | 2026-11-20 10:00 | [開く](https://mail.google.com/mail/u/0/#trash/s1) |", out)
        self.assertIn("### プロモーション（0件）\n\n対象のメールはありません", out)
        self.assertTrue(out.strip().endswith("COUNTS spam=2 promotions=0"))
        self.assertEqual(json.loads(self.state.read_text()), {"spam": ["s2", "s1"], "promotions": []})

    def test_fetch_warns_when_hitting_max_fetch_limit(self) -> None:
        msgs = [
            {"id": f"m{i}", "from": "a@example.com", "subject": f"S{i}", "date": "Fri, 20 Nov 2026 01:00:00 +0000"}
            for i in range(inbox.MAX_FETCH)
        ]
        with mock.patch.object(inbox.subprocess, "run", return_value=completed(0, json.dumps({"messages": msgs}))):
            code, out, _ = run_cli("fetch", "purchases")

        self.assertEqual(code, 0)
        self.assertIn("取得上限（100件）に達しているため", out)
        self.assertIn("#all/m0", out)

    def test_fetch_auth_error_exits_1_cleanly(self) -> None:
        err_json = json.dumps({"error": {"code": 401, "message": "Failed to get token"}})
        with mock.patch.object(inbox.subprocess, "run", return_value=completed(2, err_json)):
            code, _, err = run_cli("fetch", "spam")

        self.assertEqual(code, 1)
        self.assertIn("gws error (in:spam)", err)
        self.assertFalse(self.state.exists())

    def test_fetch_timeout_exits_1_cleanly(self) -> None:
        with mock.patch.object(inbox.subprocess, "run", side_effect=subprocess.TimeoutExpired("gws", 60)):
            code, _, err = run_cli("fetch", "spam")

        self.assertEqual(code, 1)
        self.assertIn("gws timeout", err)

    def test_apply_normal_and_skips_requery_for_empty_categories(self) -> None:
        self.state.write_text(json.dumps({"spam": ["s1"], "purchases": ["p1", "p2"], "social": []}))
        triage_queries: list[str] = []

        def fake_run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
            if "+triage" in cmd:
                q = cmd[cmd.index("--query") + 1]
                triage_queries.append(q)
                if q == "in:spam":
                    return completed(0, "No messages found")
                # One brand-new message arrived during apply
                return completed(0, json.dumps({"messages": [{"id": "p_new", "date": ""}]}))
            # Write call returning a message body containing the literal word "error" must not false-positive
            return completed(0, json.dumps({"id": "s1", "snippet": 'fixing "error" in logs'}))

        with mock.patch.object(inbox.subprocess, "run", side_effect=fake_run):
            code, out, err = run_cli("apply")

        self.assertEqual(code, 0, err)
        self.assertEqual(sorted(triage_queries), ["category:purchases is:unread", "in:spam"])
        self.assertIn("- **迷惑メール削除**: 1件 ✅", out)
        self.assertIn("- **購入アーカイブ**: 2件 ✅（処理中に新着 1件、未処理）", out)
        self.assertIn("- **ソーシャル**: 対象なし", out)
        self.assertNotIn("## gwsエラー", out)
        self.assertFalse(self.state.exists())

    def test_apply_partial_failure_returns_exit_1_and_cleans_state(self) -> None:
        self.state.write_text(json.dumps({"spam": ["s1", "s2"]}))

        def fake_run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess[str]:
            if "+triage" in cmd:
                return completed(0, json.dumps({"messages": [{"id": "s2", "date": ""}]}))
            if "s2" in " ".join(cmd):
                return completed(1, "", "permission denied")
            return completed(0, "{}")

        with mock.patch.object(inbox.subprocess, "run", side_effect=fake_run):
            code, out, _ = run_cli("apply")

        self.assertEqual(code, 1)
        self.assertIn("1件 ✅ / 失敗 1件 ❌ (s2)", out)
        self.assertIn("## gwsエラー", out)
        self.assertIn("permission denied", out)
        self.assertFalse(self.state.exists())

    def test_apply_dry_run_preserves_state_and_does_not_call_gws(self) -> None:
        self.state.write_text(json.dumps({"spam": ["s1"], "social": ["c1"]}))
        with mock.patch.object(inbox.subprocess, "run") as mock_run:
            code, out, _ = run_cli("apply", "--dry-run")

        self.assertEqual(code, 0)
        mock_run.assert_not_called()
        self.assertIn("DRY trash", out)
        self.assertIn("DRY batchModify", out)
        self.assertTrue(self.state.exists())

    def test_apply_missing_state_returns_exit_1(self) -> None:
        code, _, err = run_cli("apply")
        self.assertEqual(code, 1)
        self.assertIn("state file not found", err)

    def test_apply_empty_state_does_not_crash(self) -> None:
        self.state.write_text("{}")
        with mock.patch.object(inbox.subprocess, "run") as mock_run:
            code, out, err = run_cli("apply")

        self.assertEqual(code, 0, err)
        mock_run.assert_not_called()
        self.assertIn("## クリーンアップ完了", out)
        self.assertFalse(self.state.exists())


if __name__ == "__main__":
    unittest.main()
