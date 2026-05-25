from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "install.py"
SPEC = importlib.util.spec_from_file_location("keep_an_eye_install", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class InstallScriptTests(unittest.TestCase):
    def test_build_file_map_contains_expected_files(self) -> None:
        config = MODULE.InstallConfig(
            workspace=Path("/tmp/workspace"),
            label="Go2-W RL",
            systemd_basename="go2w-rl-codex-monitor",
            job_service="firerl-go2w.service",
            primary_log="outputs/training.log",
            progress_log="outputs/hourly_monitor.log",
            artifact_dirs=("logs", "outputs"),
            process_grep="train_low_level|python -m firerl|codex exec",
            codex_model="gpt-5.4-mini",
            run_command="python3 -B scripts/train_low_level.py --profile foo",
            goal_mode=False,
        )
        file_map = MODULE.build_file_map(config)
        self.assertIn(".codex_monitor/monitor.env", file_map)
        self.assertIn(".codex_monitor/run_command.sh", file_map)
        self.assertIn(".codex_monitor/scripts/hourly_check.sh", file_map)
        self.assertIn(".codex_monitor/scripts/send_mail.py", file_map)
        self.assertIn("run_with_monitor.sh", file_map)
        self.assertIn("run_train_with_monitor.sh", file_map)
        self.assertIn("CODEX_MONITOR_LABEL='Go2-W RL'", file_map[".codex_monitor/monitor.env"])
        self.assertIn("CODEX_MONITOR_GOAL_MODE=0", file_map[".codex_monitor/monitor.env"])
        self.assertIn("exec bash -lc 'python3 -B scripts/train_low_level.py --profile foo'", file_map[".codex_monitor/run_command.sh"])
        self.assertIn("任务概况", file_map[".codex_monitor/scripts/send_mail.py"])
        self.assertIn("原始最终报告", file_map[".codex_monitor/scripts/send_mail.py"])

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


if __name__ == "__main__":
    unittest.main()
