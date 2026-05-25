from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

SKILL_DIR = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


HOOK_MODULE = load_module("taskwatch_stop_hook", SKILL_DIR / "scripts" / "taskwatch_stop_hook.py")
INSTALL_MODULE = load_module("install", SKILL_DIR / "scripts" / "install.py")
INSTALL_HOOK_MODULE = load_module("install_global_hook", SKILL_DIR / "scripts" / "install_global_hook.py")


class TaskWatchHookTests(unittest.TestCase):
    def test_detect_terminal_goal_event(self) -> None:
        transcript = """{"type":"event_msg","payload":{"type":"thread_goal_updated","goal":{"status":"active"}}}
{"timestamp":"2026-05-25T10:00:00Z","type":"event_msg","payload":{"type":"thread_goal_updated","turnId":"abc","goal":{"objective":"run task","status":"blocked","updatedAt":"2026-05-25T10:00:00Z"}}}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "session.jsonl"
            path.write_text(transcript, encoding="utf-8")
            event = HOOK_MODULE.detect_terminal_event(path)
        assert event is not None
        self.assertEqual("blocked", event["status"])
        self.assertEqual("run task", event["objective"])
        self.assertEqual("thread_goal_updated", event["source"])

    def test_usage_limit_fallback(self) -> None:
        transcript = """{"type":"message","payload":{"text":"normal line"}}\n"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "session.jsonl"
            path.write_text(transcript, encoding="utf-8")
            event = HOOK_MODULE.detect_terminal_event(path, "You've hit your usage limit")
        assert event is not None
        self.assertEqual("usageLimited", event["status"])
        self.assertEqual("usage-limit-fallback", event["source"])

    def test_build_body_includes_task_purpose_archive_and_timing(self) -> None:
        transcript = """{"timestamp":"2026-05-25T10:00:00Z","type":"response_item","payload":{"type":"message","role":"user","content":[{"type":"input_text","text":"请测试 taskwatch，并在结束后归档今天的工作。"}]}}
{"timestamp":"2026-05-25T10:30:00Z","type":"response_item","payload":{"type":"function_call_output","call_id":"call_1","output":"Updated worklog https://example.com/doc for 05-25-2026 with 2 item(s).\\nMonthly document: 05-2026 工作记录\\n"}}
{"timestamp":"2026-05-25T11:00:00Z","type":"event_msg","payload":{"type":"thread_goal_updated","turnId":"turn-complete","goal":{"objective":"验证 TaskWatch 邮件并归档当天工作","status":"complete","updatedAt":"2026-05-25T11:00:00Z"}}}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "session.jsonl"
            path.write_text(transcript, encoding="utf-8")
            event = HOOK_MODULE.detect_terminal_event(path)
            assert event is not None
            body = HOOK_MODULE.build_body(
                {
                    "session_id": "session-1",
                    "cwd": "/home/user",
                    "turn_id": "turn-complete",
                    "last_assistant_message": "已完成归档。",
                },
                path,
                event,
            )
            subject = HOOK_MODULE.build_subject(event, HOOK_MODULE.collect_transcript_context(path, event))
        self.assertIn("任务是什么：验证 TaskWatch 邮件并归档当天工作", body)
        self.assertIn("启动的目的：请测试 taskwatch，并在结束后归档今天的工作。", body)
        self.assertIn("是否完成归档：已完成", body)
        self.assertIn("花了多久：1小时", body)
        self.assertIn("结果摘要", body)
        self.assertIn("TaskWatch Goal 完成通知 | 验证 TaskWatch 邮件并归档当天工作", subject)

    def test_install_global_hook_upserts_block_and_feature(self) -> None:
        original = "[features]\nmemories = true\n"
        updated = INSTALL_HOOK_MODULE.upsert_managed_block(
            INSTALL_HOOK_MODULE.ensure_feature_hooks_enabled(original),
            INSTALL_HOOK_MODULE.build_hook_block(),
        )
        self.assertIn("hooks = true", updated)
        self.assertIn(INSTALL_HOOK_MODULE.BLOCK_BEGIN, updated)
        self.assertIn('statusMessage = "TaskWatch checking goal status"', updated)
        rewritten = INSTALL_HOOK_MODULE.upsert_managed_block(updated, INSTALL_HOOK_MODULE.build_hook_block())
        self.assertEqual(1, rewritten.count(INSTALL_HOOK_MODULE.BLOCK_BEGIN))


if __name__ == "__main__":
    unittest.main()
