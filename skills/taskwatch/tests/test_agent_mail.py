from __future__ import annotations

import importlib.util
import json
import io
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import agent_mail
import run_with_alert
import taskwatch_stop_hook


class AgentMailTests(unittest.TestCase):
    def config(self):
        return {'MAIL_TRANSPORT': 'agent-mail', 'EMAIL_TO': 'recipient@example.com',
                'AGENT_MAIL_CLI': str(Path('/tools/agently-cli').resolve()), 'AGENT_MAIL_WORKSPACE': 'test'}

    def test_file_body_plain_text_identity_and_background_path(self):
        config = self.config()
        def run(command, **kwargs):
            self.assertNotIn('private body', command)
            self.assertIn('--confirmed', command)
            self.assertEqual(kwargs['env']['AGENTLY_WORKSPACE'], 'test')
            self.assertTrue(kwargs['env']['PATH'].startswith(str(Path(config['AGENT_MAIL_CLI']).parent)))
            self.assertEqual((Path(kwargs['cwd']) / 'body.txt').read_text(encoding='utf-8'), 'private body')
            return subprocess.CompletedProcess(command, 0, '{"ok":true,"data":{"queued":true}}', '')
        with patch.object(agent_mail.subprocess, 'run', side_effect=run):
            agent_mail.send(config, 'test subject', 'private body')

    def test_cli_failure_or_unconfirmed_output_is_not_success(self):
        for code, output in [(1, '{"queued":true}'), (0, '{"ok":false}'), (0, '{"ok":true}'), (0, '{"ok":true,"data":{"confirmation_required":true}}'), (0, 'invalid')]:
            with self.subTest(code=code, output=output), patch.object(agent_mail.subprocess, 'run', return_value=subprocess.CompletedProcess([], code, output, 'secret')):
                with self.assertRaises(RuntimeError) as caught:
                    agent_mail.send(self.config(), 'subject', 'body')
                self.assertNotIn('secret', str(caught.exception))

    def test_duplicate_and_uncertain_sends_are_not_repeated(self):
        for error in [None, subprocess.TimeoutExpired('cli', 12)]:
            with tempfile.TemporaryDirectory() as directory, patch.object(agent_mail, 'send', side_effect=error) as send:
                receipt = Path(directory) / 'delivery.json'
                if error:
                    with self.assertRaises(subprocess.TimeoutExpired):
                        agent_mail.send_once(self.config(), 's', 'b', receipt)
                else:
                    self.assertTrue(agent_mail.send_once(self.config(), 's', 'b', receipt))
                self.assertFalse(agent_mail.send_once(self.config(), 's', 'b', receipt))
                self.assertEqual(send.call_count, 1)
                self.assertEqual(json.loads(receipt.read_text())['status'], 'pending' if error else 'accepted')

    def test_configuration_requires_no_smtp_secret_and_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'mail.env'
            argv = ['agent_mail.py', '--config', str(target), '--recipient', 'recipient@example.com', '--cli', self.config()['AGENT_MAIL_CLI'], '--workspace', 'test']
            with patch.object(sys, 'argv', argv):
                self.assertEqual(agent_mail.main(), 0)
                with self.assertRaises(FileExistsError):
                    agent_mail.main()
            self.assertEqual(taskwatch_stop_hook.load_email_config(target)['MAIL_TRANSPORT'], 'agent-mail')
            self.assertNotIn('SMTP_PASS', target.read_text())

    def test_run_preserves_failure_even_when_mail_is_unavailable(self):
        with tempfile.TemporaryDirectory() as directory:
            argv = ['run_with_alert.py', '--label', 'fixture', '--state-dir', directory, '--', sys.executable, '-c', 'raise SystemExit(7)']
            with patch.object(sys, 'argv', argv), patch.object(run_with_alert, 'load_config', return_value=self.config()), patch.object(agent_mail, 'send_once', side_effect=RuntimeError('offline')):
                self.assertEqual(run_with_alert.main(), 7)
            record = json.loads(next(Path(directory).glob('*.run.json')).read_text())
            self.assertEqual(record['status'], 'failed')
            self.assertEqual(record['exit_code'], 7)

    def test_generated_mailer_uses_agent_mail(self):
        import install
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / 'send_mail.py'
            target.write_text(install.SEND_MAIL_TEMPLATE, encoding='utf-8')
            spec = importlib.util.spec_from_file_location('generated_mailer', target)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            config = Path(directory) / 'email.env'
            config.write_text(''.join(f'{k}={v}\n' for k, v in self.config().items()), encoding='utf-8')
            self.assertEqual(module._merged_config(config)['MAIL_TRANSPORT'], 'agent-mail')

    def test_hook_refresh_preserves_tables_appended_inside_old_markers(self):
        import install_global_hook
        block = install_global_hook.build_hook_block()
        extra = '[hooks.state."existing"]\ntrusted_hash = "sample"\n\n[plugins."example"]\nenabled = true\n'
        old = block.replace(install_global_hook.BLOCK_END, extra + install_global_hook.BLOCK_END)
        updated = install_global_hook.upsert_managed_block(old, block)
        removed = install_global_hook.remove_managed_block(old)
        self.assertIn(extra.strip(), updated)
        self.assertIn(extra.strip(), removed)
        self.assertEqual(updated.count('[[hooks.Stop]]'), 1)
        self.assertNotIn('[[hooks.Stop]]', removed)

    def test_goal_hook_brief_delivery_is_deduplicated(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            transcript = root / 'fixture.jsonl'
            now = datetime.now(timezone.utc).isoformat()
            transcript.write_text(json.dumps({'timestamp': now, 'type': 'event_msg', 'payload': {'type': 'thread_goal_updated', 'goal': {'status': 'complete', 'objective': 'fixture', 'updatedAt': now}}}) + '\n', encoding='utf-8')
            payload = json.dumps({'session_id': 'fixture', 'cwd': directory, 'transcript_path': str(transcript)})
            config = {**self.config(), 'MAIL_CONTENT': 'brief'}
            with patch.object(taskwatch_stop_hook, 'STATE_DIR', root), patch.object(taskwatch_stop_hook, 'audit_event'), patch.object(taskwatch_stop_hook, 'load_email_config', return_value=config), patch.object(agent_mail, 'send') as send:
                for _ in range(2):
                    with patch.object(sys, 'stdin', io.StringIO(payload)), patch.object(sys, 'stdout', io.StringIO()):
                        self.assertEqual(taskwatch_stop_hook.main(), 0)
                self.assertEqual(send.call_count, 1)
                self.assertIn('complete', send.call_args.args[2])
                self.assertNotIn('Codex 最后结论', send.call_args.args[2])


if __name__ == '__main__':
    unittest.main()
