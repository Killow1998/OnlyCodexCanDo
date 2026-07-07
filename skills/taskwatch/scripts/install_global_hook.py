#!/usr/bin/env python3
"""Install the TaskWatch global Codex Stop hook."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from pathlib import Path

import install


CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))
CONFIG_PATH = CODEX_HOME / "config.toml"
ENV_PATH = CODEX_HOME / "taskwatch.env"
STATE_DIR = CODEX_HOME / "taskwatch-state"
GLOBAL_SKILL_DIR = CODEX_HOME / "skills" / "taskwatch"
HOOK_SCRIPT = GLOBAL_SKILL_DIR / "scripts" / "taskwatch_stop_hook.py"
BLOCK_BEGIN = "# taskwatch hook begin"
BLOCK_END = "# taskwatch hook end"


def build_hook_block() -> str:
    hook_command = f'"{Path(sys.executable).resolve()}" "{HOOK_SCRIPT}"'
    return (
        f"{BLOCK_BEGIN}\n"
        "[[hooks.Stop]]\n\n"
        "[[hooks.Stop.hooks]]\n"
        'type = "command"\n'
        f"command = {json.dumps(hook_command)}\n"
        "timeout = 20\n"
        'statusMessage = "TaskWatch checking goal status"\n'
        f"{BLOCK_END}\n"
    )


def ensure_feature_hooks_enabled(text: str) -> str:
    lines = text.splitlines()
    section_start = None
    for index, line in enumerate(lines):
        if line.strip() == "[features]":
            section_start = index
            break

    if section_start is None:
        suffix = "" if not text or text.endswith("\n") else "\n"
        return text + suffix + "[features]\n" + "hooks = true\n"

    section_end = len(lines)
    for index in range(section_start + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section_end = index
            break

    hook_line = re.compile(r"^\s*hooks\s*=")
    for index in range(section_start + 1, section_end):
        if hook_line.match(lines[index]):
            lines[index] = "hooks = true"
            return "\n".join(lines) + "\n"

    lines.insert(section_end, "hooks = true")
    return "\n".join(lines) + "\n"


def upsert_managed_block(text: str, block: str) -> str:
    pattern = re.compile(rf"{re.escape(BLOCK_BEGIN)}\n.*?{re.escape(BLOCK_END)}\n?", re.DOTALL)
    if pattern.search(text):
        return pattern.sub(lambda _: block, text, count=1)
    suffix = "" if not text or text.endswith("\n") else "\n"
    return text + suffix + block


def remove_managed_block(text: str) -> str:
    pattern = re.compile(rf"{re.escape(BLOCK_BEGIN)}\n.*?{re.escape(BLOCK_END)}\n?", re.DOTALL)
    return pattern.sub("", text, count=1)


def write_email_env(args: argparse.Namespace) -> str:
    if args.sender_email and args.recipient_email and args.sender_password:
        content = install.build_email_env(
            sender_email=args.sender_email,
            recipient_email=args.recipient_email,
            sender_password=args.sender_password,
            smtp_host=args.smtp_host,
            smtp_port=args.smtp_port,
            smtp_security=args.smtp_security,
        )
        ENV_PATH.parent.mkdir(parents=True, exist_ok=True)
        ENV_PATH.write_text(content, encoding="utf-8")
        return "written"
    if ENV_PATH.exists():
        return "reused"
    raise SystemExit(
        "taskwatch email config missing. Provide --sender-email, --recipient-email, "
        "and --sender-password."
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sender-email", help="SMTP sender address.")
    parser.add_argument("--recipient-email", help="Notification recipient address.")
    parser.add_argument("--sender-password", default=os.environ.get("TASKWATCH_SENDER_PASSWORD"), help="SMTP authorization code or app password. Defaults to $TASKWATCH_SENDER_PASSWORD to keep the secret out of shell history.")
    parser.add_argument("--smtp-host", help="Override SMTP host.")
    parser.add_argument("--smtp-port", type=int, help="Override SMTP port.")
    parser.add_argument(
        "--smtp-security",
        choices=("ssl", "starttls", "plain"),
        help="Override SMTP security mode.",
    )
    parser.add_argument(
        "--global-skill-dir",
        default=str(GLOBAL_SKILL_DIR),
        help="Installed global skill directory that contains scripts/taskwatch_stop_hook.py.",
    )
    parser.add_argument(
        "--hook-only",
        action="store_true",
        help="Install or refresh the Stop hook without writing SMTP settings.",
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove the managed Stop hook block from ~/.codex/config.toml. Keeps taskwatch.env and state unless --purge.",
    )
    parser.add_argument(
        "--purge",
        action="store_true",
        help="With --remove, also delete taskwatch.env and the taskwatch-state directory.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without writing files.")
    return parser.parse_args()


def remove_hook(args: argparse.Namespace) -> int:
    config_changed = False
    if CONFIG_PATH.exists():
        config_text = CONFIG_PATH.read_text(encoding="utf-8")
        updated = remove_managed_block(config_text)
        config_changed = updated != config_text
        if config_changed and not args.dry_run:
            CONFIG_PATH.write_text(updated, encoding="utf-8")

    mode = "dry-run" if args.dry_run else "removed"
    print(f"[summary] mode: {mode}")
    if config_changed:
        print(f"[summary] config file: {CONFIG_PATH} (managed stop hook block removed)")
    else:
        print(f"[summary] config file: {CONFIG_PATH} (no managed stop hook block found)")
    print("[summary] the [features] hooks flag was left unchanged; other hooks may still use it")

    if args.purge:
        for target in (ENV_PATH, STATE_DIR):
            if not target.exists():
                continue
            if args.dry_run:
                print(f"[summary] would delete {target}")
            elif target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
                print(f"[summary] deleted {target}")
            else:
                target.unlink()
                print(f"[summary] deleted {target}")
    else:
        kept = [str(path) for path in (ENV_PATH, STATE_DIR) if path.exists()]
        if kept:
            print("[summary] kept (use --purge to delete): " + ", ".join(kept))
    return 0


def main() -> int:
    args = parse_args()
    if args.remove:
        return remove_hook(args)
    global_skill_dir = Path(args.global_skill_dir).expanduser().resolve()
    hook_script = global_skill_dir / "scripts" / "taskwatch_stop_hook.py"

    if not global_skill_dir.exists():
        raise SystemExit(f"global taskwatch skill missing: {global_skill_dir}")
    if not hook_script.exists():
        raise SystemExit(f"global hook script missing: {hook_script}")

    env_action = "reused"
    env_preview = None
    if args.sender_email and args.recipient_email and args.sender_password:
        env_preview = install.build_email_env(
            sender_email=args.sender_email,
            recipient_email=args.recipient_email,
            sender_password=args.sender_password,
            smtp_host=args.smtp_host,
            smtp_port=args.smtp_port,
            smtp_security=args.smtp_security,
        )
        env_action = "written"
    elif not ENV_PATH.exists() and not args.hook_only:
        raise SystemExit(
            "taskwatch email config missing. Provide --sender-email, --recipient-email, "
            "and --sender-password."
        )

    config_text = CONFIG_PATH.read_text(encoding="utf-8") if CONFIG_PATH.exists() else ""
    managed_block = build_hook_block().replace(str(HOOK_SCRIPT), str(hook_script))
    updated_config = upsert_managed_block(ensure_feature_hooks_enabled(config_text), managed_block)

    if args.dry_run:
        print("[summary] mode: dry-run")
        print(f"[summary] env file: {ENV_PATH} ({env_action})")
        print(f"[summary] config file: {CONFIG_PATH} (managed stop hook)")
        print(f"[summary] hook script: {hook_script}")
        if env_preview is not None:
            print("[summary] smtp config: inferred from sender")
        return 0

    if args.hook_only and not (args.sender_email and args.recipient_email and args.sender_password):
        env_action = "skipped"
    else:
        env_action = write_email_env(args)
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(updated_config, encoding="utf-8")
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    print("[summary] taskwatch global hook installed")
    print(f"[summary] env file: {ENV_PATH} ({env_action})")
    print(f"[summary] config file: {CONFIG_PATH}")
    print(f"[summary] hook script: {hook_script}")
    print(f"[summary] state dir: {STATE_DIR}")
    print("[summary] terminal goal mail: complete, blocked, usageLimited")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
