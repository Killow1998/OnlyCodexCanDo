#!/usr/bin/env python3
"""Read-only package/link checks; not a behavioral evaluation of the Skill."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    installation = parser.add_mutually_exclusive_group()
    installation.add_argument(
        "--check-global",
        action="store_true",
        help="Compare source with the default global installation.",
    )
    installation.add_argument("--global-skill", help="Compare source with this installed Skill directory.")
    installation.add_argument("--skip-global", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    errors = []
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    if not re.match(r"\A---\r?\nname: organized-proj\r?\ndescription: .+\r?\n---\r?\n", text):
        errors.append("SKILL.md: expected name and nonempty description frontmatter")
    ui = (root / "agents/openai.yaml").read_text(encoding="utf-8")
    if 'display_name: "organizedProj"' not in ui or "$organized-proj" not in ui:
        errors.append("openai.yaml: expected display name and invocation")
    files = [p for p in root.rglob("*") if p.is_file()]
    for path in files:
        if path.suffix == ".pyc" or "__pycache__" in path.parts:
            errors.append(f"unexpected cache: {path.relative_to(root)}")
        if path.suffix != ".md":
            continue
        for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if re.match(r"[a-z]+://|#", target):
                continue
            if not (path.parent / target.split("#", 1)[0]).exists():
                errors.append(f"{path.relative_to(root)}: missing link {target}")
    if args.check_global or args.global_skill:
        installed = (
            Path(args.global_skill).expanduser() if args.global_skill else Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "skills" / root.name
        )
        if installed.exists() and installed.resolve() != root:

            def contents(base):
                return {p.relative_to(base).as_posix(): p.read_bytes() for p in base.rglob("*") if p.is_file()}

            if contents(root) != contents(installed):
                errors.append("installed copy differs; deployment needs separate authorization")
        elif not installed.exists():
            errors.append(f"global skill missing: {installed}; install the authorized copy or omit the installation check")
    for error in errors:
        print(f"[fail] {error}")
    if not errors:
        print("[ok] package, links, and source hygiene; behavioral scenarios not executed")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
