#!/usr/bin/env python3
"""Install the lark-worklog-archive skill into the local Codex skills directory."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CODEX_HOME = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex"))


def check(name: str, command: str, fix: str | None = None) -> bool:
    found = shutil.which(command)
    if found:
        print(f"[ok] {name}: {found}")
        return True
    print(f"[warn] {name}: not found")
    if fix:
        print(f"  fix: {fix}")
    return False


def lark_cli_command() -> str | None:
    configured = os.environ.get("LARK_CLI")
    if configured:
        return configured
    names = ("lark-cli.cmd", "lark-cli.exe", "lark-cli") if os.name == "nt" else ("lark-cli",)
    for name in names:
        path = shutil.which(name)
        if path:
            return path
    return None


def check_lark_cli() -> bool:
    found = lark_cli_command()
    if found:
        print(f"[ok] lark-cli: {found}")
        return True
    print("[warn] lark-cli: not found")
    print("  fix: npx @larksuite/cli@latest install")
    if os.name == "nt":
        print("  note: use lark-cli.cmd if PowerShell blocks lark-cli.ps1")
    return False


def node_version_tuple(value: str) -> tuple[int, int, int] | None:
    value = value.strip().lstrip("v")
    parts = value.split(".")
    if len(parts) < 2:
        return None
    try:
        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2]) if len(parts) > 2 else 0
    except ValueError:
        return None
    return major, minor, patch


def check_node_version() -> None:
    node = shutil.which("node")
    if not node:
        return
    proc = subprocess.run([node, "--version"], text=True, encoding="utf-8", errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        return
    version = node_version_tuple(proc.stdout)
    if version and version < (20, 12, 0):
        print(f"[warn] node version: {proc.stdout.strip()} may be too old for the latest @larksuite/cli installer")
        print("  fix: upgrade Node.js to 20.12.0 or newer, then rerun npx @larksuite/cli@latest install")


def copy_skill(source: Path, target: Path, dry_run: bool) -> None:
    ignored = shutil.ignore_patterns(
        "__pycache__",
        "*.pyc",
        "monthly-docs.local.json",
        "category-rules.local.json",
    )
    if dry_run:
        print(f"[dry-run] would copy {source} -> {target}")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, dirs_exist_ok=True, ignore=ignored)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--codex-home", default=str(DEFAULT_CODEX_HOME), help="Codex home directory. Defaults to $CODEX_HOME or ~/.codex.")
    parser.add_argument("--skill-dir", default=str(SKILL_DIR), help="Source skill directory.")
    parser.add_argument("--dry-run", action="store_true", help="Print checks without copying files.")
    args = parser.parse_args()

    source = Path(args.skill_dir).resolve()
    target = Path(args.codex_home).expanduser().resolve() / "skills" / source.name
    if not (source / "SKILL.md").exists():
        raise SystemExit(f"Skill source is invalid: {source}")

    print(f"Installing {source.name}")
    check("python", sys.executable)
    check("node", "node")
    check_node_version()
    check("npm", "npm")
    check_lark_cli()
    copy_skill(source, target, args.dry_run)
    print(f"[ok] skill target: {target}")
    print("This installer only copies the skill. It does not create a Feishu/Lark app or monthly worklog.")
    print("Restart Codex so the newly installed or updated skill is loaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
