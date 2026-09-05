#!/usr/bin/env python3
"""Agent Mail delivery and private TaskWatch configuration."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile
from datetime import datetime, timezone


REQUIRED_KEYS = ('EMAIL_TO', 'AGENT_MAIL_CLI', 'AGENT_MAIL_WORKSPACE')


def validate(config: dict[str, str]) -> None:
    missing = [key for key in REQUIRED_KEYS if not config.get(key)]
    if missing:
        raise ValueError('missing Agent Mail config keys: ' + ', '.join(missing))
    for key in REQUIRED_KEYS:
        if any(char in config[key] for char in '\r\n\x00'):
            raise ValueError(f'{key} must be one line')
    recipient = config['EMAIL_TO']
    if recipient.count('@') != 1 or any(char.isspace() for char in recipient) or ',' in recipient:
        raise ValueError('EMAIL_TO must contain one recipient address')
    if not Path(config['AGENT_MAIL_CLI']).is_absolute():
        raise ValueError('AGENT_MAIL_CLI must be an absolute executable path')


def send(config: dict[str, str], subject: str, body: str) -> dict:
    validate(config)
    cli = Path(config['AGENT_MAIL_CLI'])
    env = os.environ.copy()
    env['AGENTLY_WORKSPACE'] = config['AGENT_MAIL_WORKSPACE']
    # npm's launcher needs its sibling node even in a noninteractive service.
    env['PATH'] = str(cli.parent) + os.pathsep + env.get('PATH', '')
    with tempfile.TemporaryDirectory(prefix='taskwatch-mail-') as directory:
        body_path = Path(directory) / 'body.txt'
        body_path.write_text(body, encoding='utf-8')
        body_path.chmod(0o600)
        result = subprocess.run(
            [str(cli), 'message', '+send', '--to', config['EMAIL_TO'],
             '--subject', subject, '--body-file', './body.txt',
             '--body-format', 'plain', '--confirmed'],
            cwd=directory, env=env, capture_output=True, text=True,
            encoding='utf-8', timeout=float(config.get('AGENT_MAIL_TIMEOUT_SECONDS', '12')),
            check=False,
        )
    # Do not log arbitrary CLI output: errors can include private content.
    if result.returncode:
        raise RuntimeError(f'Agent Mail CLI failed (exit {result.returncode}); inspect its private diagnostics')
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError('Agent Mail returned an uncertain response; verify sent mail before retrying') from exc
    data = response.get('data', {}) if isinstance(response, dict) else {}
    queued = isinstance(response, dict) and (response.get('queued') is True or isinstance(data, dict) and data.get('queued') is True)
    if not queued or response.get('ok') is False or isinstance(data, dict) and data.get('confirmation_required'):
        raise RuntimeError('Agent Mail did not confirm acceptance; verify delivery before retrying')
    return response


def send_once(config: dict[str, str], subject: str, body: str, receipt: Path) -> bool:
    """Claim before delivery; an uncertain attempt requires review, never blind retry."""
    validate(config)
    receipt.parent.mkdir(parents=True, exist_ok=True)
    try:
        with receipt.open('x', encoding='utf-8') as handle:
            receipt.chmod(0o600)
            json.dump({'status': 'pending', 'at': datetime.now(timezone.utc).isoformat()}, handle)
    except FileExistsError:
        return False
    send(config, subject, body)
    receipt.write_text(json.dumps({'status': 'accepted', 'at': datetime.now(timezone.utc).isoformat()}), encoding='utf-8')
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True, help='Private TaskWatch env file to create.')
    parser.add_argument('--recipient', required=True)
    parser.add_argument('--cli', required=True, help='Absolute agently-cli executable path.')
    parser.add_argument('--workspace', required=True, help='Existing AGENTLY_WORKSPACE identity.')
    parser.add_argument('--force', action='store_true', help='Replace an explicitly selected existing mail configuration.')
    args = parser.parse_args()
    config = {'MAIL_TRANSPORT': 'agent-mail', 'EMAIL_TO': args.recipient,
              'AGENT_MAIL_CLI': args.cli, 'AGENT_MAIL_WORKSPACE': args.workspace,
              'MAIL_CONTENT': 'brief'}
    validate(config)
    args.config.parent.mkdir(parents=True, exist_ok=True)
    # Exclusive creation protects an existing SMTP configuration by default.
    with args.config.open('w' if args.force else 'x', encoding='utf-8') as handle:
        os.chmod(args.config, 0o600)
        handle.write(''.join(f'{key}={value}\n' for key, value in config.items()))
    print('Agent Mail configuration saved; credentials remain in the existing CLI identity.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
