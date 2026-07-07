from __future__ import annotations

import importlib.util
import os
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path


sys.dont_write_bytecode = True

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "install.py"
SPEC = importlib.util.spec_from_file_location("keep_an_eye_install", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class InstallScriptTests(unittest.TestCase):
    def make_config(self, workspace: str = "/tmp/workspace") -> "MODULE.InstallConfig":
        return MODULE.InstallConfig(
            workspace=Path(workspace),
            label="Demo RL",
            systemd_basename="demo-rl-codex-monitor",
            job_service="demo-job.service",
            primary_log="outputs/training.log",
            progress_log="outputs/hourly_monitor.log",
            artifact_dirs=("logs", "outputs"),
            process_grep="train.py|python -m demopkg|codex exec",
            codex_model="gpt-5.4-mini",
            run_command="python3 -B scripts/train.py --profile foo",
            goal_mode=False,
        )

    def test_build_file_map_contains_expected_files(self) -> None:
        config = self.make_config()
        file_map = MODULE.build_file_map(config)
        self.assertIn(".codex_monitor/monitor.env", file_map)
        self.assertIn(".codex_monitor/run_command.sh", file_map)
        self.assertIn(".codex_monitor/scripts/hourly_check.sh", file_map)
        self.assertIn(".codex_monitor/scripts/send_mail.py", file_map)
        self.assertIn("run_with_monitor.sh", file_map)
        self.assertIn("run_train_with_monitor.sh", file_map)
        self.assertIn("CODEX_MONITOR_LABEL='Demo RL'", file_map[".codex_monitor/monitor.env"])
        self.assertIn("CODEX_MONITOR_WORKSPACE=", file_map[".codex_monitor/monitor.env"])
        self.assertIn("CODEX_MONITOR_GOAL_MODE=0", file_map[".codex_monitor/monitor.env"])
        self.assertIn("exec bash -lc 'python3 -B scripts/train.py --profile foo'", file_map[".codex_monitor/run_command.sh"])
        self.assertIn("任务概况", file_map[".codex_monitor/scripts/send_mail.py"])
        self.assertIn("结果摘要", file_map[".codex_monitor/scripts/send_mail.py"])
        self.assertIn("- 结论：", file_map[".codex_monitor/scripts/send_mail.py"])
        self.assertIn("parse_update_goal_output", file_map[".codex_monitor/scripts/send_mail.py"])
        self.assertIn("goal_time_used_seconds", file_map[".codex_monitor/scripts/send_mail.py"])
        self.assertIn('return f"goal:{task_name}"', file_map[".codex_monitor/scripts/send_mail.py"])

    def test_file_map_keys_match_managed_files(self) -> None:
        file_map = MODULE.build_file_map(self.make_config())
        self.assertEqual(set(MODULE.MANAGED_FILES), set(file_map))

    def test_generated_scripts_resolve_workspace_from_monitor_env(self) -> None:
        file_map = MODULE.build_file_map(self.make_config())
        for relative in (
            ".codex_monitor/run_command.sh",
            ".codex_monitor/scripts/hourly_check.sh",
            ".codex_monitor/scripts/install_systemd_timer.sh",
            "run_with_monitor.sh",
        ):
            self.assertIn("CODEX_MONITOR_WORKSPACE", file_map[relative], relative)

    def test_central_install_scaffolds_under_codex_home(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir) / "workspace"
            codex_home = Path(tmpdir) / "codex-home"
            workspace.mkdir()
            argv = [
                "install.py",
                str(workspace),
                "--central",
                "--systemd-basename",
                "demo-rl-codex-monitor",
                "--primary-log",
                "logs/run.log",
            ]
            env = {
                "CODEX_HOME": str(codex_home),
                "TASKWATCH_ALLOW_WINDOWS_WORKSPACE_SCAFFOLD": "1",
            }
            with mock.patch.dict(os.environ, env):
                with mock.patch.object(sys, "argv", argv):
                    self.assertEqual(0, MODULE.main())
            scaffold = codex_home / "taskwatch" / "jobs" / "demo-rl-codex-monitor"
            self.assertTrue((scaffold / "run_with_monitor.sh").exists())
            self.assertTrue((scaffold / ".codex_monitor" / "monitor.env").exists())
            monitor_env = (scaffold / ".codex_monitor" / "monitor.env").read_text(encoding="utf-8")
            self.assertIn("CODEX_MONITOR_WORKSPACE=", monitor_env)
            self.assertIn(workspace.name, monitor_env)
            self.assertEqual([], [p for p in workspace.iterdir()])

    def test_uninstall_removes_managed_files_and_keeps_runtime(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir) / "workspace"
            workspace.mkdir()
            install_argv = ["install.py", str(workspace), "--primary-log", "logs/run.log"]
            env = {"TASKWATCH_ALLOW_WINDOWS_WORKSPACE_SCAFFOLD": "1"}
            with mock.patch.dict(os.environ, env):
                with mock.patch.object(sys, "argv", install_argv):
                    self.assertEqual(0, MODULE.main())
                monitor_dir = workspace / ".codex_monitor"
                (monitor_dir / "email.env").write_text("SMTP_HOST=smtp.example.com\n", encoding="utf-8")
                (monitor_dir / "reports" / "hourly_report_1.md").write_text("# report\n", encoding="utf-8")
                with mock.patch.object(sys, "argv", ["install.py", str(workspace), "--uninstall"]):
                    self.assertEqual(0, MODULE.main())
            self.assertFalse((workspace / "run_with_monitor.sh").exists())
            self.assertFalse((monitor_dir / "monitor.env").exists())
            self.assertTrue((monitor_dir / "email.env").exists())
            self.assertTrue((monitor_dir / "reports" / "hourly_report_1.md").exists())

    def test_uninstall_purge_removes_monitor_dir(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir) / "workspace"
            workspace.mkdir()
            env = {"TASKWATCH_ALLOW_WINDOWS_WORKSPACE_SCAFFOLD": "1"}
            with mock.patch.dict(os.environ, env):
                with mock.patch.object(sys, "argv", ["install.py", str(workspace), "--primary-log", "logs/run.log"]):
                    self.assertEqual(0, MODULE.main())
                (workspace / ".codex_monitor" / "email.env").write_text("SMTP_HOST=smtp.example.com\n", encoding="utf-8")
                with mock.patch.object(sys, "argv", ["install.py", str(workspace), "--uninstall", "--purge"]):
                    self.assertEqual(0, MODULE.main())
            self.assertFalse((workspace / ".codex_monitor").exists())
            self.assertFalse((workspace / "run_with_monitor.sh").exists())

    def test_infer_smtp_for_qq_mail(self) -> None:
        host, port, security = MODULE.infer_smtp("123456@qq.com")
        self.assertEqual(("smtp.qq.com", 587, "starttls"), (host, port, security))

    def test_build_email_env_uses_inferred_values(self) -> None:
        content = MODULE.build_email_env(
            sender_email="user@gmail.com",
            recipient_email="target@example.com",
            sender_password="app-pass",
            smtp_host=None,
            smtp_port=None,
            smtp_security=None,
        )
        self.assertIn("SMTP_HOST=smtp.gmail.com", content)
        self.assertIn("SMTP_PORT=587", content)
        self.assertIn("SMTP_SECURITY=starttls", content)
        self.assertIn("EMAIL_TO=target@example.com", content)

    def test_sender_password_falls_back_to_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            argv = [
                "install.py",
                tmpdir,
                "--primary-log",
                "logs/run.log",
                "--sender-email",
                "user@qq.com",
                "--recipient-email",
                "target@example.com",
                "--dry-run",
            ]
            env = {
                "TASKWATCH_SENDER_PASSWORD": "env-secret",
                "TASKWATCH_ALLOW_WINDOWS_WORKSPACE_SCAFFOLD": "1",
            }
            with mock.patch.dict(os.environ, env):
                with mock.patch.object(sys, "argv", argv):
                    with mock.patch.object(MODULE, "build_email_env", wraps=MODULE.build_email_env) as build_env:
                        self.assertEqual(0, MODULE.main())
        self.assertEqual("env-secret", build_env.call_args.kwargs["sender_password"])

    def test_sender_password_flag_wins_over_env(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            argv = [
                "install.py",
                tmpdir,
                "--primary-log",
                "logs/run.log",
                "--sender-email",
                "user@qq.com",
                "--recipient-email",
                "target@example.com",
                "--sender-password",
                "flag-secret",
                "--dry-run",
            ]
            env = {
                "TASKWATCH_SENDER_PASSWORD": "env-secret",
                "TASKWATCH_ALLOW_WINDOWS_WORKSPACE_SCAFFOLD": "1",
            }
            with mock.patch.dict(os.environ, env):
                with mock.patch.object(sys, "argv", argv):
                    with mock.patch.object(MODULE, "build_email_env", wraps=MODULE.build_email_env) as build_env:
                        self.assertEqual(0, MODULE.main())
        self.assertEqual("flag-secret", build_env.call_args.kwargs["sender_password"])

    def test_main_refuses_workspace_local_install_on_windows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            with mock.patch.object(MODULE.os, "name", "nt"):
                with mock.patch.dict(os.environ, {}, clear=True):
                    with mock.patch.object(sys, "argv", ["install.py", tmpdir]):
                        with self.assertRaises(SystemExit) as raised:
                            MODULE.main()
        self.assertIn("workspace-local monitor is Linux only", str(raised.exception))


HOOK_SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "install_global_hook.py"
sys.path.insert(0, str(HOOK_SCRIPT_PATH.parent))
HOOK_SPEC = importlib.util.spec_from_file_location("taskwatch_install_global_hook", HOOK_SCRIPT_PATH)
HOOK_MODULE = importlib.util.module_from_spec(HOOK_SPEC)
assert HOOK_SPEC and HOOK_SPEC.loader
sys.modules[HOOK_SPEC.name] = HOOK_MODULE
HOOK_SPEC.loader.exec_module(HOOK_MODULE)


class GlobalHookScriptTests(unittest.TestCase):
    def test_remove_managed_block_strips_hook_and_is_idempotent(self) -> None:
        block = HOOK_MODULE.build_hook_block()
        text = "[features]\nhooks = true\n" + block + "[other]\nkey = 1\n"
        cleaned = HOOK_MODULE.remove_managed_block(text)
        self.assertNotIn("taskwatch hook begin", cleaned)
        self.assertIn("[features]", cleaned)
        self.assertIn("[other]", cleaned)
        self.assertEqual(cleaned, HOOK_MODULE.remove_managed_block(cleaned))

    def test_remove_managed_block_leaves_untouched_config(self) -> None:
        text = "[features]\nhooks = true\n"
        self.assertEqual(text, HOOK_MODULE.remove_managed_block(text))


if __name__ == "__main__":
    unittest.main()
