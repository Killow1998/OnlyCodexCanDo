from __future__ import annotations

import importlib.util
import json
import unittest
from datetime import datetime, timezone
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_codex_home.py"
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "codex-home"
SESSION_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "session-overhead"
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
        self.assertEqual(result["unique_bytes"], expected_bytes)
        self.assertEqual(result["hardlink_duplicates"], 0)
        self.assertEqual(result["database_like"], {"files": 1, "bytes": database_bytes})
        self.assertEqual(result["worktree_roots"], 1)
        self.assertFalse(result["truncated"])
        self.assertEqual(result["errors"], 0)
        self.assertTrue(all(count == 0 for count in result["error_kinds"].values()))
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

    def test_hardlinks_do_not_double_count_unique_storage(self) -> None:
        totals = AUDIT.new_file_totals()
        seen = set()
        AUDIT.add_file(totals, size=6, allocated=4096, identity=(1, 7), seen=seen)
        AUDIT.add_file(totals, size=6, allocated=4096, identity=(1, 7), seen=seen)
        AUDIT.finalize_totals(totals)

        self.assertEqual(totals["files"], 2)
        self.assertEqual(totals["bytes"], 12)
        self.assertEqual(totals["unique_bytes"], 6)
        self.assertEqual(totals["allocated_bytes"], 4096)
        self.assertEqual(totals["hardlink_duplicates"], 1)

    def test_since_reports_recent_growth_by_category(self) -> None:
        past = AUDIT.scan_codex_home(FIXTURE, since=datetime(1970, 1, 1, tzinfo=timezone.utc))
        future = AUDIT.scan_codex_home(FIXTURE, since=datetime(2100, 1, 1, tzinfo=timezone.utc))

        self.assertEqual(past["since"]["files"], past["files"])
        self.assertEqual(past["since"]["bytes"], past["bytes"])
        self.assertIn("sessions", past["since"]["categories"])
        self.assertEqual(future["since"]["files"], 0)
        self.assertEqual(future["since"]["categories"], {})

    def test_session_overhead_reports_aggregates_without_private_content(self) -> None:
        result = AUDIT.scan_codex_home(SESSION_FIXTURE, session_overhead=True, session_top=1)

        overhead = result["session_overhead"]
        self.assertEqual(overhead["sampled_files"], 1)
        self.assertEqual(overhead["records"], 4)
        self.assertEqual(overhead["tool_output_records"], 1)
        self.assertEqual(overhead["compaction_records"], 1)
        self.assertEqual(overhead["image_records"], 1)
        self.assertEqual(overhead["largest_files"][0]["rank"], 1)
        serialized_overhead = json.dumps(overhead)
        self.assertNotIn("fixture-session-id", serialized_overhead)
        self.assertNotIn("fixture-output", serialized_overhead)
        self.assertNotIn("fixture-summary", serialized_overhead)
        self.assertNotIn("fixture-image", serialized_overhead)


if __name__ == "__main__":
    unittest.main()
