#!/usr/bin/env python3
"""Install the lark-worklog-archive skill into the local Codex skills directory."""

from __future__ import annotations

import argparse
import os
import shutil
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
    check("npm", "npm")
    check("lark-cli", "lark-cli", "npx @larksuite/cli@latest install")
    copy_skill(source, target, args.dry_run)
    print(f"[ok] skill target: {target}")
    print("Restart Codex so the newly installed or updated skill is loaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
