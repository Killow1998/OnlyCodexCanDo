from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import json
import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


sys.dont_write_bytecode = True

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))


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
    def test_audit_event_writes_jsonl(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            original_state_dir = HOOK_MODULE.STATE_DIR
            original_audit_log_path = HOOK_MODULE.AUDIT_LOG_PATH
            try:
                HOOK_MODULE.STATE_DIR = Path(tmpdir)
                HOOK_MODULE.AUDIT_LOG_PATH = Path(tmpdir) / "taskwatch-hook-audit.log"
                HOOK_MODULE.audit_event("send_attempt", session_id="session-1", transcript_path=Path("session.jsonl"))
                records = HOOK_MODULE.AUDIT_LOG_PATH.read_text(encoding="utf-8").splitlines()
            finally:
                HOOK_MODULE.STATE_DIR = original_state_dir
                HOOK_MODULE.AUDIT_LOG_PATH = original_audit_log_path

        self.assertEqual(1, len(records))
        payload = json.loads(records[0])
        self.assertEqual("send_attempt", payload["action"])
        self.assertEqual("session-1", payload["session_id"])
        self.assertEqual("session.jsonl", payload["transcript_path"])
        self.assertIn("timestamp", payload)

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

    def test_detect_terminal_goal_uses_latest_nonterminal_state(self) -> None:
        transcript = """{"timestamp":"2026-07-14T10:00:00Z","type":"event_msg","payload":{"type":"thread_goal_updated","goal":{"status":"blocked"}}}
{"timestamp":"2026-07-14T10:01:00Z","type":"event_msg","payload":{"type":"thread_goal_updated","goal":{"status":"active"}}}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "session.jsonl"
            path.write_text(transcript, encoding="utf-8")
            event = HOOK_MODULE.detect_terminal_event(path)
        self.assertIsNone(event)

    def test_detect_terminal_goal_from_update_goal_output(self) -> None:
        transcript = """{"timestamp":"2026-06-11T10:37:03.708Z","type":"response_item","payload":{"type":"function_call_output","call_id":"call_1","output":"{\\"goal\\":{\\"threadId\\":\\"thread-1\\",\\"objective\\":\\"进行全面的code review\\",\\"status\\":\\"complete\\",\\"tokensUsed\\":164757,\\"timeUsedSeconds\\":488,\\"createdAt\\":1781173735,\\"updatedAt\\":1781174223},\\"remainingTokens\\":null}"}}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "session.jsonl"
            path.write_text(transcript, encoding="utf-8")
            event = HOOK_MODULE.detect_terminal_event(path)
        assert event is not None
        self.assertEqual("complete", event["status"])
        self.assertEqual("进行全面的code review", event["objective"])
        self.assertEqual(1781174223, event["updated_at"])
        self.assertEqual("update_goal", event["source"])

    def test_build_body_prefers_goal_time_used_seconds(self) -> None:
        transcript = """{"timestamp":"2026-06-11T07:42:05.794Z","type":"session_meta","payload":{"id":"thread-1"}}
{"timestamp":"2026-06-11T10:37:03.708Z","type":"response_item","payload":{"type":"function_call_output","call_id":"call_1","output":"{\\"goal\\":{\\"threadId\\":\\"thread-1\\",\\"objective\\":\\"进行全面的code review\\",\\"status\\":\\"complete\\",\\"tokensUsed\\":164757,\\"timeUsedSeconds\\":488,\\"createdAt\\":1781173735,\\"updatedAt\\":1781174223},\\"remainingTokens\\":null}"}}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "session.jsonl"
            path.write_text(transcript, encoding="utf-8")
            event = HOOK_MODULE.detect_terminal_event(path)
            assert event is not None
            body = HOOK_MODULE.build_body({"session_id": "thread-1", "cwd": "/repo"}, path, event)
        self.assertIn("- 耗时：8分钟8秒", body)
        self.assertNotIn("花了多久：2小时", body)

    def test_usage_limit_fallback(self) -> None:
        transcript = """{"type":"message","payload":{"text":"normal line"}}\n"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "session.jsonl"
            path.write_text(transcript, encoding="utf-8")
            event = HOOK_MODULE.detect_terminal_event(path, "You've hit your usage limit")
        assert event is not None
        self.assertEqual("usageLimited", event["status"])
        self.assertEqual("usage-limit-fallback", event["source"])

    def test_find_transcript_session_id_matching_is_exact(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            sessions = Path(tmpdir) / "sessions"
            sessions.mkdir()
            wrong = sessions / "rollout-session-10.jsonl"
            exact = sessions / "unrelated-name.jsonl"
            wrong.write_text(
                json.dumps({"type": "session_meta", "payload": {"id": "session-10"}}) + "\n",
                encoding="utf-8",
            )
            exact.write_text(
                json.dumps({"type": "session_meta", "payload": {"id": "session-1"}}) + "\n",
                encoding="utf-8",
            )
            with mock.patch.object(HOOK_MODULE, "CODEX_HOME", Path(tmpdir)):
                resolved = HOOK_MODULE.find_transcript_path({"session_id": "session-1"})
        self.assertEqual(exact, resolved)

    def test_detect_terminal_event_ignores_stale_goal_state_when_now_is_given(self) -> None:
        transcript = """{"timestamp":"2026-06-22T03:00:00Z","type":"event_msg","payload":{"type":"thread_goal_updated","turnId":"old","goal":{"objective":"old goal","status":"complete","updatedAt":"2026-06-22T03:00:00Z"}}}
{"timestamp":"2026-06-22T04:00:00Z","type":"response_item","payload":{"type":"message","role":"user","content":[{"type":"input_text","text":"ordinary follow-up"}]}}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "session.jsonl"
            path.write_text(transcript, encoding="utf-8")
            event = HOOK_MODULE.detect_terminal_event(path, now=datetime(2026, 6, 22, 4, 0, tzinfo=timezone.utc))

        self.assertIsNone(event)

    def test_build_body_is_result_focused(self) -> None:
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
                    "last_assistant_message": "- 完成了 TaskWatch 邮件验证。\n- python -B skills/taskwatch/scripts/check.py: PASS\n```json\n{\"cmd\":\"ignore me\"}\n```",
                },
                path,
                event,
            )
            subject = HOOK_MODULE.build_subject(event, HOOK_MODULE.collect_transcript_context(path, event))
        self.assertIn("一眼结论", body)
        self.assertIn("- 任务：验证 TaskWatch 邮件并归档当天工作", body)
        self.assertIn("- 归档：已完成", body)
        self.assertIn("- 耗时：1小时", body)
        self.assertIn("本次产出", body)
        self.assertIn("Codex 最后结论", body)
        self.assertIn("- 完成了 TaskWatch 邮件验证。", body)
        self.assertIn("- python -B skills/taskwatch/scripts/check.py: PASS", body)
        self.assertIn("- 结论：goal 已完成。", body)
        self.assertIn("- 主要结果：已完成「验证 TaskWatch 邮件并归档当天工作」，Codex 正常收尾。", body)
        self.assertIn("- 归档状态：已完成", body)
        self.assertIn("- 归档说明：已写入飞书工作记录（05-2026 工作记录）。", body)
        self.assertIn("- 后续处理：无需人工介入", body)
        self.assertNotIn("ignore me", body)
        self.assertIn("已写入飞书工作记录（05-2026 工作记录）。", body)
        self.assertNotIn("启动的目的", body)
        self.assertNotIn("目标原文", body)
        self.assertEqual("[TW:DONE][1小时] 验证 TaskWatch 邮件并归档当天工作", subject)

    def test_archive_noise_does_not_surface_raw_command(self) -> None:
        transcript = """{"timestamp":"2026-05-25T10:30:00Z","type":"response_item","payload":{"type":"function_call_output","call_id":"call_1","output":"{\\"cmd\\":\\"rg -n \\\\\\"need_user_authorization\\\\\\" /tmp/demo\\",\\"workdir\\":\\"/tmp\\",\\"yield_time_ms\\":1000,\\"max_output_tokens\\":600}"}}
{"timestamp":"2026-05-25T11:00:00Z","type":"event_msg","payload":{"type":"thread_goal_updated","turnId":"turn-complete","goal":{"objective":"验证 TaskWatch 邮件并归档当天工作","status":"complete","updatedAt":"2026-05-25T11:00:00Z"}}}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "session.jsonl"
            path.write_text(transcript, encoding="utf-8")
            event = HOOK_MODULE.detect_terminal_event(path)
            assert event is not None
            context = HOOK_MODULE.collect_transcript_context(path, event)
        self.assertEqual("未检测到", context["archive_status"])
        self.assertEqual("", context["archive_detail"])

    def test_git_context_missing_does_not_fail_body(self) -> None:
        transcript = """{"timestamp":"2026-05-25T11:00:00Z","type":"event_msg","payload":{"type":"thread_goal_updated","turnId":"turn-complete","goal":{"objective":"no git repo","status":"complete","updatedAt":"2026-05-25T11:00:00Z"}}}
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "session.jsonl"
            path.write_text(transcript, encoding="utf-8")
            event = HOOK_MODULE.detect_terminal_event(path)
            assert event is not None
            with mock.patch.dict(os.environ, {"GIT_CEILING_DIRECTORIES": str(Path(tmpdir).parent)}):
                body = HOOK_MODULE.build_body({"session_id": "session-1", "cwd": tmpdir}, path, event)

        self.assertIn("- 代码变更：未检测到 git 仓库", body)

    def test_state_file_for_session_sanitizes_windows_invalid_chars(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            session_id = r"C:\Users\me\.codex\sessions\2026-06-11:goal/session"
            state_file = HOOK_MODULE.state_file_for_session(Path(tmpdir), session_id)
            HOOK_MODULE.store_sent_key(Path(tmpdir), session_id, "sent-key")
            self.assertEqual("sent-key", HOOK_MODULE.load_sent_key(Path(tmpdir), session_id))
            if os.name != "nt":
                self.assertEqual(0o700, Path(tmpdir).stat().st_mode & 0o777)
                self.assertEqual(0o600, HOOK_MODULE.state_file_for_session(Path(tmpdir), session_id).stat().st_mode & 0o777)
        self.assertNotIn(":", state_file.name)
        self.assertNotIn("\\", state_file.name)
        self.assertNotIn("/", state_file.name)

    def test_send_email_uses_short_default_timeout(self) -> None:
        config = {
            "SMTP_HOST": "smtp.example.com",
            "SMTP_PORT": "587",
            "SMTP_SECURITY": "starttls",
            "SMTP_USER": "sender@example.com",
            "SMTP_PASS": "secret",
            "EMAIL_FROM": "sender@example.com",
            "EMAIL_TO": "target@example.com",
        }
        with mock.patch.object(HOOK_MODULE.smtplib, "SMTP") as smtp:
            smtp.return_value.__enter__.return_value = mock.Mock()
            HOOK_MODULE.send_email(config, "subject", "body")

        self.assertEqual(HOOK_MODULE.DEFAULT_SMTP_TIMEOUT_SECONDS, smtp.call_args.kwargs["timeout"])

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

    def test_large_transcript_is_streamed_once_and_reuses_bounded_facts(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "large-session.jsonl"
            noise = json.dumps(
                {
                    "timestamp": "2026-07-14T00:00:00Z",
                    "type": "response_item",
                    "payload": {"type": "message", "role": "user", "content": [{"text": "x" * 200}]},
                }
            )
            with path.open("w", encoding="utf-8") as handle:
                for _ in range(30000):
                    handle.write(noise + "\n")
                handle.write(
                    json.dumps(
                        {
                            "timestamp": "2026-07-14T00:10:00Z",
                            "type": "response_item",
                            "payload": {
                                "type": "message",
                                "role": "assistant",
                                "content": [{"text": "完成大 transcript 回归。\nRan 42 tests in 1.0s OK"}],
                            },
                        }
                    )
                    + "\n"
                )
                handle.write(
                    json.dumps(
                        {
                            "timestamp": "2026-07-14T00:10:01Z",
                            "type": "event_msg",
                            "payload": {
                                "type": "thread_goal_updated",
                                "goal": {"objective": "large transcript", "status": "complete"},
                            },
                        }
                    )
                    + "\n"
                )

            original_loads = HOOK_MODULE.json.loads
            with (
                mock.patch.object(Path, "read_text", side_effect=AssertionError("whole-file read forbidden")),
                mock.patch.object(HOOK_MODULE.json, "loads", wraps=original_loads) as loads,
            ):
                facts = HOOK_MODULE.scan_transcript(path)
                event = HOOK_MODULE.detect_terminal_event(path, facts=facts)
                assert event is not None
                context = HOOK_MODULE.collect_transcript_context(path, event, facts)
                body = HOOK_MODULE.build_body(
                    {"session_id": "large-session", "cwd": tmpdir},
                    path,
                    event,
                    context,
                    facts,
                )
                self.assertEqual(30002, loads.call_count)

        self.assertEqual("complete", event["status"])
        self.assertLessEqual(len(facts.recent_text_chunks), 80)
        self.assertIn("完成大 transcript 回归。", body)
        self.assertIn("unittest: PASS", body)


if __name__ == "__main__":
    unittest.main()
