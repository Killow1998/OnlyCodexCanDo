from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_codex_home.py"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "codex-home"
SPEC = importlib.util.spec_from_file_location("audit_codex_home", SCRIPT)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class AuditCodexHomeTests(unittest.TestCase):
    def test_scan_aggregates_without_reading_contents(self) -> None:
        result = AUDIT.scan_codex_home(FIXTURE, max_entries=100)
        expected_bytes = sum(path.stat().st_size for path in FIXTURE.rglob("*") if path.is_file())
        database_bytes = (FIXTURE / "logs" / "state.sqlite").stat().st_size
        worktree_bytes = (FIXTURE / "worktrees" / "demo" / "file.txt").stat().st_size

        self.assertEqual(result["files"], 3)
        self.assertEqual(result["directories"], 4)
        self.assertEqual(result["bytes"], expected_bytes)
        self.assertEqual(result["database_like"], {"files": 1, "bytes": database_bytes})
        self.assertEqual(result["worktree_roots"], 1)
        self.assertFalse(result["truncated"])
        self.assertEqual(result["categories"]["sessions"]["files"], 1)
        self.assertEqual(result["categories"]["worktrees"]["bytes"], worktree_bytes)

    def test_identifier_like_top_level_name_is_redacted(self) -> None:
        name = "a" * 32
        self.assertEqual(AUDIT.safe_bucket(name, False), "<other-files>")
        self.assertEqual(AUDIT.safe_bucket(name, True), "<other-directories>")

    def test_entry_cap_marks_scan_truncated(self) -> None:
        result = AUDIT.scan_codex_home(FIXTURE, max_entries=2)

        self.assertTrue(result["truncated"])
        self.assertEqual(result["entries_scanned"], 2)


if __name__ == "__main__":
    unittest.main()
