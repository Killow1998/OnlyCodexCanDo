#!/usr/bin/env python3
"""Run one command and send a brief Agent Mail exit notification, without polling an LLM."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

import agent_mail


def load_config(path: Path) -> dict[str, str]:
    config = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        if line.strip() and not line.lstrip().startswith('#'):
            key, value = line.split('=', 1)
            config[key.strip()] = value.strip()
    agent_mail.validate(config)
    return config


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=Path(os.environ.get('CODEX_HOME', Path.home() / '.codex')) / 'taskwatch.env')
    parser.add_argument('--label', required=True)
    parser.add_argument('--state-dir', type=Path, required=True, help='Private directory for run identity, exit status, and delivery receipts.')
    parser.add_argument('command', nargs=argparse.REMAINDER, help='Command after --; arguments are passed directly without a shell.')
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command:
        parser.error('a command is required after --')
    config = load_config(args.config)
    run_id = uuid.uuid4().hex
    args.state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    state = args.state_dir / (run_id + '.run.json')
    record = {'run_id': run_id, 'label': args.label, 'cwd': str(Path.cwd()), 'status': 'running'}
    state.write_text(json.dumps(record), encoding='utf-8')
    state.chmod(0o600)
    try:
        code = subprocess.call(command)
    except OSError as exc:
        code = 127
        record['error'] = type(exc).__name__
    record.update(status='exited' if code == 0 else 'failed', exit_code=code)
    state.write_text(json.dumps(record), encoding='utf-8')
    body = f"Task: {args.label}\nStatus: {record['status']}\nExit code: {code}\nWorkspace: {Path.cwd()}\nEvidence: {state}\n"
    if code == 0:
        body += 'The process exited successfully; result quality still needs its task acceptance check.\n'
    try:
        agent_mail.send_once(config, f"TaskWatch: {args.label} {record['status']}", body, args.state_dir / (run_id + '.delivery.json'))
    except Exception as exc:
        print(f'TaskWatch delivery needs attention: {type(exc).__name__}; see {args.state_dir}', file=sys.stderr)
    return code if code >= 0 else 128 - code


if __name__ == '__main__':
    raise SystemExit(main())
